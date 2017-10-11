from snapyelp.qt import qt5

from snapyelp.qt import view

from snapyelp import fixed

from twisted.web import xmlrpc, server
from twisted.internet import reactor, defer, task

class AgentWorker(xmlrpc.XMLRPC):
    
    @defer.inlineCallbacks
    def xmlrpc_job(self, job):
        print 'job:', job
        result = []
        window = view.ChromeView()
        window.setFixedWidth(1366)
        window.setFixedHeight(768)
        window.show()
        window.page().profile().setRequestInterceptor(view.intercept)
        yield window.goto_url(job[fixed.job][0][fixed.url])
        qt5.app.toImage()
        defer.returnValue(result)
        
if __name__ == '__main__':
    aw = AgentWorker(allowNone=True)
    reactor.listenTCP(7002, server.Site(aw))
    reactor.run()
