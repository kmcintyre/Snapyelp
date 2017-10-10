import os
from glob import glob

from snapyelp.aws import app_util

build_dir = '/home/ubuntu/Snapyelp/build/es5-bundled'
publish_filters = ['*.html', 'bower_components/webcomponentsjs/webcomponents-loader.js', 'bower_components/webcomponentsjs/custom-elements-es5-adapter.js']

def get_publish_list():
    pl = set([])
    for pf in publish_filters:
        result = [y for x in os.walk(build_dir) for y in glob(os.path.join(x[0], pf))]
        for res in result:
            pl.add(res)
    return list(pl)

def do_publish():         
    for res in get_publish_list():    
        publish_to = res[len(build_dir)+1:]
        key = app_util.save_s3(publish_to, None, res)
        print publish_to, 'to:', key.name
        
if __name__ == '__main__':    
    do_publish()
