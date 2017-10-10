import boto.ec2
import boto.route53
from snapyelp.aws import bucket_util
from snapyelp.aws import cloudfront

def get_zone():
    for zn in boto.route53.connection.Route53Connection().get_zones():        
        if zn.name[:-1] == bucket_util.snapyelpbucket:
            return zn
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
                           bucket_util.snapyelpbucket, 
                           'A', 
                           alias_hosted_zone_id='Z2FDTNDATAQYW2', 
                           alias_dns_name=dn, 
                           alias_evaluate_target_health=False)
        records.commit()
    else:
        print 'exists'        
    
if __name__ == '__main__': 
    set_apex()