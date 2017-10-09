from twisted.internet import reactor, defer

from twisted.web.client import getPage

import boto.ec2

def update_route_53(region, instance):
    print 'region:', region, 'instance:', instance 
    reactor.stop()

def add_instance():
    return getPage('http://169.254.169.254/latest/meta-data/instance-id')

def get_region():
    return getPage('http://169.254.169.254/latest/meta-data/placement/availability-zone')

def self_error(err):
    print 'selfie error:', err
    reactor.stop()

def selfie():
    dl = defer.DeferredList([get_region(), add_instance()])
    dl.addCallback(lambda rl: update_route_53(rl[0][1], rl[1][1]))
    dl.addErrback(add_instance)
    return dl

reactor.callWhenRunning(selfie)    
reactor.run()
