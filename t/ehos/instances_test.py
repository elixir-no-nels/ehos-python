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
    
def test_get_clouds():
    i = I.Instances() 

    i.add_cloud(name='cph', instance='12345')
    i.add_cloud(name='osl', instance='56789')
    
    names = i.get_clouds()
    assert names ==  {'cph':'12345', 'osl':'56789'}
    
    
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
        i.add_node( '123', name = 'qwerty2', cloud='tyt', state='bla')

def test_add_node_unknown_illegal_status():
    i = I.Instances() 
    
    i.add_cloud(name='tyt', instance='12345')

    with pytest.raises( RuntimeError ):
        i.add_node( '123', name = 'qwerty2', cloud='tyt', status='bla')
        
        

def test_get_node():
    i = I.Instances() 

    i.add_cloud(name='tyt', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')

    i.add_node( '123_1', name = 'qwerty1', cloud='tyt', status='idle')
    i.add_node( '123_2', name = 'qwerty2', cloud='tyt')
    i.add_node( '123_3', name = 'qwerty3', cloud='tyt2')

    node = i.get_node('123_1')
    print( node )
    
    assert node == {'id':'123_1', 'name': 'qwerty1', 'cloud':'tyt', 'status':'idle', 'state':'booting'}

    
def test_get_node_ids():
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')


    i.add_node( '123_1', name = 'qwerty11', cloud='tyt1', status="busy")
    i.add_node( '123_2', name = 'qwerty12', cloud='tyt2', status="busy")
    i.add_node( '123_3', name = 'qwerty13', cloud='tyt3', status="busy")

    
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

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")

      
    nodes = i.get_node_names(state='booting')

    assert nodes == ['qwerty11']


    
def test_get_node_names_by_status(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")
      
    nodes = i.get_node_names(status='idle')

    assert nodes == ['qwerty11']

    

def test_get_node_names_by_cloud(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")

      
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

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', status="suspended")

      
    nodes = i.get_nodes()

    assert nodes == [{'cloud': 'tyt1', 'id': '123_11', 'name': 'qwerty11', 'state': 'booting', 'status': 'idle'},
                     {'cloud': 'tyt2', 'id': '123_12', 'name': 'qwerty12', 'state': 'booting', 'status': 'busy'},
                     {'cloud': 'tyt3', 'id': '123_13', 'name': 'qwerty13', 'state': 'booting', 'status': 'suspended'}]
        


def test_get_nodes_by_state(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")

      
    nodes = i.get_nodes(state=['booting'])

    assert nodes == [{'cloud': 'tyt1', 'id': '123_11', 'name': 'qwerty11', 'state': 'booting', 'status': 'idle'},]


def test_get_nodes_illegal_state(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")

      
    with pytest.raises( RuntimeError ):
        nodes = i.get_nodes(state=['bootings'])


    
def test_get_nodes_status(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")
      
    nodes = i.get_nodes(status=['idle'])

    assert nodes == [{'cloud': 'tyt1', 'id': '123_11', 'name': 'qwerty11', 'state': 'booting', 'status': 'idle'}]


def test_get_nodes_illegal_status(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")

      
    with pytest.raises( RuntimeError ):
        nodes = i.get_nodes(status=['nay'])

    

def test_get_nodes_cloud(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")


      
    nodes = i.get_nodes(cloud=['tyt2'])

    assert nodes == [{'cloud': 'tyt2', 'id': '123_12', 'name': 'qwerty12', 'state': 'active', 'status': 'busy'}]
        

def test_get_nodes_unknown_cloud(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")

      
    with pytest.raises( RuntimeError ):
        nodes = i.get_nodes(cloud=['aws'])

    
def test_get_nodes_names(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")
      
    nodes = i.get_nodes(status=['idle'])

    assert nodes == [{'cloud': 'tyt1', 'id': '123_11', 'name': 'qwerty11', 'state': 'booting', 'status': 'idle'}]


        
        
        

def test_get_node_ids_by_state(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")

      
    nodes = i.get_node_ids(state='booting')

    assert nodes == ['123_11']


    
def test_get_node_ids_by_status(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")
      
    nodes = i.get_node_ids(status='idle')

    assert nodes == ['123_11']

    

def test_get_node_ids_by_cloud(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3', state='suspended', status="suspended")

      
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

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")

    nodes = i.get_node_ids(status='retiring')

    assert nodes == []



def test_node_name2id(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")
    
    assert i.name2id('qwerty21') == '123_21'

def test_node_name2id_unknown(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")
    
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

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")
    
    assert i.id2name('123_21') == 'qwerty21'

def test_node_id2name_unknown(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")
    
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

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")

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

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")

    assert i.nodes_in_cloud('tyt4') == []
    


def test_node_state_counts( ):
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')


    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle", state='active')
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="busy", state='active')
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt2', status="benchmarking", state='active')
    i.add_node( '123_24', name = 'qwerty24', cloud='tyt1', status="starting", state='booting')
    i.add_node( '123_25', name = 'qwerty25', cloud='tyt1', status="vacating", state='unknown')
    i.add_node( '123_26', name = 'qwerty26', cloud='tyt1', status="lost", state='booting')

    assert i.node_state_counts()['all'] == {'idle': 1, 'busy': 3, 'other': 1, 'total': 4}
    assert i.node_state_counts() == {'all': {'busy': 3, 'idle': 1, 'other': 1, 'total': 4},
                                     'tyt1': {'busy': 1, 'idle': 1, 'other': 1, 'total': 2},
                                     'tyt2': {'busy': 2, 'idle': 0, 'other': 0, 'total': 2}}




    
def test_set_state(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt1', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt1', state='suspended', status="suspended")

      
    nodes = i.set_state('123_12', 'deleted')

    assert i._nodes[ '123_12']['state'] == 'deleted'


def test_set_state_unknown(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt1', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt1', state='suspended', status="suspended")

      
    with pytest.raises( RuntimeError ):
        nodes = i.set_state('123_12', 'bla')

def test_set_state_unknown_node(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt1', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt1', state='suspended', status="suspended")

      
    with pytest.raises( RuntimeError ):
        nodes = i.set_state('12ss3_12', 'bla')
        
def test_set_state_same(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt1', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt1', state='suspended', status="suspended")

    nodes = i.set_state('123_12', 'active')

    assert i._nodes[ '123_12']['state'] == 'active'


def test_get_state(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt1', state='active', status="busy")
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt1', state='suspended', status="suspended")
    

    assert i.get_state( '123_12') ==  'active'
    

def test_get_state_unknown_node(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1', state='booting', status="idle")

    with pytest.raises( RuntimeError ):
        i.get_state( '123d_11')
    
    

    
        
def test_set_status(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")

    i.set_status( '123_22', 'busy')
    
    assert i._nodes[ '123_22']['status'] == 'busy'
    
def test_set_status_unknown_node(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')

    with pytest.raises( RuntimeError ):
        i.set_status( '123_23', 'yt')
    

def test_set_status_illegal_status(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')

    with pytest.raises( RuntimeError ):
        i.set_status( '123_11', 'yt')
    
        
def test_get_status(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")

    i.set_status( '123_23','idle')
    assert i.get_status('123_23') == 'idle'



    
def test_get_status_unknown(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')

    with pytest.raises( RuntimeError ):
        i.get_status( '123_23dd')
    


def test_find_id(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")

    assert i.find( id='123_23') == {'cloud': 'tyt3',
                                    'id': '123_23',
                                    'name': 'qwerty23',
                                    'state': 'booting',
                                    'status': 'idle'}


def test_find_name(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")

    print( i.find( name='qwerty23') )

    
    assert i.find( name='qwerty23') == {'cloud': 'tyt3',
                                        'id': '123_23',
                                        'name': 'qwerty23',
                                        'state': 'booting',
                                        'status': 'idle'}


def test_find_id_wrong(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")

    assert i.find( id='does_not_exist') == None

    
def test_find_name_wrong(): 
    i = I.Instances() 

    i.add_cloud(name='tyt1', instance='12345')
    i.add_cloud(name='tyt2', instance='12345')
    i.add_cloud(name='tyt3', instance='12345')

    i.add_node( '123_11', name = 'qwerty11', cloud='tyt1')
    i.add_node( '123_12', name = 'qwerty12', cloud='tyt2')
    i.add_node( '123_13', name = 'qwerty13', cloud='tyt3')

    i.add_node( '123_21', name = 'qwerty21', cloud='tyt1', status="idle")
    i.add_node( '123_22', name = 'qwerty22', cloud='tyt2', status="idle")
    i.add_node( '123_23', name = 'qwerty23', cloud='tyt3', status="idle")

    assert i.find( id='does_not_exist') == None
    
    
    

