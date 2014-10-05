from boto.route53.connection import Route53Connection

from twisted.web.client import Agent
from twisted.internet import reactor


from snapyelp import fixed_twisted

agent_browser = Agent(reactor)

def set_mx_domain(mail_dns):
    conn = Route53Connection()
    for hz in conn.get_zones():
        print hz.name
        print hz.id
        #mx = hz.get_mx(hz.name)
        try:
            hz.update_mx(hz.name, "20 " + mail_dns, ttl=300, identifier=None, comment='Mail for:' + hz.name)
            print 'good:', hz.name
        except:
            print 'bad:', hz.name
        #hz.update_mx('ec2-107-22-104-72.compute-1.amazonaws.com', 20)
        #print hz
        #print hz.id
        #for r in hz.get_records():
        #    if r.type == 'MX':
        #        print r
        #        print '    ', r.type, r.name, r.identifier
        #        r.add_change('identifier',mail_dns)
        #        r.commit()


def printint(ans):
    print ans

def get_instance():
    d = agent_browser.request('http://169.254.169.254/latest/meta-data/instance-id')
    d.addCallback(fixed_twisted.get_body)
    
reactor.run()