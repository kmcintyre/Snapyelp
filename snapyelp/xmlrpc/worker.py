from snapyelp.qt import qt5

from snapyelp.qt import view

from snapyelp import fixed

from twisted.web import xmlrpc, server
from twisted.internet import reactor, defer, task
import hashlib
import time


class AgentWorker(xmlrpc.XMLRPC):
    
    def get_window(self, width = 1366, height = 768):
        window = view.ChromeView()
        window.setFixedWidth(width)
        window.setFixedHeight(height)
        window.show()
        window.page().profile().setRequestInterceptor(view.intercept)
        return window
    
    def verify_or_goto_url(self, window, url):
        if window.page().url().toString() == url:
            return defer.succeed(True)
        else:
            return window.goto_url(url)        
    
    @defer.inlineCallbacks
    def xmlrpc_job(self, job, location = None, bucket = None):
        print 'job:', job
        window = self.get_window()        
        for j in job[fixed.job]:
            url = j[fixed.url]
            start_time = time.time()
            yield self.verify_or_goto_url(window, url)
            j[fixed.load_time] = time.time() - start_time
            j[fixed.requests] = view.intercept.requests            
            if location:
                self.snapshot(url, window, location, bucket)
        job[fixed.result] = True                    
        defer.returnValue(job)
    
    def xmlrpc_snapshot(self, url, location = None, bucket = None):
        self.snapshot(url, self.get_window(), location, bucket)        
    
    @defer.inlineCallbacks
    def snapshot(self, url, cv = None, location = None, bucket = None):
        yield self.verify_or_goto_url(cv, url)
        qt5.app.toImage(location, bucket)
        yield task.deferLater(reactor, 1, defer.succeed, True)
        
        #https://www.google.com/search?q=where+am+i+right+now
    
if __name__ == '__main__':
    aw = AgentWorker(allowNone=True)
    reactor.listenTCP(7000, server.Site(aw))
    reactor.run()
