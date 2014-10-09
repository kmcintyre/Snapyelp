import sys

from twisted.web import server, resource
from twisted.internet import reactor


from snapyelp.aws import dynamo
from snapyelp import fixed

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
        print request
        html = "<html>"        
        for ot in dynamo.OpenTable().scan():
            ag = fixed.item_to_dict(ot)
            del ag['citypassword']
            html += str(ag)
            html += "<br><br>"
        html += "</html>"
        request.write(html)
        request.finish()
        return server.NOT_DONE_YET
        
root = RootResource()
site = server.Site(root)
port = 80
if len(sys.argv) > 1:
    try:
        port = int(sys.argv[1])
    except:
        print 'bad pro?:', port        
    
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
