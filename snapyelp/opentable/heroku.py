'''
Created on Oct 12, 2014

@author: kevin

Explority module to opentable herokuapp 
'''

from twisted.internet import reactor, defer
from twisted.web.client import Agent

import urllib
import json

from snapyelp import fixed_twisted

agent_browser = Agent(reactor)

url = 'http://opentable.herokuapp.com/api'

def printit(body):
    print len(body)
    print body

def api(endpoint='stats'):
    d = agent_browser.request("GET", uri = url + '/' + endpoint)
    d.addCallback(fixed_twisted.get_body)
    return d

def city_loop(cities):
    print 'cities:', len(cities)
    try:
        city = cities.pop()
        ep = 'restaurants?' + urllib.urlencode({'city':city})
        print ep
        d = api(ep)
        d.addCallback(printit)
        d.addCallback(lambda ign: city_loop(cities))
        return d    
    except Exception as e:
        print e
        return defer.SUCCESS

def get_cities():        
    d = api('cities')
    d.addCallback(json.loads)
    return d

if __name__ == '__main__':
    d = get_cities()
    d.addCallback(printit)
    reactor.run()


    