from snapyelp.opentable import user

from snapyelp.opentable import find

from snapyelp import fixed

from twisted.internet import reactor, defer

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

from autobahn.twisted.websocket import WebSocketClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol

import json

click_period = 60 * 5
client_factory = WebSocketClientFactory("ws://service.snapyelp.com:8081", debug = False)


class OperatorClientProtocol(WebSocketClientProtocol):
    
    def __init__(self):
        self.swkey = None
        self.awaiting_message = None
        self.connect_message = None
        
    def autostart(self, message):
        print 'autostart', message
        self.connect_message = message        
        self.awaiting_message = defer.Deferred()                
        return self.awaiting_message     

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
                    window = user.create_window()
                    d = user.do_login(window)
                    d.addCallback(lambda ign: find.do_find(window))
                    d.addCallback(reservation_result, window)
            except ValueError as e:
                if isinstance(payload, str):
                    self.swkey = payload
                    if self.connect_message:
                        self.connect_message[fixed.swkey] = self.swkey                    
                        self.sendMessage(json.dumps(self.connect_message))                        
                else:
                    raise e
            

    def onClose(self, wasClean, code, reason):
        print 'close:', self.peer, wasClean, code, reason

def new_protocol(protocol):
    print 'new_protocol:', protocol
    protocol.autostart({'operator':'opentable'})

def run_operate():
    print 'run operate:'
    point = TCP4ClientEndpoint(reactor, "service.snapyelp.com", 8081)
    operator = OperatorClientProtocol()
    operator.factory = client_factory
    d = connectProtocol(point, operator)
    d.addCallback(new_protocol)            
    return d

if __name__ == '__main__':
    reactor.callWhenRunning(run_operate) 
    reactor.run()
