from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.websocket import WebSocketServerProtocol

import json
from snapyelp import fixed

from twisted.internet import task

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
                if fixed.agent in incoming and fixed.agent not in self.user:
                    print 'update as agent:', incoming
                    self.user.update(incoming)
                elif fixed.result in incoming:
                    print 'got result:', incoming
                elif fixed.job in incoming:
                    job = {}
                    job.update(self.user)
                    job.update(incoming)
                    print 'job:', job 
                    [c.sendMessage(json.dumps(job)) for c in self.factory.agents()]
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
    heartbeat_interval = 60
    
    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)        
        self.clients = []
        task.LoopingCall(self.heartbeat).start(self.heartbeat_interval)        

    def agents(self):
        return [c for c in self.clients if fixed.agent in c.user]

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
        
    def heartbeat(self):
        print 'heartbeat interval:', self.heartbeat_interval, 'clients length:', len(self.clients)           
            
factory = SnapyelpServerFactory("ws://localhost:8080")

if __name__ == '__main__':
    from twisted.internet import reactor
    reactor.listenTCP(8080, factory)
    reactor.run()