import pytest

import ehos.instances as I
#import ehos.tyt

import sys
print(sys.modules['ehos.instances'] )
print( I )


def test_init():

    i = I.Instances()

    assert i._nodes == {}


def test_add_cloud():

    i = I.Instances()

    i.connect( url='postgresql://ehos:ehos@127.0.0.1:5432/ehos_instances')

    a = i._get_cloud_id('cloud_1')
    b = i._get_cloud_id('cloud_2')

    assert a == i._get_cloud_id('cloud_1')
    assert b == i._get_cloud_id('cloud_2')
    

    
    
def test_add_state():

    i = I.Instances()

    i.connect( url='postgresql://ehos:ehos@127.0.0.1:5432/ehos_instances')

    a = i._get_state_id('state_1')
    b = i._get_state_id('state_2')

    assert a == i._get_state_id('state_1')
    assert b == i._get_state_id('state_2')
    

def test_add_status():

    i = I.Instances()

    i.connect( url='postgresql://ehos:ehos@127.0.0.1:5432/ehos_instances')

    a = i._get_status_id('status_1')
    b = i._get_status_id('status_2')

    assert a == i._get_status_id('status_1')
    assert b == i._get_status_id('status_2')

    
    
def test_add_node():


    i = I.Instances()

    i.connect( url='postgresql://ehos:ehos@127.0.0.1:5432/ehos_instances')

    i._add_node_to_db(id='id1', name='name1', cloud='uh1', state='booting', status='starting')


    

def test_update_node():

    i = I.Instances()

    i.connect( url='postgresql://ehos:ehos@127.0.0.1:5432/ehos_instances')

    i._add_node_to_db(id='id2', name='name2', cloud='uh1', state='booting', status='starting')

    i._update_node(id='id2', state='changed_state')
    i._update_node(id='id2', status='changed_status')
    
