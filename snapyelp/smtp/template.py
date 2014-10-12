'''
Created on Oct 12, 2014

@author: kevin

Module for converting email to html  
'''

import StringIO
from bs4 import BeautifulSoup
from email.header import decode_header
from email.utils import parsedate
import random
import re
import string
import time

from twisted.python.filepath import FilePath
from twisted.web.template import renderer, XMLFile, tags, VALID_HTML_TAG_NAMES

from snapyelp import fixed_twisted
from snapyelp import fixed
    
class EmailElement(fixed_twisted.GenericElement):
    loader = XMLFile(FilePath('etc/templates/email_template.xml'))        

    def __init__(self, helo, origin, user):
        print 'create element', helo, origin, user        
        self.broadcast_dict = fixed.blank_msg()        
        self.broadcast_dict['helo'] = str(helo)        
        self.broadcast_dict['origin'] = str(origin)
        self.broadcast_dict['user'] = str(user)
        self.domain = None
        self.incoming_email = None
        self.summary = None
        self.html = None
        self.attachments = []
    
    def raw_email(self, in_email):
        
        self.incoming_email = in_email
        
        def decode_safely(s, charset='ascii'):
            try:
                return s.decode(charset or 'ascii', 'replace')
            except LookupError:  # bogus charset
                return s.decode('ascii', 'replace')
        def decode_rfc2047_header(h):
            return ''.join(decode_safely(s, charset)
                   for s, charset in decode_header(h))
        def extractemail(h):
            try:
                return re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', h)[0].lower()
            except:
                return h.lower()
                
        self.broadcast_dict['to'] = decode_rfc2047_header(self.incoming_email.get("to"))
        print self.broadcast_dict['to']
        self.broadcast_dict['from'] = decode_rfc2047_header(self.incoming_email.get("from"))
        print self.broadcast_dict['from']
        self.broadcast_dict['subject'] = decode_rfc2047_header(self.incoming_email.get("subject"))
        print self.broadcast_dict['subject']
        if self.broadcast_dict['to'] == 'None':
            print 'no to', self.broadcast_dict['user']
            self.broadcast_dict['to'] = str(self.broadcast_dict['user'])
        if self.broadcast_dict['from'] == 'None':
            print 'no from', self.broadcast_dict['origin'] 
            self.broadcast_dict['from'] = str(self.broadcast_dict['origin'])
        print 'to:', self.broadcast_dict['to'], 'from:', self.broadcast_dict['from']
        self.broadcast_dict['derived_to'] = extractemail(self.broadcast_dict['to'])
        self.broadcast_dict['derived_from'] = extractemail(self.broadcast_dict['from'])                
        print 'derived_to:', self.broadcast_dict['derived_to'], 'derived_from:', self.broadcast_dict['derived_from'], 'subject:', self.broadcast_dict['subject']
        
        def get_date():
            try:
                d = parsedate(self.incoming_email.get("date"));
                if d == 'None':
                    print 'create time'
                    return time.time()                
                return d.time()
            except:
                return time.time()
            
        self.broadcast_dict['date'] = get_date();         
        
        self.broadcast_dict['attachments'] = None
        self.broadcast_dict['multipart'] = False                     
        self.broadcast_dict['msg'] = decode_rfc2047_header(self.incoming_email.get("message-id"))        
        
        ds = time.strftime(fixed.dt_split_format, time.localtime(self.broadcast_dict['date']))
        file_hash = ''.join(random.choice(string.ascii_lowercase) for x in range(6))
        file_format = '%s_%s' % (ds, file_hash)
        print 'file format:', file_format
         
        self.broadcast_dict['file_dest'] = file_format
        

    def get_broadcast_dict(self):
        return self.broadcast_dict
    
    @renderer
    def pagehead(self, request, tag):        
        return tag("derived by amazon.com")

    @renderer
    def subject(self, request, tag):
        return tag(self.broadcast_dict['subject'])

    @renderer
    def date(self, request, tag):
        return tag(str(self.broadcast_dict['date']))    

    @renderer
    def _helo(self, request, tag):        
        return tag(self.broadcast_dict['helo'])

    @renderer
    def _origin(self, request, tag):
        return tag(self.broadcast_dict['origin'])

    @renderer
    def _user(self, request, tag):
        return tag(str(self.broadcast_dict['user']))    

    @renderer
    def derived_to(self, request, tag):
        return tag(self.broadcast_dict['derived_to'])

    @renderer
    def derived_from(self, request, tag):
        return tag(str(self.broadcast_dict['derived_from']))    


    @renderer
    def message(self, request, tag):
        def walkit(p, prev = 0):
            if prev > 20:
                raise Exception('To much walking')
            print 'walkit called', p.get_content_type(), p.get_charsets()
            if p.is_multipart():
                print 'is multipart'
                self.broadcast_dict['multipart'] = True
                for part in p.walk():                    
                    if "multipart" not in part.get_content_type():
                        print 'subwalk'
                        prev += 1
                        yield walkit(part, prev)
                    else:
                        pass
                        # print "multipart:", part.get_payload();
            else:
                content_type = p.get_content_type()
                charset = ''
                filename = '' 
                if p.get_charsets() is not None:
                    charset = p.get_charsets()[0]
                if charset is None:
                    charset = ''
                io = StringIO.StringIO(p.get_payload(decode=True))
                print 'content_type:', content_type, ' charset:', charset
                if content_type == "text/html":
                    try:
                        bs = BeautifulSoup(io)
                        for tl in bs.findAll(True):
                            if tl.name not in VALID_HTML_TAG_NAMES:
                                tl.extract()                            
                        [s.extract() for s in bs('script')]                            
                        [s.extract() for s in bs('noscript')]
                        [s.extract() for s in bs('style')]
                        [s.extract() for s in bs('meta')]
                        [s.extract() for s in bs('title')]                    
                        self.html = bs.prettify(encoding='utf-8')
                                                                            
                        body = tags.span(fixed._placeholder)
                        print 'set html element'
                    except Exception as e:                        
                        print 'html failure:', e
                elif content_type == "text/plain":    
                    try:                
                        body = tags.pre(io.getvalue())
                    except Exception as e:
                        print 'text failure:', e
                else:
                    print 'attachment:', content_type                    
                    try:
                        print 'content-disposition:', p['content-disposition']
                        filename = re.findall("filename=(\S+)", p['content-disposition'])[0].replace('\"', '')
                        print 'filename:', filename
                        try:
                            filename = p.get_param('filename', None, 'content-disposition')                                             
                        except Exception as e2:
                            print 'fuck me1:', e2
                            filename = re.search(fixed.email_filename, filename).group(2)                            
                    except Exception as e:
                        print 'fuck me2:', e
                        filename = 'unknown'
                    
                    print 'filename:', filename                         
                    self.broadcast_dict['attachments'] = True                                        
                    self.attachments.append((filename, io.getvalue(), content_type))                    
                    body = fixed.sizeof_fmt(io.len)  
                
                def filename_link(f):
                    if len(f) > 0:
                        t = tags.a(f)
                        t.attributes['href'] = 'http://www.Base.com/' + self.broadcast_dict['file_dest'] + "_" + f 
                        return t
                    else:
                        return f
                print 'got here'                        
                yield tag.clone().fillSlots(
                        body=body,
                        content_type=content_type,
                        charset=charset,
                        filename=filename_link(filename)
                        )        
        yield walkit(self.incoming_email)

    @renderer
    def headers(self, request, tag):
        for key in self.incoming_email.keys():
            print 'key:', key, ' value:', self.incoming_email[key]
            yield tag.clone().fillSlots(key=key, value=self.incoming_email[key])
