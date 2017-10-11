from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.websocket import WebSocketServerProtocol

import json
from snapyelp import fixed

from twisted.internet import reactor

class SnapyelpServerProtocol(WebSocketServerProtocol):
    
    stream_delay = 1    
    
    def onConnect(self, request):
        print 'connect:', request.peer, 'key:', request.headers['sec-websocket-key']
        self.chk = request.headers['sec-websocket-key']
        self.user = { fixed.ws_key : self.chk }

    def onOpen(self):
        print "open:", self.peer
        WebSocketServerProtocol.onOpen(self)
        self.factory.associate(self)
        self.sendMessage(str(self.user[fixed.ws_key]))                       

    def jsonMessage(self, msg = None):
        if self.user:        
            if msg:
                msg.update(self.user)
                self.sendMessage(json.dumps(msg))
            else:
                self.sendMessage(json.dumps(self.user))            
    
    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                incoming = json.loads(payload.decode('utf8'))
                if 'operator' in incoming and 'reservation' in incoming:
                    print 'reservation response:', incoming
                    del self.user['busy']
                    instagator = self.factory.get_clients(incoming['reservation'])                    
                    instagator.jsonMessage({ 'reservation':  incoming['rn'] + ' ' + incoming['ri'] + ' reserved by:' + incoming['dn']})
                elif 'operator' in incoming:
                    print 'set operator'
                    self.user['operator'] = incoming['operator']                    
                elif 'site' in incoming and 'reserve' in incoming:
                    operator = self.factory.get_operator()
                    if operator: 
                        operator.jsonMessage({ 'reserve': incoming['reserve'], 'reserve_key' : self.user[fixed.ws_key]})
                    else:
                        self.jsonMessage({ 'reservation': 'Agent Busy' })
                    
                elif 'site' in incoming:
                    self.user['site']  = incoming['site']
                else:
                    print 'wtf?:', self.peer, incoming
            except ValueError as e:
                print 'value error:', e
                if isinstance(payload, str):
                    if self.user[fixed.ws_key] == payload:
                        print 'string value:', payload
                        self.jsonMessage()
                else:
                    print 'wtf2?'
                    raise e
            except Exception as e2:
                print 'onMessage exception:', e2, payload
        elif isBinary:
            print 'ignore binary'

    def onClose(self, wasClean, code, reason):
        self.factory.disassociate(self)
        print "connection close: {0} was clean: {1} code: {2}".format(self.peer,wasClean,code)        


class SnapyelpServerFactory(WebSocketServerFactory):
    
    protocol = SnapyelpServerProtocol
    
    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)        
        self.clients = []        

    def associate(self, client):        
        print 'associate client:', client.peer        
        try:
            self.clients.append(client)            
        except Exception as e:
            print 'back log exception:', e
                
    def disassociate(self, client):    
        try:
            self.clients.remove(client)
            print 'disassociate:', client.peer
        except:
            pass            

    def get_operator(self):
        try:
            operator = [c for c in self.clients if 'operator' in c.user.keys() and 'busy' not in c.user.keys()][0]
            operator.user['busy'] = True
            return operator
        except:
            return None
         

    def get_clients(self, key = None):
        if not key:
            return [c for c in self.clients if 'site' in c.user.keys()]
        else:
            print 'get specific client:', key
            try:
                return [c for c in self.clients if 'site' in c.user.keys() and c.user[fixed.ws_key] == key][0]
            except:
                pass
            
factory = SnapyelpServerFactory("ws://localhost:8082")

if __name__ == '__main__':
    reactor.listenTCP(8082, factory)
    reactor.run()