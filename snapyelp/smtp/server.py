'''
Created on Oct 12, 2014

@author: kevin

Multi-service SMTP server and web socket server  
'''

from twisted.internet import reactor

from snapyelp.smtp.processor import MemoryBag, PerminentHtmlS3, Attachments, BrowserPreview, BagIt
from snapyelp.smtp.base import BaseSMTPServerFactory
from snapyelp.smtp.ws import PostmanWSServerFactory

smtp_port = 25
ws_port = 8025

def set_public_dns(postman_factory, failover = None):
    from twisted.web.client import getPage
    def set_localhost(err):
        print err
        print 'failover (None is don`t accept - accept from 127.0.0.1)'
        postman_factory.public_dns = failover
        
    def set_domain(domain):
        print 'set domain:', domain        
        postman_factory.public_dns = domain                            
    d = getPage('http://169.254.169.254/latest/meta-data/public-hostname')
    d.addCallback(set_domain)
    d.addErrback(set_localhost)


postman = PostmanWSServerFactory(url="ws://localhost:%s" % str(ws_port))
set_public_dns(postman)
postman.bag = MemoryBag()    
postman.routes.append(PerminentHtmlS3())
postman.routes.append(BrowserPreview())
postman.routes.append(BagIt())
postman.routes.append(Attachments())

smptfactory = BaseSMTPServerFactory(postman=postman)
    
if __name__ == '__main__':
    reactor.listenTCP(ws_port, postman)    
    reactor.listenTCP(smtp_port, smptfactory)    
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
