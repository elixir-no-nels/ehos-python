import pytest
import re
import tempfile
import os

import ehos.utils as utils

def test_get_host_ip():

    ip = utils.get_host_ip()

    # as the actual ip will differ go for 4 digits spaced with .
    assert re.match(r'\d+\.\d+\.\d+\.\d+', ip)


def test_get_host_name():

    ip = utils.get_host_name()

    # as the actual ip will differ go for 4 digits spaced with .
    assert re.match(r'\w+', ip)


def test_timestamp():

    ts = utils.timestamp()
    print( ts )
    assert isinstance(ts, int)


def test_datetimestamp():

    ts = utils.datetimestamp()

    assert re.match(r'\d+T\d+', ts)


def test_random_string_001():

    assert len( utils.random_string(4)) == 4

def test_random_string_002():

    assert len( utils.random_string()) == 10


def test_random_string_003():

    assert len( utils.random_string(-1)) == 0


def test_make_node_name():

    name = utils.make_node_name()
    assert re.match(r'ehos-node-\d+t\d+', name)


def test_make_node_name_002():

    name = utils.make_node_name(prefix="prefix", name='type')
    assert re.match(r'prefix-type-\d+t\d+', name)

def test_system_call_001():


    assert utils.system_call('ls -lrt') == 0

def test_system_call_002():

    with pytest.raises( FileNotFoundError ):
        assert utils.system_call('lss -lrt') != 0


def test_get_node_id():
    with pytest.raises( RuntimeError ):
        utils.get_node_id()

def test_get_node_id_002():

    assert utils.get_node_id('t/data/instance-id') == '6f4967d5-706e-4f58-8287-74796c8fff26'

def test_readin_whole_file():

    content = utils.readin_whole_file(filename='t/data/instance-id')

    assert content == "6f4967d5-706e-4f58-8287-74796c8fff26\n"


def test_find_config_file( ):
    config_file = utils.find_config_file(filename='ehos.yaml')

    assert config_file == 'etc/ehos.yaml'


def test_find_config_file_002():
    config_file = utils.find_config_file(filename='ehos.yaml', dirs=['t/data'])

    assert config_file == 't/data/ehos.yaml'


def test_find_config_file_003():
    with pytest.raises( RuntimeError ):
        config_file = utils.find_config_file(filename='ehos.Yaml', dirs=['t/data'])


def test_readin_config_file():
    config = utils.readin_config_file('t/data/ehos.yaml')

 #   pp.pprint( config )


def test_alter_file():


    tmp_fh, tmp_file = tempfile.mkstemp(suffix=".yaml", dir="/tmp/", text=True)
    #    tmp_fh.close()

    utils.patch_file(filename='t/data/ehos.yaml', pattern='{basename}', replace='Base1', outfile=tmp_file)
    config = utils.readin_config_file(tmp_file)

    assert config.ehos.base_image_id == 'Base1'
    os.remove( tmp_file )

def test_alter_file_002():


    utils.patch_file(filename='t/data/ehos.yaml', pattern='{basename}', replace='Base1')
    config = utils.readin_config_file('t/data/ehos.yaml')

    assert config.ehos.base_image_id == 'Base1'
    os.unlink('t/data/ehos.yaml')
    os.rename('t/data/ehos.yaml.original', 't/data/ehos.yaml')
#    os.remove( tmp_file )


def test_alter_file_003():

    with pytest.raises( RuntimeError ):
        utils.patch_file(filename='t/data/ehos.yaml', pattern=None, replace=None, outfile=None)


def test_alter_file_patterns():

    tmp_fh, tmp_file = tempfile.mkstemp(suffix=".yaml", dir="/tmp/", text=True)

    utils.patch_file(filename='t/data/ehos.yaml', patterns=[('{basename}', 'Base111')], outfile=tmp_file)
    config = utils.readin_config_file(tmp_file)

    assert config.ehos.base_image_id == 'Base111'
    os.remove( tmp_file )




def test_make_uid_domain_name():

    uid_domain = utils.make_uid_domain_name(length=10)

    assert type(uid_domain) == str
    assert uid_domain.count(".") == 9


def test_make_uid_domain_name_long():


    with pytest.raises( RuntimeError ):
        uid_domain = utils.make_uid_domain_name(length=1000)




