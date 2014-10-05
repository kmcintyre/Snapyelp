import json
import re
import time
from twisted.internet import defer
from twisted.names import client

from snapyelp import fixed

from snapyelp.aws import bucket_util
from snapyelp.smtp.template import EmailElement

from boto.dynamodb2.table import Table
from boto.dynamodb2.fields import HashKey, RangeKey

from twisted.web.xmlrpc import Proxy

class NullBag:

    def get_messages(self):
        return []

    def add_message(self, msg):
        pass
    
    
class Postman:        

    def __init__(self):
        self.public_dns = 'localhost'
        self.valid_domains = []
        self.invalid_domains = []    
        self.routes = []
        self.browser = None
        self.bag = NullBag()          
    
    def resend(self, client, count):
        print 'postman resend'
        for msg in self.bag.get_messages():  
            try: 
                if not client.cheap_filter(msg):
                    print "re-send message to " + client.peer
                    client.sendMessage(json.dumps(msg))
                    count += -1
                    print 'count:', count
                    if count == 0:
                        return
            except Exception as e:
                print 'resend errror:', e
                
    def anticipate(self, helo, origin, user):
        print "anticipate count:",
        return EmailElement(helo, origin, user)

    def new_email(self, incoming_email, email_element, domain):
        email_element.raw_email(incoming_email)
        email_element.domain = domain
        def error(e):
            print 'new email error:', e        
        def add_result_back(html_result):
            if email_element.html is not None:
                try:
                    pattern_obj = re.compile(fixed.html_placeholder, re.MULTILINE)
                    html_result = pattern_obj.sub(email_element.html, html_result) 
                except Exception as e:
                    print 'bind html exception:', e       
            email_element.summary = html_result                
            return email_element        
        d = email_element.flat()        
        d.addCallback(add_result_back)
        d.addCallback(self.broadcast)        
        d.addErrback(error)
        return d
    
    def broadcast(self, ee):
        print 'broadcast:', ee.get_broadcast_dict()
        print 'route lenth:', len(self.routes)
        for route in self.routes:
            try:
                route.route_email(ee)
            except Exception as e:
                print 'broadcast exception', e
        self.bag.add_message(ee.get_broadcast_dict())
        print 'return ee:', ee
        return ee
    
    def status(self):
        print 'postman status'
        status = fixed.blank_msg();
        status['from'] = 'postman'         
        status['subject'] = { 'valid_domains' : self.valid_domains, 'routes' : [str(r) for r in self.routes], 'mailbag': str(self.bag) } 
        return {'status': status}                    

    def check_domain(self, domain_name):
        print 'check_domain:', domain_name
        if domain_name == self.public_dns:
            return defer.succeed(True)
        def printresult(records):
            answers, authority, additional = records
            for a in answers:
                print 'a', a.name, a.type, a.fmt, a.payload.name
                try:
                    if str(a.payload.name) == self.public_dns:
                        return True
                except:
                    pass
            return False            
        d = client.lookupMailExchange(domain_name)
        d.addCallback(printresult)
        return d

class BrowserPreview:
        
    def route_email(self, ee):
        def error(err):
            print 'mail error:', err
        proxy = Proxy('http://localhost:8001/')
        if ee.html:
            print 'preview html in browser'
            d = proxy.callRemote('preview', ee.html, fixed.digest(ee.broadcast_dict['file_dest']) )
            d.addCallback(lambda local_file: bucket_util.save_s3( 
                             bucket_util.snapyelp_bucket('mail', 'snapyelp.com'),
                             str(ee.broadcast_dict['file_dest'] + "_preview.png"), 
                             None, 
                             local_file)
                          )                          
            d.addErrback(error)
            return d
        else:
            print 'not previewed'            
    def __repr__(self):
        return 'Preview in WebKit'
        
class PerminentHtmlS3:
        
    version = 'm2'
    
    def route_email(self, ee):
        print 'route email perm'   
        bucket_util.save_s3( 
             bucket_util.snapyelp_bucket('mail', 'snapyelp.com'),
             str(ee.broadcast_dict['file_dest'] + '.html'), 
             ee.summary, 
             None,
             'text/html'
        )

    def __repr__(self):        
        return 'Store Html in S3'


class PerminentJsonS3:
    
    def route_email(self, ee):
        bucket_util.save_s3( 
             bucket_util.snapyelp_bucket('mail', 'snapyelp.com'),
             str(ee.broadcast_dict['file_dest'] + '.json'), 
             json.dumps(ee.broadcast_dict), 
             None,
             'application/json'
        )
    def __repr__(self):
        return 'Store JSON in S3'

class Attachments:
    
    def route_email(self, ee):
        if ee.attachments is not None:
            for filename, raw_file, content_type in ee.attachments:
                bucket_util.save_s3( 
                     bucket_util.snapyelp_bucket('mail', 'snapyelp.com'),
                     ee.broadcast_dict['file_dest'] + "_" + filename, 
                     raw_file, 
                     None,
                     content_type
                )
    def __repr__(self):
        return 'Store attachments in S3'    


class BagIt:
    
    def get_mail_table(self, domain):
        mail_table = 'mail_' + domain
        print 'mail table:', mail_table        
        Base_table = Table(mail_table)        
        try:
            print mail_table, 'count:', Base_table.count()    
        except:
            print 'creating:', mail_table
            Base_table = Table.create(mail_table,
            schema=[
                HashKey('derived_to'),
                RangeKey('derived_from')        
            ],
            throughput={
            'read': 2,
            'write': 2
            })
        return Base_table    
    
    def route_email(self, ee):

        print 'bag it route_email:', ee.broadcast_dict['derived_to'], 'from:', ee.broadcast_dict['derived_from']
        try:        
            item = self.get_mail_table(ee.domain).query(derived_to__eq=ee.broadcast_dict['derived_to'], derived_from__eq=ee.broadcast_dict['derived_from'], limit=1).next()
            print 'update item'
            item['lastConnection'] = time.time()
            item['connectionsMade'] = item['connectionsMade'] + 1
            item['msg'] = item['msg'] + "," + ee.broadcast_dict['file_dest']
            item.save()
        except Exception as e:
            from boto.dynamodb2.items import Item
            print 'create item:', e
            try:
                now = time.time()
                item = Item(self.get_mail_table(ee.domain),
                    data={  
                          'derived_to' : ee.broadcast_dict['derived_to'],
                          'derived_from': ee.broadcast_dict['derived_from'],
                          'firstConnection' : now,
                          'lastConnection' : now,
                          'connectionsMade' : 1,
                          'msg': ee.broadcast_dict['file_dest']
                }
                )
                item.save()
            except Exception as e2:
                print e2
    
    def __repr__(self):
        return 'Store conversation in Dynamo'    

class MemoryBag():
    
    limit = 50
    
    def __init__(self):
        self.all_msg = []
        self.total_msg = 0
    
    def get_messages(self):
        return self.all_msg

    def add_message(self, msg):
        self.total_msg += 1
        if len(self.all_msg) > MemoryBag.limit:
            self.all_msg.pop()
        self.all_msg.insert(0, msg)

    def __repr__(self):
        return 'Memory Only ({0} total)'.format(self.total_msg)
