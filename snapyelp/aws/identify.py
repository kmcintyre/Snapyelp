from twisted.internet import reactor, defer
from twisted.web.client import getPage
from snapyelp.aws import app_util, app_routes

import os.path
import filecmp

def get_instance():
    return getPage('http://169.254.169.254/latest/meta-data/instance-id')

def az_to_region(az):
    while az[-1:].isalpha():      
        az = az[:-1]
    return az    

def get_region():
    return getPage('http://169.254.169.254/latest/meta-data/placement/availability-zone').addCallback(az_to_region)

def enable_start(service_name):
    print 'enable and start:', service_name
    os.system('sudo systemctl enable ' + service_name + '.service')
    os.system('sudo systemctl start ' + service_name )

@defer.inlineCallbacks
def selfie():
    rl = yield defer.DeferredList([get_region(), get_instance()])
    region = rl[0][1]
    instance = rl[1][1]
    print 'region:', region, 'instance:', instance
    default_services = ['worker', 'agent']
    if region == app_util.app_region:
        yield defer.maybeDeferred(app_routes.set_cname, 'service.' + app_util.app_name)
        default_services.append('service')
    for service_name in default_services:
        file_path = '/etc/systemd/system/' + service_name + '.service'
        service_path = '/home/ubuntu/Snapyelp/etc/systemd/' + service_name + '.service'
        if not os.path.exists(file_path) or not filecmp.cmp(file_path, service_path):
            os.system('sudo cp ' + service_path + ' /etc/systemd/system/' + service_name + '.service')
        enable_start(service_name)
    reactor.stop()

if __name__ == '__main__':
    reactor.callWhenRunning(selfie)    
    reactor.run()
