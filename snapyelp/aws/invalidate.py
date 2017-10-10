from snapyelp.aws import cloudfront
from snapyelp.aws import publish

def do_invalidate():
    import boto
    c = boto.connect_cloudfront()
    for d in c.get_all_distributions():
        if d.origin.dns_name == cloudfront.snapyelpdisto:
            print 'domain id:', d.id, 'domain name:', d.domain_name, 'domain status:', d.status, 'comment:', d.comment            
            for ir in c.get_invalidation_requests(d.id):
                if ir.status != 'Completed':
                    print 'invalidate request:', ir.id, ir.status
                    exit(1)
            paths = [res[len(publish.build_dir):] for res in publish.get_publish_list()]
            print 'paths:', paths
            c.create_invalidation_request(d.id, paths)

if __name__ == '__main__':    
    do_invalidate()            
