from autobahn.twisted.websocket import WebSocketClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol

from twisted.internet.protocol import ReconnectingClientFactory

from twisted.internet import defer

import json

from snapyelp import fixed

click_period = 60 * 5
client_factory = WebSocketClientFactory("ws://localhost:8082")

class AgentClientProtocol(WebSocketClientProtocol):
    
    def __init__(self):
        super(AgentClientProtocol, self).__init__()
        self.swkey = None
        self.awaiting_message = None
        self.connect_message = None        
    
    def onOpen(self):
        print 'open'
        self.sendMessage(json.dumps({ fixed.agent: 'localhost'}), isBinary = False)        
    
    def onConnect(self, response):
        print 'connect:', response.peer
      
    def onMessage(self, payload, isBinary):        
        if isBinary:
            print 'binary incominng'
        else:
            try:
                incoming = json.loads(payload.decode('utf8'))
                print 'incoming:', incoming
                if 'reserve' in incoming:
                    def reservation_result(res, win):
                        print 'reservation_result:', res, win
                        reservation_msg = {'rn': res[0], 'ri': res[1], 'dn': res[2], 'reservation' : incoming['reserve_key']}
                        reservation_msg.update(self.connect_message)
                        self.sendMessage(json.dumps(reservation_msg))                    
            except ValueError as e:
                if isinstance(payload, str):
                    self.swkey = payload
                    if self.connect_message:
                        self.connect_message[fixed.ws_key] = self.swkey                    
                        self.sendMessage(json.dumps(self.connect_message))                        
                else:
                    raise e
            

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

def start_agent(host='localhost', port=8082):
    factory = ReconnectingWebSocketClientFactory()
    factory.host = host
    factory.port = port
    print 'client start:', host, port
    reactor.connectTCP(host, port, factory)

if __name__ == '__main__':
    from twisted.internet import reactor
    reactor.callWhenRunning(start_agent) 
    reactor.run()
