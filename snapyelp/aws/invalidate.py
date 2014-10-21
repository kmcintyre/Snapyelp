def do_invalidate(paths, origin):
    import boto
    c = boto.connect_cloudfront()
    for d in c.get_all_distributions():
        if d.origin.dns_name == origin:
            print d.id, d.domain_name, d.status, d.comment            
            for ir in c.get_invalidation_requests(d.id):
                if ir.status != 'Completed':
                    return 'no can do!!!'
                    print 'invalidate request:', ir.id, ir.status
                            
            c.create_invalidation_request(d.id, paths)
            

cf = 'snapyelp.com.s3.amazonaws.com'
print cf
standard_file = ['/index.html', '/index.js', '/require.js']        
do_invalidate(standard_file, cf)    
