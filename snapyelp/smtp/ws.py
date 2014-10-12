'''
Created on Oct 12, 2014

@author: kevin

Websocket module for serving incoming email to connect clients
'''

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
import json
from twisted.internet import reactor

from snapyelp.smtp.processor import Postman

class BaseWSProtocol(WebSocketServerProtocol):
    
    def onOpen(self):
        print 'onOpen'
        self.factory.register_client(self)
        self.filter = None
        self.heartbeat = None
        self.status = None
    
    def cheap_filter(self, msg):
        if self.filter is None:
            return False
        print 'filter:'
        for k, v in self.filter.iteritems():
            print 'check:', k, ' in ', v, ' value: ', msg[k]
            try:
                if msg[k] in v or v in msg[k]:
                    return False
            except Exception as e:
                print 'filter check error:', e
        return True

    def onMessage(self, msg, binary):
        print 'onMessage:', msg        
        try:
            incoming = json.loads(msg)
        except Exception as e:
            print 'json exception:', e
            return 
        
        if 'filter' in incoming:
            print 'add filter:', incoming['filter']
            self.filter = incoming['filter']                
            
        if 'heartbeat' in incoming:
            print 'heartbeat:', incoming['heartbeat']
            self.heartbeat = incoming['heartbeat']
            if self.heartbeat:
                reactor.callLater(0, self.factory.heartbeat, self)
                        
        if 'last' in incoming:
            print 'last: call resend'
            reactor.callLater(0, self.factory.resend, self, incoming['last'])

    def connectionLost(self, reason):
        print 'connectionLost'
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

class BaseWSServerFactory(WebSocketServerFactory):
    protocol = BaseWSProtocol

    def __init__(self, url, debug=False, debugCodePaths=False):
        WebSocketServerFactory.__init__(self, url, debug=debug, debugCodePaths=debugCodePaths)
        self._clients = []
        # reactor.callLater(BaseWSServerFactory.heartbeat_delay, self.heartbeat)

    def register_client(self, client):
        if not client in self._clients:
            print "register client:", client.peer
            self._clients.append(client)
                
    def unregister(self, client): 
        print "unregistered:", client.peer       
        if client in self._clients:
            self._clients.remove(client)
        else:
            print 'nobody to remove!'
                    
    def email_broadcast(self, email_dict):
        print 'factory email_broadcast to:', len(self._clients)
        msg_string = json.dumps(email_dict)        
        for c in self._clients:
            if not c.cheap_filter(email_dict):
                print "message sent to:", c.peer
                c.sendMessage(msg_string)
            else:
                print "filtered message to:", c.peer
    
    def resend(self, client, count=1):
        print 'factory resend'
        raise 'factory resend', (client, count)

    def heartbeat(self, client=None):
        if client is None:
            print 'send heartbeat to all:', len(self._clients)
            for c in self._clients:
                if c.heartbeat:
                    c.sendMessage(json.dumps(self.status()))
        else:
            print 'reply heartbeat'
            client.sendMessage(json.dumps(self.status()))
    
                        
        # if self.servers is None: 
        # else:
        #    print 'call postman'
        #    self.postman.status(client)

    """    
    def connectionMade(self, addr):
        for c in self.clients:
            c.sendMessage(json.dumps({ "host": str(addr.host), "action" : "connected"}))
    """
class PostmanWSServerFactory(Postman, BaseWSServerFactory):
    
    
    def __init__(self, url, debug=False, debugCodePaths=False):
        BaseWSServerFactory.__init__(self, url, debug=debug, debugCodePaths=debugCodePaths)
        Postman.__init__(self)
        reactor.callLater(10, self.pulse)        

    def anticipate(self, helo, origin, user):
        ee = Postman.anticipate(self, helo, origin, user)
        return ee

    def broadcast(self, ee):
        Postman.broadcast(self, ee)
        self.email_broadcast(ee.get_broadcast_dict())
    
    def pulse(self):
        print 'pulse'
        self.heartbeat(None);
        reactor.callLater(60, self.pulse)

if __name__ == '__main__':    
    print 'start websocket factory'    
    factory = PostmanWSServerFactory(url="ws://localhost:8080")        
    reactor.listenTCP(8080, factory)
    reactor.run()    
