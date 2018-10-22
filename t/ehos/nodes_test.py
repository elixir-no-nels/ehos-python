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
    
