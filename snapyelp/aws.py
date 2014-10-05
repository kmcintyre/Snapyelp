
from boto.route53.connection import Route53Connection
from twisted.web.client import Agent
from twisted.internet import reactor, defer

import boto.ec2

from snapyelp import fixed_twisted

agent_browser = Agent(reactor)

def update_route_53(instance, region):
    print 'instance:', instance

    conn = boto.ec2.connect_to_region(region)
    reservations = conn.get_all_instances(instance_ids=[instance])
    instance = reservations[0].instances[0]
    
    tagname = instance.tags['Name']
    print 'site:', tagname
    route53 = Route53Connection()
    for hz in route53.get_zones():
	print 'hz:', hz.name[:-1]
	if hz.name[:-1] == tagname:
	    print hz.find_records(tagname,'MX')
	    print 'ip address:', instance.ip_address
	    if hz.find_records(tagname,'MX'):
		print 'update mx'
	        hz.update_mx(hz.name, "20 " + instance.ip_address, ttl=300, identifier=None, comment='Mail for:' + hz.name)
	    else:
		print 'add mx'
	        hz.add_mx(hz.name, "20 " + instance.ip_address, ttl=300, identifier=None, comment='Mail for:' + hz.name)


def add_instance(region):
    print 'region:', region
	
    for r in boto.ec2.regions():
	if r.name in region:
	    region = r.name

    print 'region:', region
    d = agent_browser.request('GET', 'http://169.254.169.254/latest/meta-data/instance-id')
    d.addCallback(fixed_twisted.get_body)
    d.addCallback(update_route_53, region)

def get_region():
    d = agent_browser.request('GET', 'http://169.254.169.254/latest/meta-data/placement/availability-zone')
    d.addCallback(fixed_twisted.get_body)
    return d

def selfie():
    d = get_region()
    d.addCallback(add_instance)



reactor.callWhenRunning(selfie)    
reactor.run()
