import pytest

import ehos.instances_db as I
#import ehos.tyt

import sys
print(sys.modules['ehos.instances_db'] )
print( I )

url = 'postgresql://postgres:docker@127.0.0.1:5432/ehos'


def test_init():

    i = I.InstancesDB( url )

    assert i.node_list() == {}


def test_add_cloud():

    i = I.InstancesDB( url )


    a = i._get_cloud_id('cloud_1')
    b = i._get_cloud_id('cloud_2')

    assert a == i._get_cloud_id('cloud_1')
    assert b == i._get_cloud_id('cloud_2')
    

    
    
def test_add_state():

    i = I.InstancesDB( url )


    a = i._get_state_id('state_1')
    b = i._get_state_id('state_2')

    assert a == i._get_state_id('state_1')
    assert b == i._get_state_id('state_2')
    

def test_add_status():

    i = I.InstancesDB( url )


    a = i._get_status_id('status_1')
    b = i._get_status_id('status_2')

    assert a == i._get_status_id('status_1')
    assert b == i._get_status_id('status_2')

    
    
def test_add_node():


    i = I.InstancesDB( url )


    i._add_node_to_db(id='id1', name='name1', cloud='uh1', state='booting', status='starting')


    

def test_update_node():

    i = I.InstancesDB( url )


    i._add_node_to_db(id='id2', name='name2', cloud='uh1', state='booting', status='starting')

    i._update_node(uuid='id2', state='changed_state')
    i._update_node(uuid='id2', status='changed_status')
    
