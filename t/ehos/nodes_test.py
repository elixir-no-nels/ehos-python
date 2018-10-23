import pytest

import ehos.nodes as N



def test_init():

    n = N.Nodes() 

    assert n._nodes == {}


def test_add_node():
    n = N.Nodes() 
    
    n.add( '123', name = 'qwerty', cloud='tyt')
    
    assert n._nodes[ '123'][ 'name'] == 'qwerty'
    assert n._nodes[ '123'][ 'cloud'] == 'tyt'
    assert n._nodes[ '123'][ 'status'] == 'starting'
    

def test_add_node_duplicate_id():
    n = N.Nodes() 
    
    n.add( '123', name = 'qwerty2', cloud='tyt')

    with pytest.raises( RuntimeError ):
        n.add( '123', name = 'qwerty2', cloud='tyt')


def test_add_node_duplicate_name():
    n = N.Nodes() 
    
    n.add( '1234', name = 'qwerty2', cloud='tyt')

    with pytest.raises( RuntimeError ):
        n.add( '123', name = 'qwerty2', cloud='tyt')


def test_get_node():
    n = N.Nodes() 

    n.add( '123_1', name = 'qwerty1', cloud='tyt', status='running')
    n.add( '123_2', name = 'qwerty2', cloud='tyt')
    n.add( '123_3', name = 'qwerty3', cloud='tyt2')

    node = n.get_node('123_1')
    print( node )
    
    assert node == {'name': 'qwerty1', 'cloud':'tyt', 'status':'running'}

def test_get_clouds(): 
    n = N.Nodes() 

    n.add( '123_11', name = 'qwerty11', cloud='tyt1')
    n.add( '123_12', name = 'qwerty12', cloud='tyt2')
    n.add( '123_13', name = 'qwerty13', cloud='tyt3')

    n.add( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    n.add( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    n.add( '123_23', name = 'qwerty23', cloud='tyt3', status="running")
      
    clouds = n.get_clouds()

    assert clouds == ['tyt1','tyt2','tyt3']
    
    
def test_get_node_ids():
    n = N.Nodes() 

    n.add( '123_1', name = 'qwerty1', cloud='tyt')
    n.add( '123_2', name = 'qwerty2', cloud='tyt')
    n.add( '123_3', name = 'qwerty3', cloud='tyt2')

    nodes = n.get_node_ids()
    
    assert nodes == ['123_1','123_2','123_3']


def test_get_node_unknown_id():
    n = N.Nodes() 
    
    n.add( '1234', name = 'qwerty2', cloud='tyt')
    n.add( '123_2', name = 'qwerty22', cloud='tyt')
    n.add( '123_3', name = 'qwerty32', cloud='tyt2')

    with pytest.raises( RuntimeError ):
        node = n.get_node('123_10')
    

def test_get_node_ids_filtered(): 
    n = N.Nodes() 

    n.add( '123_11', name = 'qwerty11', cloud='tyt1')
    n.add( '123_12', name = 'qwerty12', cloud='tyt2')
    n.add( '123_13', name = 'qwerty13', cloud='tyt3')

    n.add( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    n.add( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    n.add( '123_23', name = 'qwerty23', cloud='tyt3', status="running")
      
    nodes = n.get_node_ids(status='running')

    assert nodes == ['123_21','123_22','123_23']


def test_get_node_ids_filtered_empty(): 
    n = N.Nodes() 

    n.add( '123_11', name = 'qwerty11', cloud='tyt1')
    n.add( '123_12', name = 'qwerty12', cloud='tyt2')
    n.add( '123_13', name = 'qwerty13', cloud='tyt3')

    n.add( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    n.add( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    n.add( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    nodes = n.get_node_ids(status='stopped')

    assert nodes == []



def test_node_name2id(): 
    n = N.Nodes() 

    n.add( '123_11', name = 'qwerty11', cloud='tyt1')
    n.add( '123_12', name = 'qwerty12', cloud='tyt2')
    n.add( '123_13', name = 'qwerty13', cloud='tyt3')

    n.add( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    n.add( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    n.add( '123_23', name = 'qwerty23', cloud='tyt3', status="running")
    
    assert n.name2id('qwerty21') == '123_21'

def test_node_name2id_unknown(): 
    n = N.Nodes() 

    n.add( '123_11', name = 'qwerty11', cloud='tyt1')
    n.add( '123_12', name = 'qwerty12', cloud='tyt2')
    n.add( '123_13', name = 'qwerty13', cloud='tyt3')

    n.add( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    n.add( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    n.add( '123_23', name = 'qwerty23', cloud='tyt3', status="running")
    
    with pytest.raises( RuntimeError ):
        n.name2id('qwerty213')

def test_get_node_id2name(): 
    n = N.Nodes() 

    n.add( '123_11', name = 'qwerty11', cloud='tyt1')
    n.add( '123_12', name = 'qwerty12', cloud='tyt2')
    n.add( '123_13', name = 'qwerty13', cloud='tyt3')

    n.add( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    n.add( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    n.add( '123_23', name = 'qwerty23', cloud='tyt3', status="running")
    
    assert n.id2name('123_21') == 'qwerty21'

def test_node_id2name_unknown(): 
    n = N.Nodes() 

    n.add( '123_11', name = 'qwerty11', cloud='tyt1')
    n.add( '123_12', name = 'qwerty12', cloud='tyt2')
    n.add( '123_13', name = 'qwerty13', cloud='tyt3')

    n.add( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    n.add( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    n.add( '123_23', name = 'qwerty23', cloud='tyt3', status="running")
    
    with pytest.raises( RuntimeError ):
        n.id2name('123_91') == 'qwerty213'
        


def test_nodes_in_cloud(): 
    n = N.Nodes() 

    n.add( '123_11', name = 'qwerty11', cloud='tyt1')
    n.add( '123_12', name = 'qwerty12', cloud='tyt2')
    n.add( '123_13', name = 'qwerty13', cloud='tyt3')

    n.add( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    n.add( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    n.add( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    assert n.nodes_in_cloud('tyt3') == ['123_23', '123_13']


def test_nodes_in_cloud_empty(): 
    n = N.Nodes() 

    n.add( '123_11', name = 'qwerty11', cloud='tyt1')
    n.add( '123_12', name = 'qwerty12', cloud='tyt2')
    n.add( '123_13', name = 'qwerty13', cloud='tyt3')

    n.add( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    n.add( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    n.add( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    assert n.nodes_in_cloud('tyt4') == []
    

def test_set_status(): 
    n = N.Nodes() 

    n.add( '123_11', name = 'qwerty11', cloud='tyt1')
    n.add( '123_12', name = 'qwerty12', cloud='tyt2')
    n.add( '123_13', name = 'qwerty13', cloud='tyt3')

    n.add( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    n.add( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    n.add( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    n.set_status( '123_22', 'changed')
    
    assert n._nodes[ '123_22']['status'] == 'changed'
    
    

def test_set_status(): 
    n = N.Nodes() 

    n.add( '123_11', name = 'qwerty11', cloud='tyt1')
    n.add( '123_12', name = 'qwerty12', cloud='tyt2')
    n.add( '123_13', name = 'qwerty13', cloud='tyt3')

    n.add( '123_21', name = 'qwerty21', cloud='tyt1', status="running")
    n.add( '123_22', name = 'qwerty22', cloud='tyt2', status="running")
    n.add( '123_23', name = 'qwerty23', cloud='tyt3', status="running")

    assert n.get_status( '123_23') == 'running'
    
    
    
