import boto.ec2

from twisted.internet import reactor, defer
from twisted.web.client import getPage
from snapyelp.aws import app_util, app_routes, replicate

from snapyelp import fixed

import os.path
import filecmp

def get_instance():
    return getPage('http://169.254.169.254/latest/meta-data/instance-id')

def az_to_region(az):
    while az[-1:].isalpha():      
        az = az[:-1]
    return az    

def get_region():
    return getPage('http://169.254.169.254/latest/meta-data/placement/availability-zone').addCallback(az_to_region).addErrback(lambda err: defer.succeed('localhost'))

def enable_start(service_name):
    print 'enable and start:', service_name
    os.system('sudo systemctl enable ' + service_name + '.service')
    os.system('sudo systemctl start ' + service_name )
    
def service_names(region):
    sns = ['worker', 'agent']
    if region == app_util.app_region:
        sns.append('websocket')
    return sns

def service_path(sn):
    return '/home/ubuntu/Snapyelp/etc/systemd/' + sn + '.service'

def source_service_path(sn):
    return '/etc/systemd/system/' + sn + '.service'

@defer.inlineCallbacks
def selfie():
    rl = yield defer.DeferredList([get_region(), get_instance()])
    region = rl[0][1]
    instance_id = rl[1][1]
    print 'region:', region, 'instance id:', instance_id
    if region == app_util.app_region:
        yield defer.maybeDeferred(app_routes.set_cname, 'service.' + app_util.app_name)
        security_groups = yield getPage('http://169.254.169.254/latest/meta-data/security-groups')
        print 'security groups:', security_groups
    try:
        for service_name in service_names(region):
            fp = source_service_path(service_name)
            sp = service_path(service_name)
            if not os.path.exists(fp) or not filecmp.cmp(fp, sp):
                os.system('sudo cp ' + sp + ' ' + fp)
            enable_start(service_name)
        for instance in boto.ec2.connect_to_region(region).get_only_instances(instance_ids=[instance_id]):
            if fixed.tag_state in instance.tags and instance.tags[fixed.state_replicate]:
                replicate.replicate()
                instance.remove_tag(fixed.tag_state)
    except Exception as e:
        print 'exception:', e
                            
    reactor.stop()

if __name__ == '__main__':
    reactor.callWhenRunning(selfie)    
    reactor.run()
