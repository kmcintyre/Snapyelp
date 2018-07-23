from twisted.internet import reactor, defer
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from twisted.internet.ssl import ClientContextFactory

from urlparse import urlparse
from lxml import etree
from pymongo import MongoClient
from bson import json_util
import json 

scrape_collection = MongoClient().test.scrape

def clean_url(href, url):
    if href.startswith('http://'):
        res = urlparse(href)
        url_obj = get_url(href)
        if not url_obj:
            a = {'url': href, 'http_code': 421, 'referrer': [url] }
            scrape_collection.insert(a)
        elif url not in url_obj['referrer']:
            scrape_collection.update_one({ '_id': url_obj['_id'] }, { '$push': { 'referrer': url } })
        fix_url = 'https://' + res.netloc + href.split(res.netloc)[1]
        return fix_url    
    if href.startswith('https://'):
        return href
    elif href.startswith('//'):
        res = urlparse(url)
        https_url = 'https://' + res.netloc + url.split(res.netloc)[1]
        return https_url    
    elif href.startswith('/'):
        res = urlparse(url)
        return 'https://' + res.netloc + href
    else:
        return url + href

def add_url(url, referrer = None, additional = None):
    url_obj = get_url(url)
    if not url_obj:        
        a = {}
        if additional and isinstance(additional, dict):
            a.update(additional)
        a['url'] = url
        a['referrer'] = []        
        if referrer and url != referrer:
            a['referrer'].append(referrer)
        scrape_collection.insert(a)
    elif referrer and referrer not in url_obj['referrer']:
        scrape_collection.update_one( { '_id': url_obj['_id'] }, { '$push': { 'referrer': referrer } })            

def get_url(url):
    url_dict = {'url': url}
    cached_url = scrape_collection.find_one(url_dict)
    if cached_url: 
        url_obj = json.loads(json_util.dumps(cached_url))
        url_obj['_id'] = cached_url.get('_id')
        return url_obj 
    return None

main_url = 'https://quickbooks.intuit.com/ca/resources/'
add_url(main_url)

class WebClientContextFactory(ClientContextFactory):
    def getContext(self, hostname, port):
        return ClientContextFactory.getContext(self)

agent = Agent(reactor, WebClientContextFactory())

def post_process(new_urls, from_url):
    for nu in new_urls:
        add_url(nu, from_url)
    
def process_body(body, url):
    try:
        html = etree.HTML(body)        
        hrefs = html.cssselect('[href]')
        scripts = html.cssselect('script[src]')
        images = html.cssselect('img[src]')
        #print 'url:', url, 'hrefs:', len(hrefs), 'scripts:', len(scripts), 'images:', len(images)
        check_urls = [i.attrib['src'] for i in images] + [s.attrib['src'] for s in scripts] + [h.attrib['href'] for h in hrefs]
        for cc in check_urls:
            add_url(clean_url(cc, url), url)
    except Exception as e:
        print 'process body exception:', e

def process_response(response, url):
    d = readBody(response)
    d.addCallback(process_body, url)
    d.addErrback(error_url, url)
    return d        

def append_url(response, url, referrer = None):
    url_obj = get_url(url)
    a = {'http_code': response.code }
    for h in response.headers.getAllRawHeaders():
        a[h[0].lower()] = h[1][0] if len(h[1]) == 1 else h[1]     
    if response.code in [301,302]:
        add_url(clean_url(a['location'], url), referrer)        
        scrape_collection.update_one(
            { '_id': url_obj['_id'] },
            {'$push': { 'referrer': referrer } }
        )
    scrape_collection.update_one(
        { '_id': url_obj['_id'] },
        {'$set': a }
    )
    if 'content-type' in a and a['content-type'].split(';')[0] == 'text/html' and url.startswith(main_url) and response.code == 200:
        return process_response(response, url)
    return defer.succeed(True)

def error_url(err, url):
    print 'error:', err, url
    url_obj = get_url(url)
    scrape_collection.update_one(
        { '_id': url_obj['_id'] },
        {'$set': {'http_code': 504}}
    )    
    
def scrape(url, referrer = None):
    try:
        print 'scrape:', url
        d = agent.request(
        'GET',
        str(url),
        Headers({'User-Agent': ['Twisted Web Client Example']}),
        None)
        d.addCallback(append_url, url, referrer)
        d.addErrback(error_url, url)
        return d
    except Exception as e:
        error_url(e, url)
        return defer.succeed(True)

def url_scrape(url_obj):
    ref = None
    if 'referrer' in url_obj and len(url_obj['referrer']) > 0:
        ref = url_obj['referrer'][0]
    return scrape(url_obj['url'], ref)    

def check_urls():
    cursor = scrape_collection.find({ 'http_code' : { "$exists" : False } }).limit(25)
    if cursor.count() == 0:
        reactor.stop()
    else: 
        dl = defer.DeferredList([url_scrape(c) for c in cursor])
        dl.addCallback(lambda ign: reactor.callLater(0, check_urls))
    
if __name__ == '__main__':
    print 'run' 
    reactor.callWhenRunning(check_urls)       
    reactor.run()