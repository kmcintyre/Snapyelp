from autobahn.twisted.websocket import WebSocketClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol

from twisted.internet.protocol import ReconnectingClientFactory

import json
import xmlrpclib

from snapyelp import fixed
from snapyelp.aws import app_util, identify

import requests

click_period = 60 * 5

#client_factory = WebSocketClientFactory('ws://' + app_util.app_service + ':8080')
client_factory = WebSocketClientFactory('ws://' + app_util.connection_host + ':' + str(app_util.connection_port))

class AgentClientProtocol(WebSocketClientProtocol):
    
    def __init__(self):
        super(AgentClientProtocol, self).__init__()
        self.swkey = None
        self.awaiting_message = None
        self.connect_message = None        
    
    def defineAgent(self, region):
        response = requests.get('http://ip-api.com/json') 
        print 'define agent:', region, response.json()        
        return { fixed.agent: { fixed.nickname: region, fixed.location: response.json() }}
    
    def onOpen(self):
        print 'open'
        d = identify.get_region()
        d.addCallback(self.defineAgent)
        d.addCallback(lambda agent: self.sendMessage(json.dumps(agent), isBinary = False))
    
    def onConnect(self, response):
        print 'connect:', response.peer
        
    def results(self, r):
        print 'results:', r
        
    def error(self, err):
        print 'error:', err 
        
    def runJob(self, incoming):
        proxy = xmlrpclib.ServerProxy('http://localhost:7000')
        return proxy.job(incoming)                    
      
    def onMessage(self, payload, isBinary):        
        if isBinary:
            print 'binary incominng'
        else:
            try:
                incoming = json.loads(payload.decode('utf8'))
                if fixed.job in incoming:
                    print 'agent job:', incoming
                    incoming.update(self.runJob(incoming))
                    self.sendMessage(json.dumps(incoming))                             
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

def start_agent(host=app_util.connection_host, port=app_util.connection_port):
    factory = ReconnectingWebSocketClientFactory()
    factory.host = host
    factory.port = port
    print 'client start:', host, port
    reactor.connectTCP(host, port, factory)

if __name__ == '__main__':
    from twisted.internet import reactor
    reactor.callWhenRunning(start_agent) 
    reactor.run()