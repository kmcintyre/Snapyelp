from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.websocket import WebSocketServerProtocol

import json
from snapyelp import fixed
from snapyelp.aws import app_util

from twisted.internet import task, defer

class SnapyelpServerProtocol(WebSocketServerProtocol):
    
    stream_delay = 1
    deferred_job = None  
    
    def onConnect(self, request):
        print request
        print 'connect:', request.peer, 'key:', request.headers['sec-websocket-key'] 
        self.user = { fixed.ws_key : request.headers['sec-websocket-key'], fixed.detect_agent: request.headers['user-agent'].startswith('AutobahnPython') }

    def onOpen(self):
        print 'open:', self.user
        WebSocketServerProtocol.onOpen(self)
        self.factory.associate(self)        
        if not self.user[fixed.detect_agent]:
            agents = [a.user[fixed.agent] for a in self.factory.agents()]
            print 'agents:', agents
            self.sendMessage(json.dumps({ 'agents': agents }))                       

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
                    self.factory.pushagents()
                elif fixed.result in incoming:
                    for user in [u for u in self.factory.users() if u.user[fixed.ws_key] == incoming[fixed.ws_key]]:
                        incoming.update({ fixed.agent: self.user[fixed.agent]})
                        user.sendMessage(json.dumps(incoming))
                    self.deferred_job.callback(True)
                elif fixed.job in incoming:                    
                    job = {}
                    job.update(self.user)
                    job.update(incoming)
                    print 'queue job:', job
                    self.factory.queue.put(job)                     
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
    
    queue = defer.DeferredQueue()
    test_id = 0
    
    protocol = SnapyelpServerProtocol
    heartbeat_interval = 60
    
    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)        
        self.clients = []
        task.LoopingCall(self.heartbeat).start(self.heartbeat_interval)
        self.queue.get().addBoth(self.handle_queue)
    
    
    def maybe_cancel(self, dl):
        if not dl.called:
            print 'timeout erroring'
            dl.errback(False)
        else:
            print 'deferred fired successfully'        
    
    def handle_queue(self, queue_object):
        print 'handle queue:', self.test_id
        self.test_id += 1
        queue_object[fixed.test_id] = self.test_id
        self.user(queue_object[fixed.ws_key]).sendMessage(json.dumps({ fixed.test_id: self.test_id }))
        dl = []
        for agent in self.agents():
            print 'push to agent:', agent
            d = defer.Deferred()
            agent.deferred_job = d
            agent.sendMessage(json.dumps(queue_object))
            dl.append(d)
        dl = defer.DeferredList(dl)
        dl.addBoth(lambda ign: self.queue.get().addBoth(self.handle_queue))
        reactor.callLater(30, self.maybe_cancel, dl)

    def agents(self):
        return [c for c in self.clients if fixed.agent in c.user]
    
    def user(self, ws_key):
        for user in [u for u in self.users() if u.user[fixed.ws_key] == ws_key]:
            return user
    
    def users(self):
        return [c for c in self.clients if fixed.agent not in c.user]
    
    def pushagents(self):
        agents = {'agents' : [a.user[fixed.agent] for a in self.agents()]}
        print 'pushagents:', agents
        [u.sendMessage(json.dumps(agents)) for u in self.users()]    

    def associate(self, client):        
        print 'associate client:', client.peer        
        try:
            self.clients.append(client)            
        except Exception as e:
            print 'back log exception:', e
                
    def disassociate(self, client):    
        try:
            self.clients.remove(client)
            if fixed.agent in client.user:
                self.pushagents()
            print 'disassociate:', client.peer
        except:
            pass
        
    def heartbeat(self):
        print 'heartbeat interval:', self.heartbeat_interval, 'clients length:', len(self.clients)           
            
factor_host = 'ws://' + app_util.connection_host + ':' + str(app_util.connection_port)
print 'factor host:', factor_host
factory = SnapyelpServerFactory(factor_host)

if __name__ == '__main__':
    from twisted.internet import reactor
    reactor.listenTCP(app_util.connection_port, factory)
    reactor.run()