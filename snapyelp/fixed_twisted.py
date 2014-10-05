
from twisted.internet import defer, protocol    
from twisted.web.client import ResponseDone

import StringIO

class StringIOResponse(protocol.Protocol): 
    
    def __init__(self, respone_deferred):
        self.respone_deferred = respone_deferred
        self.respone_value = StringIO.StringIO()

    def dataReceived(self, b):
        # print 'data received', b
        self.respone_value.write(b)
                                            
    def connectionLost(self, reason):
        if reason.check(ResponseDone):
            rep_string = self.respone_value.getvalue()
            self.respone_deferred.callback(rep_string)
        else:
            if (not self.respone_deferred.called):
                self.respone_deferred.errback(reason)
                
def get_body(response):
    finished = defer.Deferred()
    response.deliverBody(StringIOResponse(finished))
    return finished      