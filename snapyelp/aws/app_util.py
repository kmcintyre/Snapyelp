import boto
import mimetypes

app_name = 'snapyelp.com'
app_region = 'us-east-2'
app_bucket = app_name + '.s3.amazonaws.com'
app_service = 'service.' + app_name

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

def bucket():
    try:
        return bucket_conv(app_name)
    except:
        print 'creating a bucket:', app_name
        return boto.connect_s3().create_bucket(app_name)
                    
def save_s3(filename, contents, systemfile, content_type=None, acl='public-read', meta=None):
    from boto.s3.key import Key
    key = Key(bucket(),filename) 
    if content_type is not None:        
        key.set_metadata('Content-Type', content_type)
    elif systemfile:
        gt = mimetypes.guess_type(systemfile)
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
        key.set_contents_from_file(open(systemfile, 'r'))        
    if acl is not None:
        key.set_acl(acl)
    return key