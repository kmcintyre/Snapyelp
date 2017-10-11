from twisted.internet import reactor, defer, task

import os
import boto.ec2
from snapyelp.aws import app_util, identify
from snapyelp import fixed

def all_images(region):    
    return boto.ec2.connect_to_region(region).get_all_images(owners=['self'], filters={'name': app_util.app_name})

@defer.inlineCallbacks
def region_instance(region_instance_seq):
    region, instance_id = region_instance_seq[0], region_instance_seq[1]
    print 'region:', region, 'instance:', instance_id
    if region == app_util.app_region:
        print 'connect to:', region
        for image in all_images(region):
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
            for service_name in identify.service_names(region):
                os.system('sudo rm ' + identify.service_path(service_name) )
            for instance in r_conn.get_only_instances(instance_ids=[instance_id]):
                print 'instance to tag:', instance
                instance.add_tag(fixed.tag_state, fixed.state_replicate)
            ami_response = r_conn.create_image(instance_id, app_util.app_name)
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
