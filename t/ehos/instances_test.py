import pytest

import ehos.instances as I


def test_init():

    i = I.Instances() 

    assert i._nodes == {}


def test_add_cloud():
    i = I.Instances() 

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
    
    names = i.get_cloud_names()
    assert names ==  ['cph', 'osl']


def test_get_cloud_names_empty():
    i = I.Instances() 

    names = i.get_cloud_names()
    assert names ==  []
    
    
    
def test_add_node():
    i = I.Instances() 
    
    i.add_cloud(name='tyt', instance='12345')

    i.add_node( '123', name = 'qwerty', cloud='tyt')
    
    assert i._nodes[ '123'][ 'name'] == 'qwerty'
    assert i._nodes[ '123'][ 'cloud'] == 'tyt'
    assert i._nodes[ '123'][ 'status'] == 'starting'
    

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


def test_get_node():
    i = I.Instances() 

    i.add_cloud(name='tyt', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')

    i.add_node( '123_1', name = 'qwerty1', cloud='tyt', status='running')
    i.add_node( '123_2', name = 'qwerty2', cloud='tyt')
    i.add_node( '123_3', name = 'qwerty3', cloud='tyt2')

    node = i.get_node('123_1')
    print( node )
    
    assert node == {'id':'123_1', 'name': 'qwerty1', 'cloud':'tyt', 'status':'running'}

    
def test_get_node_ids():
    i = I.Instances() 

    i.add_cloud(name='tyt', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')

    i.add_node( '123_1', name = 'qwerty1', cloud='tyt')
    i.add_node( '123_2', name = 'qwerty2', cloud='tyt')
    i.add_node( '123_3', name = 'qwerty3', cloud='tyt2')

    nodes = i.get_node_ids()
    
    assert nodes == ['123_1','123_2','123_3']


def test_get_node_unknown_id():
    i = I.Instances() 
    
    i.add_cloud(name='tyt', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')

    i.add_node( '1234', name = 'qwerty2', cloud='tyt')
    i.add_node( '123_2', name = 'qwerty22', cloud='tyt')
    i.add_node( '123_3', name = 'qwerty32', cloud='tyt2')

    with pytest.raises( RuntimeError ):
        node = i.get_node('123_10')
    

def test_get_node_ids_filtered(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")
      
    nodes = i.get_node_ids(status='running')

    assert nodes == ['123_21','123_22','123_23']


def test_get_node_ids_filtered_empty(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    nodes = i.get_node_ids(status='stopped')

    assert nodes == []



def test_node_name2id(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")
    
    assert i.name2id('qwerty21') == '123_21'

def test_node_name2id_unknown(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")
    
    with pytest.raises( RuntimeError ):
        i.name2id('qwerty213')

def test_get_node_id2name(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")
    
    assert i.id2name('123_21') == 'qwerty21'

def test_node_id2name_unknown(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")
    
    with pytest.raises( RuntimeError ):
        i.id2name('123_91') == 'qwerty213'
        


def test_nodes_in_cloud(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

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

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    assert i.nodes_in_cloud('tyt4') == []
    

def test_set_status(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    i.set_status( '123_22', 'changed')
    
    assert i._nodes[ '123_22']['status'] == 'changed'
    
    

def test_set_status(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    assert i.get_status( '123_23') == 'running'



def test_find_id(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    assert i.find( id='123_23') == ('123_23', 'qwerty23', 'tyt3', "running")

def test_find_name(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    print( i.find( name='qwerty23') )

    
    assert i.find( name='qwerty23') == ('123_23', 'qwerty23', 'tyt3', "running")


def test_find_id_wrong(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    with pytest.raises( RuntimeError ):
        i.find( name='does_not_exist')

    
def test_find_name_wrong(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    with pytest.raises( RuntimeError ):
        i.find( name='qwerty231')
    
    
    

