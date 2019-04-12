
import sys
import re
import os
import tempfile
import pprint
pp = pprint.PrettyPrinter(indent=4)


import pytest


import ehos as E


def test_timestamp():


    
    assert type(E.timestamp() ) == int
    
    
    

def test_datetimestamp():
    dt = E.datetimestamp()
    assert type( dt ) == str
    assert re.match(r'\d+T\d+', dt)




def test_random_string():

    rnd_str = E.random_string()
    
    assert type( rnd_str ) == str
    assert len( rnd_str) == 10

def test_random_string_long():

    rnd_str = E.random_string(100)
    
    assert type( rnd_str ) == str
    assert len( rnd_str) == 100

    
def test_make_node_name():

    nn = E.make_node_name()
    assert re.match(r'ehos-node-\d+', nn)


def test_make_node_name_spec():

    nn = E.make_node_name(prefix="EHOS_1", name='MaSter')
    assert re.match(r'ehos-1-master-\d+', nn)

    
    
def test_get_node_id():
    id = E.get_node_id(filename='t/data/instance-id')

    assert id == '6f4967d5-706e-4f58-8287-74796c8fff26'

def test_get_node_id_no_file():
    with pytest.raises( RuntimeError ):
        id = E.get_node_id(filename='t/data/instance-id-no-here')

    
    

def test_readin_config_file():
    config = E.readin_config_file('t/data/ehos.yaml')

    pp.pprint( config )

    
    assert sorted(config.clouds.keys()) == ['os_bgn', 'os_cph']

    assert config.clouds.os_bgn.backend == 'openstack'
    assert config.clouds.os_bgn.region_name ==  'bgo'
    assert config.clouds.os_bgn.project_domain_name == 'banana-port'
    assert config.clouds.os_bgn.user_domain_name == 'banana-port'
    assert config.clouds.os_bgn.no_cache ==  1
    assert config.clouds.os_bgn.auth.username == 'marmoset@bananalab.com'
    assert config.clouds.os_bgn.auth.password == 'new-world'
    assert config.clouds.os_bgn.auth.project_name == 'raindance'
    assert config.clouds.os_bgn.auth.auth_url ==  'https://cloud.dk:5000/v3'

    assert config.clouds.os_cph.backend == 'openstack'
    assert config.clouds.os_cph.region_name == 'cph'
    assert config.clouds.os_cph.project_domain_name == 'banana-port'
    assert config.clouds.os_cph.user_domain_name == 'banana-port'
    assert config.clouds.os_cph.no_cache == 1
    assert config.clouds.os_cph.auth.username == 'mandrill@bananalab.com'
    assert config.clouds.os_cph.auth.password == 'old-world'
    assert config.clouds.os_cph.auth.project_name == 'mermaid'
    assert config.clouds.os_cph.auth.auth_url == 'https://cloud.no:5000/v3'

    assert config.ehos.project_prefix == 'ehos-v2'
    assert config.ehos.flavor == 'm1.medium' 
    assert config.ehos.base_image_id == '{basename}'
    assert config.ehos.base_image == 'GOLD CentOS 7'
    assert config.ehos.network == 'dualStack'
    assert config.ehos.key == 'banana-key'
    assert config.ehos.security_groups == 'banana'

    # for tweaking the ehos demon
    assert config.ehos.submission_nodes == 1 # masternode countes as one node.
    assert config.ehos.nodes_max == 4
    assert config.ehos.nodes_min == 2
    assert config.ehos.nodes_spare == 2
    assert config.ehos.sleep_min == 10
    assert config.ehos.sleep_max == 60

    # Condor settings
    assert config.condor.host_ip == 'None'
    assert config.condor.password == 'None'

    assert E.check_config_file( config ) == True

    

def test_readin_whole_file():

    content = E.get_node_id(filename='t/data/instance-id')

    assert content == "6f4967d5-706e-4f58-8287-74796c8fff26"

    
def test_find_config_file( ):
    config_file = E.find_config_file(filename='ehos.yaml', dirs=['t/data'])

    assert config_file == 't/data/ehos.yaml'


def test_alter_file():


    tmp_fh, tmp_file = tempfile.mkstemp(suffix=".yaml", dir="/tmp/", text=True)
#    tmp_fh.close()
    
    E.patch_file(filename='t/data/ehos.yaml', pattern='{basename}', replace='Base1', outfile=tmp_file)
    config = E.readin_config_file(tmp_file)

    assert config.ehos.base_image_id == 'Base1'
    os.remove( tmp_file )

def test_alter_file_patterns():

    tmp_fh, tmp_file = tempfile.mkstemp(suffix=".yaml", dir="/tmp/", text=True)
    
    E.patch_file(filename='t/data/ehos.yaml', patterns=[('{basename}', 'Base111')], outfile=tmp_file)
    config = E.readin_config_file(tmp_file)

    assert config.ehos.base_image_id == 'Base111'
    os.remove( tmp_file )

    
def test_log_level():

    assert E.log_level(1) == 1
    assert E.log_level(2) == 2
    assert E.log_level(3) == 3
    assert E.log_level(4) == 4
    assert E.log_level(5) == 5
    assert E.log_level(0) == 1
    assert E.log_level(6) == 5

def test_system_call():
    assert E.system_call( "sleep 1" ) == 0

    with pytest.raises( FileNotFoundError ):
        E.system_call( "sleeps 1" )
        

def test_make_uid_domain_name():

    uid_domain = E.make_uid_domain_name(length=10)

    assert type(uid_domain) == str
    assert uid_domain.count(".") == 9


def test_make_uid_domain_name_long():


    with pytest.raises( RuntimeError ):
        uid_domain = E.make_uid_domain_name(length=1000)
    

    
    
