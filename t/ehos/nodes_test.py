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
        

def test_get_nodes():
    n = N.Nodes() 
    nodes = print( n.get_nodes())

    n.add( '123_1', name = 'qwerty1', cloud='tyt')
    n.add( '123_2', name = 'qwerty2', cloud='tyt')
    n.add( '123_3', name = 'qwerty3', cloud='tyt2')

    nodes = n.get_nodes()
    
    assert nodes == ['123_1','123_2','123_3']
