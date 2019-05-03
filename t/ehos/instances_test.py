import pytest
from unittest.mock import Mock, patch


import ehos.instances as I
import ehos
#import ehos.tyt

import sys
print(sys.modules['ehos.instances'] )
print( I )

db_name = 'ehos_testing'
url = "postgresql://ehos:ehos@127.0.0.1:5432/{db_name}".format( db_name=db_name )


def test_init():

    i = I.Instances()

    assert i._nodes == {}



def test_connect_disconnect():
    i = I.Instances()
    i.connect( url )
    i.disconnect()

def test_add_cloud():
    i = I.Instances() 

    i.add_cloud(name='cph', instance='12345')


def test_add_cloud_002():
    i = I.Instances()
    i.connect( url )

    i.add_cloud(name='cph', instance='12345')


def test_add_cloud_dup():
    i = I.Instances() 

    i.add_cloud(name='cph', instance='12345')
    
    with pytest.raises( RuntimeError ):
        i.add_cloud(name='cph', instance='12345')

    
def test_get_cloud():
    i = I.Instances() 

    i.add_cloud(name='cph', instance='12345')
    i.add_cloud(name='osl', instance='56789')
    
    c = i.get_cloud('cph')
    assert c == '12345'

def test_add_clouds():
    i = I.Instances()
    i.add_clouds({'a':123, 'b':456})
    assert i.clouds() ==  {'a':123, 'b':456}




def test_get_cloud_unknown():
    i = I.Instances() 

    i.add_cloud(name='cph', instance='12345')
    i.add_cloud(name='osl', instance='56789')
    
    with pytest.raises( RuntimeError ):
        i.get_cloud('bgn')

def test_get_cloud_names():
    i = I.Instances() 

    i.add_cloud(name='cph', instance='12345')
    i.add_cloud(name='osl', instance='56789')
    
    names = i.cloud_names()
    assert names ==  ['cph', 'osl']


def test_get_cloud_names_empty():
    i = I.Instances() 

    names = i.cloud_names()
    assert names ==  []
    
def test_get_clouds():
    i = I.Instances() 

    i.add_cloud(name='cph', instance='12345')
    i.add_cloud(name='osl', instance='56789')
    
    names = i.clouds()
    assert names ==  {'cph':'12345', 'osl':'56789'}
    
    
def test_add_node():
    i = I.Instances() 
    
    i.add_cloud(name='tyt', instance='12345')

    i.add_node( '123', name = 'qwerty', cloud='tyt')
    
    assert i._nodes[ '123'][ 'name'] == 'qwerty'
    assert i._nodes[ '123'][ 'cloud'] == 'tyt'
    assert i._nodes[ '123'][ 'node_state'] == 'node_starting'


def test_add_node_002():
    i = I.Instances()
    i.connect( url )

    i.add_cloud(name='tyt', instance='12345')

    i.add_node( '123', name = 'qwerty', cloud='tyt')

    assert i._nodes[ '123'][ 'name'] == 'qwerty'
    assert i._nodes[ '123'][ 'cloud'] == 'tyt'
    assert i._nodes[ '123'][ 'node_state'] == 'node_starting'


def test_add_node_duplicate_id():
    i = I.Instances() 
    
    i.add_cloud(name='tyt', instance='12345')
    i.add_node( '123', name = 'qwerty2', cloud='tyt')

    with pytest.raises( RuntimeError ):
        i.add_node( '123', name = 'qwerty2', cloud='tyt')


def test_add_node_duplicate_name():
    i = I.Instances() 
    
    i.add_cloud(name='tyt', instance='12345')
    i.add_node( '1234', name = 'qwerty2', cloud='tyt')

    with pytest.raises( RuntimeError ):
        i.add_node( '123', name = 'qwerty2', cloud='tyt')

def test_add_node_unknown_cloud():
    i = I.Instances() 
    
    i.add_cloud(name='tyt', instance='12345')
    i.add_node( '1234', name = 'qwerty2', cloud='tyt')

    with pytest.raises( RuntimeError ):
        i.add_node( '123', name = 'qwerty2', cloud='tytss')


