import boto
import mimetypes

snapyelpbucket = 'snapyelp.com'

def check_key(bucket, filename):
    possible_key = bucket.get_key(filename)
    if possible_key:
        return possible_key.metadata
    else:
        return None

def bucket_conv(bucket_name):
    try:
        return boto.connect_s3().get_bucket(bucket_name)
    except Exception as e:
        print 'missing bucket?:', e, bucket_name
        raise e

def snapyelp_bucket():
    try:
        return bucket_conv(snapyelpbucket)
    except:
        print 'creating a bucket:', snapyelpbucket
        return boto.connect_s3().create_bucket(snapyelpbucket)
                    
def save_s3(filename, contents, systemfile, content_type=None, acl='public-read', meta=None):
    from boto.s3.key import Key
    #print 'save s3:', bucket.name, filename, systemfile
    key = Key(snapyelp_bucket(),filename) 
    if content_type is not None:        
        key.set_metadata('Content-Type', content_type)
    elif systemfile:
        gt = mimetypes.guess_type(systemfile)
        #print 'guest type:', gt[0], systemfile
        key.set_metadata('Content-Type', gt[0])
    if meta is not None:
        for seq in meta:
            try:
                print 'meta:', seq[0], seq[1], seq[1].__class__            
                key.set_metadata(seq[0], seq[1] )
            except Exception as e:
                print 'except meta:', seq[0], e.__class__.__name__     
    if contents is not None:
        print 'set contents-direct:', len(contents), filename
        key.set_contents_from_string(contents)
    if systemfile is not None:        
        #print 'set filesystem'
        key.set_contents_from_file(open(systemfile, 'r'))        
    if acl is not None:
        #print 'set acl'
        key.set_acl(acl)
        #deal_with_meta(key,meta)
    return key     