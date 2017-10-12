import boto
from snapyelp.aws import app_util

def get_distro_summary():
    for d in boto.connect_cloudfront().get_all_distributions():
        if d.origin.dns_name == app_util.app_bucket:            
            return d

def create_distro():
    origin = boto.cloudfront.origin.S3Origin(app_util.app_bucket)
    distro = boto.connect_cloudfront().create_distribution(cnames=[app_util.app_name], origin=origin, enabled=False, comment='Snapyelp Distribution')
    return distro

if __name__ == '__main__': 
    if get_distro_summary():
        ds = get_distro_summary()
        print 'origin:', ds.origin.dns_name, 'enabled:', ds.enabled, 'domain name:', ds.domain_name
        if not ds.enabled:
            print 'enable distro'
            ds.get_distribution().enable()
        dc = boto.connect_cloudfront().get_distribution_config(ds.id)        
        if dc.default_root_object != 'index.html':
            print 'need to set Default Root Object'
    else:
        d = create_distro()
        print 'create distro:', d
    
        