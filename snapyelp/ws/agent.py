from autobahn.twisted.websocket import WebSocketClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol

from twisted.internet.protocol import ReconnectingClientFactory

import json
import xmlrpclib

from snapyelp import fixed
from snapyelp.aws import app_util, identify

click_period = 60 * 5

connection_host = app_util.app_service
connection_host = 'localhost'

#client_factory = WebSocketClientFactory('ws://' + app_util.app_service + ':8080')
client_factory = WebSocketClientFactory('ws://' + connection_host + ':8080')

class AgentClientProtocol(WebSocketClientProtocol):
    
    def __init__(self):
        super(AgentClientProtocol, self).__init__()
        self.swkey = None
        self.awaiting_message = None
        self.connect_message = None        
    
    def onOpen(self):
        print 'open'
        d = identify.get_region()
        d.addCallback(lambda region: self.sendMessage(json.dumps({ fixed.agent: region}), isBinary = False))
    
    def onConnect(self, response):
        print 'connect:', response.peer
        
    def results(self, r):
        print 'results:', r
        
    def error(self, err):
        print 'error:', err        
      
    def onMessage(self, payload, isBinary):        
        if isBinary:
            print 'binary incominng'
        else:
            try:
                incoming = json.loads(payload.decode('utf8'))
                if fixed.job in incoming:
                    print 'job!'
                    proxy = xmlrpclib.ServerProxy('http://localhost:7000')
                    result = proxy.job(incoming)
                    incoming[fixed.result] = result
                    self.sendMessage(json.dumps(incoming))
                print 'incoming:', incoming                             
            except ValueError as e:
                print e

    def onClose(self, wasClean, code, reason):
        print 'close:', self.peer, wasClean, code, reason

class ReconnectingWebSocketClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    
    protocol = AgentClientProtocol
    
    def clientConnectionFailed(self, connector, reason):
        print 'clientConnectionFailed:', connector, 'reason:', reason
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        print 'clientConnectionLost:', connector, 'reason:', reason
        self.retry(connector)    

def start_agent(host=connection_host, port=8080):
    factory = ReconnectingWebSocketClientFactory()
    factory.host = host
    factory.port = port
    print 'client start:', host, port
    reactor.connectTCP(host, port, factory)

if __name__ == '__main__':
    from twisted.internet import reactor
    reactor.callWhenRunning(start_agent) 
    reactor.run()