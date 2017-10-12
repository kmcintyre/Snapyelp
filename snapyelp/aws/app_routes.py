import boto.ec2
import boto.route53

from twisted.internet import defer, reactor
from twisted.web.client import getPage

from snapyelp.aws import app_util
from snapyelp.aws import cloudfront

def get_zone():
    for zn in boto.route53.connection.Route53Connection().get_zones():        
        if zn.name[:-1] == app_util.app_name:
            return zn

@defer.inlineCallbacks
def set_cname(domain):
    zn = get_zone()
    public_dns = yield getPage('http://169.254.169.254/latest/meta-data/public-hostname')
    if zn.find_records(domain, 'CNAME'):
        print 'update cname:', domain
        zn.update_cname(domain, public_dns, ttl=300, identifier=None)
    else:
        print 'add cname:', domain
        zn.add_cname(domain, public_dns, ttl=300, identifier=None)
        
def set_apex():
    z = get_zone()    
    dn = cloudfront.get_distro_summary().domain_name
    print 'cloudfront name:', dn
    cloudfront.get_distro_summary().domain_name
    records = z.get_records()
    create = True
    for r in records:
        print r.name, r.type, r.alias_dns_name
        if r.alias_dns_name == dn + '.':
            create = False
    if create:
        print 'create'
        records.add_change('CREATE', 
                           app_util.app_name, 
                           'A', 
                           alias_hosted_zone_id='Z2FDTNDATAQYW2', 
                           alias_dns_name=dn, 
                           alias_evaluate_target_health=False)
        records.commit()
    else:
        print 'exists'        
    
if __name__ == '__main__': 
    reactor.callWhenRunning(set_cname, 'service.snapyelp.com')
    reactor.run()