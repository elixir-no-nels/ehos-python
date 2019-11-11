
import sys
import re
import os
import tempfile
import pprint

import ehos.utils

pp = pprint.PrettyPrinter(indent=4)


import pytest


import ehos as E

db_name = 'ehos_testing'
url = "postgresql://ehos:ehos@127.0.0.1:5432/{db_name}".format( db_name=db_name )

    
def test_init():
    E.init( condor_init=False)
    E.instances_connect_to_database( url )



def test_connect_to_clouds():

    config = ehos.utils.readin_config_file('ehos.yaml')

    E.connect_to_clouds( config )
    pp.pprint( E.get_cloud_connector('uh_bgo'))
#    assert


def test_connect_to_clouds_001():

    config = ehos.utils.readin_config_file('ehos.yaml')

    config.clouds.uh_bgo.backend = 'Unknown'
    with pytest.raises( RuntimeError ):
        E.connect_to_clouds( config )

