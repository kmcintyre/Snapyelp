'''
Created on Oct 12, 2014

@author: kevin

Module for distributing email to connect websocket clients
'''

from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
import json

class TwitterRetrieveClientProtocol(WebSocketClientProtocol):
    
    def onConnect(self, response):
        print "server connect: {0}".format(response.peer)
        self.server = response.peer
    
    def onOpen(self):
        print "open: {0}".format(self.server)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            incoming = json.loads(payload);
            href = 'http://service.snapyelp.com/' + incoming["file_dest"] + '.html'
        else:
            print 'non-binary skipped'        


if __name__ == '__main__':
    from twisted.internet import reactor
    client_factory = WebSocketClientFactory("ws://localhost:8025", debug = False)    
    client_factory.protocol = TwitterRetrieveClientProtocol
    reactor.connectTCP("localhost", 8025, client_factory)
    reactor.run()