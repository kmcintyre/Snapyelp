from twisted.internet import reactor, defer
from twisted.web.client import getPage
from snapyelp.aws import app_util, app_routes

@defer.inlineCallbacks
def update_route_53(region, instance):
    print 'region:', region, 'instance:', instance
    if region == app_util.app_region:
        yield defer.maybeDeferred(app_routes.set_cname, 'service.' + app_util.app_name)
    reactor.stop()
    
def get_public_dns():
    return getPage('http://169.254.169.254/latest/meta-data/public-hostname')    

def get_instance():
    return getPage('http://169.254.169.254/latest/meta-data/instance-id')

def az_to_region(az):
    while az[-1:].isalpha():      
        az = az[:-1]
    return az    

def get_region():
    return getPage('http://169.254.169.254/latest/meta-data/placement/availability-zone').addCallback(az_to_region)

def self_error(err):
    print 'selfie error:', err
    reactor.stop()

def selfie():
    dl = defer.DeferredList([get_region(), get_instance()])
    dl.addCallback(lambda rl: update_route_53(rl[0][1], rl[1][1]))
    dl.addErrback(self_error)
    return dl

if __name__ == '__main__':
    reactor.callWhenRunning(selfie)    
    reactor.run()
