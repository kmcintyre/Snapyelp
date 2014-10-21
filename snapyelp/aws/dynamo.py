'''
Created on Oct 12, 2014

@author: kevin

http server for end-points related to build out
'''

from boto.dynamodb2.fields import HashKey, RangeKey
from boto.dynamodb2.table import Table, Item

import time
import random
from snapyelp import fixed

allow_overwrite = True

class CommonTable(Table):
        
    def __init__(self, *args, **kwargs):
        super(CommonTable, self).__init__(*args, **kwargs)                

    def view(self):
        v = []
        for s in self.scan():
            v.append(fixed.item_to_dict(s))
        return v
    
    def furnish(self, member):          
        from boto.dynamodb2.exceptions import ConditionalCheckFailedException  
        try:
            if 'ts_add' not in member:
                member['ts_add'] = int(time.time())
            item = Item(self, data=member)
            try:             
                item.save(overwrite=False)
                print 'save complete'
            except ConditionalCheckFailedException as e:
                if allow_overwrite:
                    print 'overwrite'
                    item.save(overwrite=True)
                else:
                    print 'overwrite blocked'                        
        except Exception as e:
            print 'ADD exception:', e, member

class OpenTable(CommonTable):

    def __init__(self, *args, **kwargs):
        super(OpenTable, self).__init__('opentable')
        try:
            print 'opentable count:', self.count()
        except:
            Table.create('opentable',
              schema=[
                HashKey('city')
              ],
              throughput={
                'read': 1,
                'write': 1
            }, indexes=[
            ])
            print 'creating dynamo opentable table'
    
    def get_active(self):
        city = random.choice(self.view)
        if 'no_good' not in city:
            return city
        else:
            return self.get_active()