def test_add_node_unknown_illegal_state():
    i = I.Instances() 
    
    i.add_cloud(name='tyt', instance='12345')

    with pytest.raises( RuntimeError ):
        i.add_node( '123', name = 'qwerty2', cloud='tyt', vm_state='bla')

def test_add_node_unknown_illegal_node_state():
    i = I.Instances() 
    
    i.add_cloud(name='tyt', instance='12345')

    with pytest.raises( RuntimeError ):
        i.add_node( '123', name = 'qwerty2', cloud='tyt', node_state='bla')
        
        

def test_get_node():
    i = I.Instances() 

    i.add_cloud(name='tyt', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')

    i.add_node( '123_1', name = 'qwerty1', cloud='tyt', node_state='node_idle')
    i.add_node( '123_2', name = 'qwerty2', cloud='tyt')
    i.add_node( '123_3', name = 'qwerty3', cloud='tyt2')

    node = i.get_node('123_1')
    print( node )
    
    assert node == {'id':'123_1', 'name': 'qwerty1', 'cloud':'tyt', 'node_state':'node_idle', 'vm_state':'vm_booting'}

    
def test_get_node_ids():
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')


    i.add_node( '123_1', name = 'qwerty11', cloud='tyt1', node_state="node_busy")
    i.add_node( '123_2', name = 'qwerty12', cloud='tyt2', node_state="node_busy")
    i.add_node( '123_3', name = 'qwerty13', cloud='tyt3', node_state="node_busy")

    
    nodes = i.get_node_ids()
    
    assert nodes == ['123_1','123_2','123_3']

def test_get_node_names():
    i = I.Instances() 

    i.add_cloud(name='tyt', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')

    i.add_node( '123_1', name = 'qwerty1', cloud='tyt')
    i.add_node( '123_2', name = 'qwerty2', cloud='tyt')
    i.add_node( '123_3', name = 'qwerty3', cloud='tyt2')

    nodes = i.get_node_names()
    
    assert nodes == ['qwerty1','qwerty2','qwerty3']


def test_get_node_names_by_state(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")

      
    nodes = i.get_node_names(vm_state='vm_booting')

    assert nodes == ['qwerty11']


    
def test_get_node_names_by_node_state(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")
      
    nodes = i.get_node_names(node_state='node_idle')

    assert nodes == ['qwerty11']

    

def test_get_node_names_by_cloud(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")

      
    nodes = i.get_node_names(cloud='tyt2')

    assert nodes == ['qwerty12']
        
    
    

def test_get_node_unknown_id():
    i = I.Instances() 
    
    i.add_cloud(name='tyt', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')

    i.add_node( '1234', name = 'qwerty2', cloud='tyt')
    i.add_node( '123_2', name = 'qwerty22', cloud='tyt')
    i.add_node( '123_3', name = 'qwerty32', cloud='tyt2')

    with pytest.raises( RuntimeError ):
        node = i.get_node('123_10')
    

def test_get_nodes_all(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', node_state="node_suspended")

      
    nodes = i.get_nodes()

    assert nodes == [{'cloud': 'tyt1', 'id': '123_11', 'name': 'qwerty11', 'vm_state': 'vm_booting', 'node_state': 'node_idle'},
                     {'cloud': 'tyt2', 'id': '123_12', 'name': 'qwerty12', 'vm_state': 'vm_booting', 'node_state': 'node_busy'},
                     {'cloud': 'tyt3', 'id': '123_13', 'name': 'qwerty13', 'vm_state': 'vm_booting', 'node_state': 'node_suspended'}]



def test_get_nodes_by_state():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")


    nodes = i.get_nodes(vm_state=['vm_booting'])

    assert nodes == [{'cloud': 'tyt1', 'id': '123_11', 'name': 'qwerty11', 'vm_state': 'vm_booting', 'node_state': 'node_idle'},]


def test_get_nodes_illegal_state():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")


    with pytest.raises( RuntimeError ):
        nodes = i.get_nodes(vm_state=['bootings'])



def test_get_nodes_node_state():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")

    nodes = i.get_nodes(node_state=['node_idle'])

    assert nodes == [{'cloud': 'tyt1', 'id': '123_11', 'name': 'qwerty11', 'vm_state': 'vm_booting', 'node_state': 'node_idle'}]


def test_get_nodes_illegal_node_state():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")


    with pytest.raises( RuntimeError ):
        nodes = i.get_nodes(node_state=['nay'])



def test_get_nodes_cloud():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")



    nodes = i.get_nodes(cloud=['tyt2'])

    assert nodes == [{'cloud': 'tyt2', 'id': '123_12', 'name': 'qwerty12', 'vm_state': 'vm_active', 'node_state': 'node_busy'}]


def test_get_nodes_unknown_cloud():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")


    with pytest.raises( RuntimeError ):
        nodes = i.get_nodes(cloud=['aws'])


def test_get_nodes_names():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")

    nodes = i.get_nodes(node_state=['node_idle'])

    assert nodes == [{'cloud': 'tyt1', 'id': '123_11', 'name': 'qwerty11', 'vm_state': 'vm_booting', 'node_state': 'node_idle'}]






def test_get_node_ids_by_state():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")


    nodes = i.get_node_ids(vm_state='vm_booting')

    assert nodes == ['123_11']



def test_get_node_ids_by_node_state():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")

    nodes = i.get_node_ids(node_state='node_idle')

    assert nodes == ['123_11']



def test_get_node_ids_by_cloud():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', vm_state='vm_suspended', node_state="node_suspended")


    nodes = i.get_node_ids(cloud='tyt2')

    assert nodes == ['123_12']




def test_get_node_ids_filtered_empty():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    nodes = i.get_node_ids(node_state='node_retiring')

    assert nodes == []



def test_node_name2id():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    assert i.vm_name2id('qwerty21') == '123_21'

def test_node_name2id_unknown():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    with pytest.raises( RuntimeError ):
        i.vm_name2id('qwerty213')

def test_get_node_id2name():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    assert i.vm_id2name('123_21') == 'qwerty21'

def test_node_id2name_unknown():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    with pytest.raises( RuntimeError ):
        i.vm_id2name('123_91') == 'qwerty213'



def test_nodes_in_cloud():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    print( i.nodes_in_cloud('tyt3') )

    assert sorted(i.nodes_in_cloud('tyt3')) == sorted(['123_23', '123_13'])


def test_nodes_in_cloud_empty():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    assert i.nodes_in_cloud('tyt4') == []



def test_node_state_counts( ):
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')


    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle", vm_state='vm_active')
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_busy", vm_state='vm_active')
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt2', node_state="node_benchmarking", vm_state='vm_active')
    i.add_node( '123_24', name = 'qwerty24', cloud='tyt1', node_state="node_starting", vm_state='vm_booting')
    i.add_node( '123_25', name = 'qwerty25', cloud='tyt1', node_state="node_vacating", vm_state='vm_unknown')
    i.add_node( '123_26', name = 'qwerty26', cloud='tyt1', node_state="node_lost", vm_state='vm_booting')

    assert i.node_state_counts()['all'] == {'node_idle': 1, 'node_busy': 3, 'node_other': 1, 'node_total': 4}
    assert i.node_state_counts() == {'all': {'node_busy': 3, 'node_idle': 1, 'node_other': 1, 'node_total': 4},
                                     'tyt1': {'node_busy': 1, 'node_idle': 1, 'node_other': 1, 'node_total': 2},
                                     'tyt2': {'node_busy': 2, 'node_idle': 0, 'node_other': 0, 'node_total': 2}}





def test_set_state():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt1', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt1', vm_state='vm_suspended', node_state="node_suspended")


    nodes = i.set_vm_state('123_12', 'vm_deleted')

    assert i._nodes[ '123_12']['vm_state'] == 'vm_deleted'


def test_set_state_unknown():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt1', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt1', vm_state='vm_suspended', node_state="node_suspended")


    with pytest.raises( RuntimeError ):
        nodes = i.set_vm_state('123_12', 'bla')

def test_set_state_unknown_node():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt1', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt1', vm_state='vm_suspended', node_state="node_suspended")


    with pytest.raises( RuntimeError ):
        nodes = i.set_vm_state('12ss3_12', 'bladsfsdf')

def test_set_state_same():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt1', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt1', vm_state='vm_suspended', node_state="node_suspended")

    nodes = i.set_vm_state('123_12', 'vm_active')

    assert i._nodes[ '123_12']['vm_state'] == 'vm_active'


def test_get_vm_state():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt1', vm_state='vm_active', node_state="node_busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt1', vm_state='vm_suspended', node_state="node_suspended")


    assert i.vm_state('123_12') == 'vm_active'


def test_get_state_unknown_node():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', vm_state='vm_booting', node_state="node_idle")

    with pytest.raises( RuntimeError ):
        i.vm_state('123d_11')





def test_set_node_state():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    i.set_node_state( '123_22', 'node_busy')

    assert i._nodes[ '123_22']['node_state'] == 'node_busy'

def test_set_node_state_unknown_node():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')

    with pytest.raises( RuntimeError ):
        i.set_node_state( '123_23', 'yt')


def test_set_node_state_illegal_node_state():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')

    with pytest.raises( RuntimeError ):
        i.set_node_state( '123_11', 'yt')


def test_get_node_state():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    i.set_node_state( '123_23','node_idle')
    assert i.get_node_state('123_23') == 'node_idle'




def test_get_node_state_unknown():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')

    with pytest.raises( RuntimeError ):
        i.get_node_state( '123_23dd')



def test_find_id():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    assert i.find( id='123_23') == {'cloud': 'tyt3',
                                    'id': '123_23',
                                    'name': 'qwerty23',
                                    'vm_state': 'vm_booting',
                                    'node_state': 'node_idle'}


def test_find_name():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')


    assert i.find( name='not-there') == None



def test_find_name_002():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    print( i.find( name='qwerty23') )


    assert i.find( name='qwerty23') == {'cloud': 'tyt3',
                                        'id': '123_23',
                                        'name': 'qwerty23',
                                        'vm_state': 'vm_booting',
                                        'node_state': 'node_idle'}


def test_find_name_002():
    i = I.Instances()

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')


    assert i.find( ) == None


def test_find_id_wrong(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    assert i.find( id='does_not_exist') == None

    
def test_find_name_wrong(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', node_state="node_idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', node_state="node_idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', node_state="node_idle")

    assert i.find( id='does_not_exist') == None



def fake_vm_list(clouds):
    '''
        node_idle         =  1
        node_starting     =  2
        node_busy         =  3
        node_suspended    =  4
        node_vacating     =  5
        node_killing      =  6
        node_benchmarking =  7
        node_retiring     =  8
        node_lost         =  9

        vm_booting = 1
        vm_active = 2
        vm_suspended = 3
        vm_restarting = 4
        vm_stopping = 5
        vm_deleted = 6
        vm_unknown = 7
    '''

    vms = { 'uuid_1':{'name':'n1', 'cloud_name':'bgo', 'id':'uuid_1', 'vm_state':'vm_booting',    'node_state':'node_idle'},
            'uuid_2':{'name':'n2', 'cloud_name':'bgo', 'id':'uuid_2', 'vm_state':'vm_active',     'node_state':'node_starting'},
            'uuid_3':{'name':'n3', 'cloud_name':'osl', 'id':'uuid_3', 'vm_state':'vm_suspended',  'node_state':'node_idle'},
            'uuid_4':{'name':'n4', 'cloud_name':'osl', 'id':'uuid_4', 'vm_state':'vm_restarting', 'node_state':'node_idle'},
            'uuid_5':{'name':'n5', 'cloud_name':'osl', 'id':'uuid_5', 'vm_state':'vm_stopping',   'node_state':'node_idle'},
            'uuid_6':{'name':'n6', 'cloud_name':'osl', 'id':'uuid_6', 'vm_state':'vm_deleted',    'node_state':'node_idle'},
            'uuid_7':{'name':'n7', 'cloud_name':'osl', 'id':'uuid_7', 'vm_state':'vm_unknown',    'node_state':'node_idle'},
            'uuid_8':{'name':'n8', 'cloud_name':'osl', 'id':'uuid_8', 'vm_state':'vm_unknown',    'node_state':'node_idle'},
            }



    return vms



@patch.object(ehos, 'vm_list', fake_vm_list)
def test_update_000():
    i = I.Instances()
    i.add_cloud(name='bgo', instance='12345')
    i.add_node( id='uuid_2', name = 'n2', cloud='bgo', vm_state='vm_active', node_state='node_idle')

    nodes = {'not_ehos':'node_bla bla bla'}

    i.update(nodes = nodes)
    assert i.get_nodes() == [{'cloud': 'bgo',
                              'id': 'uuid_2',
                              'name': 'n2',
                              'node_state': 'node_idle',
                              'vm_state': 'vm_active'}]


@patch.object(ehos, 'vm_list', fake_vm_list)
def test_update_001():
    i = I.Instances()
    i.add_cloud(name='bgo', instance='12345')
    i.add_node( id='uuid_2', name = 'n2', cloud='bgo', vm_state='vm_active', node_state='node_idle')

    nodes = {'n2':"node_busy"}

    i.update(nodes = nodes)
    assert i.get_nodes() == [{'cloud': 'bgo',
                              'id': 'uuid_2',
                              'name': 'n2',
                              'node_state': 'node_busy',
                              'vm_state': 'vm_active'}]


@patch.object(ehos, 'vm_list', fake_vm_list)
def test_update_002():
    i = I.Instances()
    i.add_cloud(name='bgo', instance='12345')
    i.add_node( id='uuid_99', name = 'n99', cloud='bgo', vm_state='vm_active', node_state='node_idle')

    nodes = {'n2':"node_busy"}

    i.update(nodes = nodes)
    print( i.get_nodes())
    assert i.get_nodes() == [{'cloud': 'bgo',
                              'id': 'uuid_99',
                              'name': 'n99',
                              'node_state': 'node_lost',
                              'vm_state': 'vm_deleted'},
                             {'cloud': 'bgo',
                              'id': 'uuid_2',
                              'name': 'n2',
                              'node_state': 'node_busy',
                              'vm_state': 'vm_active'},
                             ]



@patch.object(ehos, 'vm_list', fake_vm_list)
def test_update_003():
    i = I.Instances()
    i.add_cloud(name='bgo', instance='12345')
    i.add_node( id='uuid_1', name = 'n1', cloud='bgo', vm_state='vm_active', node_state='node_idle')

    nodes = {'n1':"node_busy"}

    print( i._nodes)

    i.update(nodes = nodes)
    assert i.get_nodes() == [{'cloud': 'bgo',
                              'id': 'uuid_1',
                              'name': 'n1',
                              'node_state': 'node_busy',
                              'vm_state': 'vm_active'}]

@patch.object(ehos, 'vm_list', fake_vm_list)
def test_update_004():
    i = I.Instances()
    i.add_cloud(name='bgo', instance='12345')
    i.add_node( id='uuid_1', name = 'n1', cloud='bgo', vm_state='vm_active', node_state='node_idle')

    nodes = {'n1':"node_suspended"}

    print( i._nodes)

    i.update(nodes = nodes)
    assert i.get_nodes() == [{'cloud': 'bgo',
                              'id': 'uuid_1',
                              'name': 'n1',
                              'node_state': 'node_lost',
                              'vm_state': 'vm_deleted'}]

@patch.object(ehos, 'vm_list', fake_vm_list)
def test_update_005():
    i = I.Instances()
    i.add_cloud(name='bgo', instance='12345')
    i.add_node( id='uuid_1', name = 'n1', cloud='bgo', vm_state='vm_booting', node_state='node_starting')

    nodes = {'n1':"node_idle"}

    print( i._nodes)

    i.update(nodes = nodes)
    assert i.get_nodes() == [{'cloud': 'bgo',
                              'id': 'uuid_1',
                              'name': 'n1',
                              'node_state': 'node_idle',
                              'vm_state': 'vm_active'}]
