from snapyelp.aws import publish, app_util
import boto

def do_invalidate():
    
    c = boto.connect_cloudfront()
    for d in c.get_all_distributions():
        if d.origin.dns_name == app_util.app_bucket:
            print 'domain id:', d.id, 'domain name:', d.domain_name, 'domain status:', d.status, 'comment:', d.comment            
            for ir in c.get_invalidation_requests(d.id):
                if ir.status != 'Completed':
                    print 'invalidate request:', ir.id, ir.status
                    exit(1)
            paths = [res[len(publish.build_dir):] for res in publish.get_publish_list()]            
            if paths:
                print 'invalidate paths:', paths
                c.create_invalidation_request(d.id, paths)
            else:
                print 'invalidate skipped'                

if __name__ == '__main__':    
    do_invalidate()            
