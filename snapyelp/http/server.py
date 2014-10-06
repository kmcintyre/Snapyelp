import sys

from twisted.web import server, resource
from twisted.internet import reactor


class LoadingResource(resource.Resource):
    
    def render_GET(self, request):
        return server.NOT_DONE_YET        
    
class RootResource(resource.Resource):    
    
    isLeaf = False
    def getChild(self, name, request):
        print 'curator', name, request.uri
        if name == '':
            print 'return self!'
            return self
        
        if name in self.children:
            print 'got child'
            return resource.Resource.getChild(self, name, request)            
        else:
            return resource.NoResource()
        
    def render_GET(self, request):
        return "<html>Snapyelp</html>"
        
root = RootResource()
site = server.Site(root)
port = 8000
if len(sys.argv) > 1:
    port = int(sys.argv[1])        
    
if __name__ == '__main__':    
    reactor.listenTCP(port, site)
    print 'start reactor'
    reactor.run()
else:
    from twisted.application import internet, service
    application = service.Application("Curator")
        
    multiservice = service.MultiService()    
    http_service = internet.TCPServer(port, site)    
    http_service.setServiceParent(multiservice)
    multiservice.setServiceParent(application) 
    print 'application set'   