from twisted.internet import reactor, defer, task

import boto.ec2
from snapyelp.aws import app_util
from snapyelp.aws import identify

def all_instances(region):    
    return boto.ec2.connect_to_region(region).get_all_images(owners=['self'], filters={'name': app_util.app_name})

@defer.inlineCallbacks
def region_instance(region_instance_seq):
    region, instance = region_instance_seq[0], region_instance_seq[1]
    while region[-1:].isalpha():      
        region = region[:-1]
        print 'change to:', region
    print 'region:', region, 'instance:', instance
    if region == app_util.app_region:
        print 'connect to:', region
        for image in all_instances(region):
            try:
                print 'de-register images:', image
                image.deregister()
                print 'wait 20 seconds'
                yield task.deferLater(reactor, 20, defer.succeed, True)        
            except Exception as e:
                print 'de-register error:', e
        print 'create image:', app_util.app_name
        r_conn = boto.ec2.connect_to_region(region)
        try:
            ami_response = r_conn.create_image(instance, app_util.app_name)
            print 'ami response:', ami_response
        except Exception as e:
            print 'exception:', e       
    else:
        print 'region mismatch'
    yield task.deferLater(reactor, 1, defer.succeed, True)    
    print 'complete'
    reactor.callLater(0, reactor.stop)        

def ami_save():
    dl = defer.DeferredList([identify.get_region(), identify.get_instance()])
    dl.addCallback(lambda res: defer.succeed((res[0][1], res[1][1])))
    dl.addCallback(region_instance)

if __name__ == '__main__':
    reactor.callWhenRunning(ami_save)
    reactor.run()
