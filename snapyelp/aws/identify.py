from twisted.internet import reactor, defer
from twisted.web.client import getPage
from snapyelp.aws import app_util, app_routes

def get_instance():
    return getPage('http://169.254.169.254/latest/meta-data/instance-id')

def az_to_region(az):
    while az[-1:].isalpha():      
        az = az[:-1]
    return az    

def get_region():
    return getPage('http://169.254.169.254/latest/meta-data/placement/availability-zone').addCallback(az_to_region)

@defer.inlineCallbacks
def selfie():
    rl = yield defer.DeferredList([get_region(), get_instance()])
    region = rl[0][1]
    instance = rl[1][1]
    print 'region:', region, 'instance:', instance
    if region == app_util.app_region:
        yield defer.maybeDeferred(app_routes.set_cname, 'service.' + app_util.app_name)
    
    reactor.stop()

if __name__ == '__main__':
    reactor.callWhenRunning(selfie)    
    reactor.run()
