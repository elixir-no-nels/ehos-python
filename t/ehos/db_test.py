import pytest

import ehos.db as ehos_db
import ehos.db_utils as db_utils



import sys
print(sys.modules['ehos.db'] )
print( ehos_db )

db_name = 'ehos_testing'
url = "postgresql://ehos:ehos@127.0.0.1:5432/{db_name}".format( db_name=db_name )




def create_tables():

    db = db_utils.DB( url )

    tables = db.table_names()

    for table in tables:
        #print("Dropping table {}".format( table ))
        db.do("DROP table IF EXISTS {} CASCADE".format( table ))

    db.from_file( 'sql/instances.sql')

    db.close()

def test_init():

    i = ehos_db.DB( )
    i.connect( url )

    i.disconnect()


def test_create_tables():
    create_tables()


def test_add_cloud():

    i = ehos_db.DB( )
    i.connect( url )
    create_tables()

    a = i.cloud_id('cloud_1')
    b = i.cloud_id('cloud_2')

    assert a == i.cloud_id('cloud_1')
    assert b == i.cloud_id('cloud_2')


def test_get_clouds():

    i = ehos_db.DB( )
    i.connect( url )
    create_tables()

    a = i.cloud_id('cloud_1')
    b = i.cloud_id('cloud_2')

    assert [{'id':1, 'name':'cloud_1'},
            {'id':2, 'name':'cloud_2'}] == i.clouds()

    
def test_add_state():

    i = ehos_db.DB( )
    i.connect( url )
    create_tables()


    a = i.vm_state_id('state_1')
    b = i.vm_state_id('state_2')

    assert a == i.vm_state_id('state_1')
    assert b == i.vm_state_id('state_2')
    

def test_add_status():

    i = ehos_db.DB( )
    i.connect( url )
    create_tables()


    a = i.node_state_id('status_1')
    b = i.node_state_id('status_2')

    assert a == i.node_state_id('status_1')
    assert b == i.node_state_id('status_2')

    
    
def test_add_node():


    i = ehos_db.DB( )
    i.connect( url )
    create_tables()


    i.add_node(id='id1', name='name1', cloud='uh1', vm_state='booting', node_state='starting')


def test_get_nodes():


    i = ehos_db.DB( )
    i.connect( url )
    create_tables()


    i.add_node(id='id1', name='name1', cloud='uh1', vm_state='booting', node_state='starting')
    i.add_node(id='id2', name='name2', cloud='uh2', vm_state='booting2', node_state='starting2')
    i.add_node(id='id3', name='name3', cloud='uh3', vm_state='booting', node_state='starting')

    assert [{'id': 1, 'uuid': 'id1', 'name': 'name1', 'node_state': 'starting', 'vm_state': 'booting'},
            {'id': 2, 'uuid': 'id2', 'name': 'name2', 'node_state': 'starting2', 'vm_state': 'booting2'},
            {'id': 3, 'uuid': 'id3', 'name': 'name3', 'node_state': 'starting', 'vm_state': 'booting'}] == i.nodes()


def test_get_nodes_002():


    i = ehos_db.DB( )
    i.connect( url )
    create_tables()


    i.add_node(id='id1', name='name1', cloud='uh1', vm_state='booting', node_state='starting')
    i.add_node(id='id2', name='name2', cloud='uh2', vm_state='booting2', node_state='starting2')
    i.add_node(id='id3', name='name3', cloud='uh3', vm_state='booting', node_state='starting')

    print( i.nodes())

    assert [{'id': 1, 'uuid': 'id1', 'name': 'name1', 'node_state': 'starting', 'vm_state': 'booting'},
            {'id': 3, 'uuid': 'id3', 'name': 'name3', 'node_state': 'starting', 'vm_state': 'booting'}] == i.nodes(node_state_id=1)


def test_get_nodes_003():


    i = ehos_db.DB( )
    i.connect( url )
    create_tables()


    i.add_node(id='id1', name='name1', cloud='uh1', vm_state='booting', node_state='starting')
    i.add_node(id='id2', name='name2', cloud='uh2', vm_state='booting2', node_state='starting2')
    i.add_node(id='id3', name='name3', cloud='uh3', vm_state='booting', node_state='starting')

    assert [{'id': 2, 'uuid': 'id2', 'name': 'name2', 'node_state': 'starting2', 'vm_state': 'booting2'}] == i.nodes(vm_state_id=2)


def test_nodes_state():


    i = ehos_db.DB( )
    i.connect( url )
    create_tables()


    i.add_node(id='id1', name='name1', cloud='uh1', vm_state='booting', node_state='starting')
    i.add_node(id='id2', name='name2', cloud='uh2', vm_state='booting2', node_state='starting2')
    i.add_node(id='id3', name='name3', cloud='uh3', vm_state='booting', node_state='starting')

    assert [{'id':1, 'name':'starting'},
            {'id':2, 'name':'starting2'}] == i.node_states()


def test_vm_state():


    i = ehos_db.DB( )
    i.connect( url )
    create_tables()


    i.add_node(id='id1', name='name1', cloud='uh1', vm_state='booting', node_state='starting')
    i.add_node(id='id2', name='name2', cloud='uh2', vm_state='booting2', node_state='starting2')
    i.add_node(id='id3', name='name3', cloud='uh3', vm_state='booting', node_state='starting')

    assert [{'id':1, 'name':'booting'},
            {'id':2, 'name':'booting2'}] == i.vm_states()


def test_node_id():


    i = ehos_db.DB( )
    i.connect( url )
    create_tables()


    i.add_node(id='id1', name='name1', cloud='uh1', vm_state='booting', node_state='starting')
    i.add_node(id='id2', name='name2', cloud='uh2', vm_state='booting2', node_state='starting2')
    i.add_node(id='id3', name='name3', cloud='uh3', vm_state='booting', node_state='starting')

    assert 2  == i.node_id('id2')


def test_update_node():

    i = ehos_db.DB( )
    i.connect( url )
    create_tables()

    i.vm_state_id('booting')
    i.node_state_id('starting')


    i.add_node(id='id2', name='name2', cloud='uh1', vm_state='booting', node_state='starting')


    i.update_node(uuid='id2', vm_state='changed_vm_state')
    i.update_node(uuid='id2', node_state='changed_node_state')


def test_update_node_002():

    i = ehos_db.DB( )
    i.connect( url )
    create_tables()

    i.vm_state_id('booting')
    i.node_state_id('starting')


    i.add_node(id='id2', name='name2', cloud='uh1', vm_state='booting', node_state='starting')
    i.add_node(id='id2', name='name2', cloud='uh1', vm_state='booting1', node_state='starting2')

    assert [{'id': 1, 'uuid': 'id2', 'name': 'name2', 'node_state': 'starting2', 'vm_state': 'booting1'}] == i.nodes()
