import boto.ec2
import boto.vpc

import os

from snapyelp.aws import app_util

import time
from twisted.internet import defer, reactor

from os.path import expanduser

def get_master_ami():
    conn = boto.ec2.connect_to_region(app_util.app_region)
    for image in conn.get_all_images(owners=['self'], filters={'name': app_util.app_name}):
        #print 'source image:', image.id, image.name, image.tags
        return image
    
def get_region_ami(region, ami_id, create):    
    r_conn = boto.ec2.connect_to_region(region)
    for r_image in r_conn.get_all_images(owners=['self'], filters={'name': app_util.app_name}):
        return r_image
    if create:            
        print region, 'need to clone image:', ami_id
        replicate_response = r_conn.copy_image(app_util.app_region, ami_id, app_util.app_name)
        print 'replicate_response:', replicate_response
        has_replication = False
        while not has_replication:
            print region, ' waiting replication'
            time.sleep(10)
            for replicated_image in r_conn.get_all_images(owners=['self'], filters={'name': app_util.app_name}):
                has_replication = True
                return replicated_image                                 

#blocked = ['us-east-1']
blocked = []
def get_regions():
    conn = boto.ec2.connect_to_region(app_util.app_region)
    return [s for s in sorted(conn.get_all_regions(), key = lambda r: r.name) if s.name not in blocked]

def destroy(instances=True, images=True):    
    for r in get_regions():
        r_conn = boto.ec2.connect_to_region(r.name)
        if instances:    
            for d_instance in r_conn.get_only_instances(filters={"tag:App" : app_util.app_name}):
                if d_instance.state != 'terminated':                    
                    d_instance.terminate()
                    print r.name, 'terminate instance:', d_instance.id
        if r.name != app_util.app_region:
            if images:  
                for r_image in r_conn.get_all_images(owners=['self'], filters={'name': app_util.app_name}):
                    if r_image.state == 'available':                        
                        r_image.deregister()
                        print r.name, 'deregister:', r_image.id
                        deregistered = False
                        while not deregistered:
                            time.sleep(10)
                            all_images = r_conn.get_all_images(owners=['self'], filters={'name': app_util.app_name})
                            if len(all_images) == 0:
                                deregistered = True
                            for dr_image in all_images:
                                print r.name, 'waiting deregister:', dr_image.id, 'state:', dr_image.state
                                    
                    else:
                        print 'already deregisted:', r_image.state
                for s in r_conn.get_all_snapshots(owner='self'):
                    if get_master_ami().id in s.description:
                        delete_response = s.delete()
                        print 'delete:', delete_response, r.name, 'snapshot:', s.id, 'status:', s.status
@defer.inlineCallbacks
def replicate():
    image = get_master_ami()
    dl = []
    for r in get_regions():
        if r.name != app_util.app_region:
            d = defer.maybeDeferred(get_region_ami, r.name, image.id, True)
            dl.append(d)
    rl = yield defer.DeferredList(dl)
    for replication_ami in [r[1] for r in rl]:
        print replication_ami.id, replication_ami.state

def instances():
    for r in get_regions():
        r_conn = boto.ec2.connect_to_region(r.name)
        securitygroups = [sg for sg in r_conn.get_all_security_groups() if sg.vpc_id and sg.name == 'default']
        if len(securitygroups) == 0:
            print 'need security group'
        subnets = boto.vpc.connect_to_region(r.name).get_all_subnets()
        r_ami = get_region_ami(r.name, get_master_ami().id, False)
        if r_ami:         
            print r.name, 'replication ami:', r_ami.id, 'security groups:', [(s.name, s.vpc_id) for s in securitygroups], 'subnets:', subnets
            has_instance = False
            for instance in r_conn.get_only_instances(filters={"tag:App" : app_util.app_name}):
                if instance.state != 'terminated':
                    print 'existing instance:', instance.id, 'state:', instance.state
                    has_instance = True
            if not has_instance:
                print r.name, 'need instance:', r_ami
                interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(
                    subnet_id=subnets[0].id,
                    groups=[securitygroups[0].id],
                    associate_public_ip_address=True
                )
                interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)
                _it = 't2.nano'
                print 'instance type:', _it                
                try:
                    reservation = r_conn.run_instances(
                        image_id=r_ami.id,
                        instance_type=_it,
                        network_interfaces=interfaces,
                        key_name=r.name
                    )
                    print 'reservation:', reservation.id, reservation.instances
                    while not has_instance:
                        print 'waiting instance'
                        time.sleep(10)
                        for instance in r_conn.get_only_instances(instance_ids=[reservation.instances[0].id]):
                            print 'instance:', instance.id, 'state:', instance.state
                            has_instance = True                            
                            instance.add_tag('App', app_util.app_name)
                            
                except Exception as e:                    
                    if e.error_code == 'InvalidKeyPair.NotFound':
                        fn = expanduser("~") + '/aws/' + r.name + '.pem'
                        print 'create key pair:', fn
                        pem = r_conn.create_key_pair(r.name)                        
                        with open(fn, 'w') as text_file:
                            print pem.material
                            text_file.write(pem.material)
                        text_file.close()
                        os.chmod(fn, 0400)                                                
                    else:
                        print 'exception:', e
        else:
            print 'no ami for:', r.name
            
if __name__ == '__main__':
    reactor.callWhenRunning(replicate)
    reactor.run()
    