from twisted.internet import reactor

from snapyelp.smtp.processor import MemoryBag, PerminentHtmlS3, PerminentJsonS3, Attachments, BrowserPreview, BagIt
from snapyelp.smtp.base import BaseSMTPServerFactory
from snapyelp.smtp.ws import PostmanWSServerFactory

smtp_port = 1025
ws_port = 8025

postman = PostmanWSServerFactory(url="ws://localhost:%s" % str(ws_port))
postman.bag = MemoryBag()    
postman.routes.append(PerminentHtmlS3())
postman.routes.append(PerminentJsonS3())
postman.routes.append(BrowserPreview())
postman.routes.append(BagIt())
postman.routes.append(Attachments())

smptfactory = BaseSMTPServerFactory(postman=postman)
    
if __name__ == '__main__':
    reactor.listenTCP(ws_port, postman)    
    reactor.listenTCP(smtp_port, smptfactory)    
    #reactor.callLater(3.14, frontpage)
    print 'start reactor'
    reactor.run()
else:
    from twisted.application import internet, service
    application = service.Application("SmtpWS")
    
    multiservice = service.MultiService()
    
    ws_service = internet.TCPServer(ws_port, postman)
    stmp_service = internet.TCPServer(smtp_port, smptfactory)
    
    ws_service.setServiceParent(multiservice)
    stmp_service.setServiceParent(multiservice)
    
    print 'application set'    
    multiservice.setServiceParent(application)
    reactor.callLater(3.14, frontpage)