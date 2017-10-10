from twisted.internet import reactor, defer, task

import boto.ec2
from snapyelp.aws import bucket_util
from snapyelp.aws import identify

@defer.inlineCallbacks
def region_instance(region_instance_seq):
    print region_instance_seq
    print 'ans:', region_instance_seq[0], region_instance_seq[1]
    conn = boto.ec2.connect_to_region(region_instance_seq[0])
    #for image in conn.get_all_images(owners=['self'], filters={'name': bucket_util.snapyelpbucket}):
    #    try:
    #        print 'de-register images:', image
    #        image.deregister()
    #    except Exception as e:
    #        print 'de-register error:', e
    yield task.deferLater(reactor, 60, defer.succeed, True)
    print 'create image:', bucket_util.snapyelpbucket
    conn.create_image(region_instance_seq[1], bucket_util.snapyelpbucket)

def ami():
    dl = defer.DeferredList([identify.get_region(), identify.get_instance()])
    dl.addCallback(lambda res: defer.succeed((res[0][1], res[1][1])))
    dl.addCallback(region_instance)

if __name__ == '__main__':
    reactor.callWhenRunning(ami)
    reactor.run()
