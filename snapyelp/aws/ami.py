from twisted.internet import reactor, defer, task

import boto.ec2
from snapyelp.aws import app_util
from snapyelp.aws import identify

@defer.inlineCallbacks
def region_instance(region_instance_seq):
    region = region_instance_seq[0]
    while region[-1:].isalpha():      
        region = region[:-1]
        print 'change to:', region
    print 'region:', region
    if region == app_util.app_region:
        print 'connect to:', region
        conn = boto.ec2.connect_to_region(region)
        for image in conn.get_all_images(owners=['self'], filters={'name': app_util.app_name}):
            try:
                print 'de-register images:', image
                image.deregister()
                print 'wait 60 seconds'
                yield task.deferLater(reactor, 60, defer.succeed, True)        
            except Exception as e:
                print 'de-register error:', e
        print 'create image:', app_util.app_name
        ami_response = conn.create_image(region_instance_seq[1], app_util.app_name)
        print 'ami response:', ami_response.state
    else:
        print 'region mismatch'
    reactor.callLater(0, reactor.stop)        

def ami_save():
    dl = defer.DeferredList([identify.get_region(), identify.get_instance()])
    dl.addCallback(lambda res: defer.succeed((res[0][1], res[1][1])))
    dl.addCallback(region_instance)

if __name__ == '__main__':
    reactor.callWhenRunning(ami_save)
    reactor.run()
