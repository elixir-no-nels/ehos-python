#!/usr/bin/python3
# 
# 
# 
# 
# Kim Brugger (20 Sep 2018), contact: kim@brugger.dk

import sys
import os
import argparse
import re
import tempfile

import pprint
pp = pprint.PrettyPrinter(indent=4)

import logging
logger = logging.getLogger('ehos_build_images')

from munch import Munch

# Hackey time add ehos module directory if running from a download!

script_dir = os.path.dirname(os.path.abspath( __file__))
if os.path.isfile("{}/../ehos/ehos.py".format( script_dir)):
    sys.path.append("{}/../".format( script_dir))
    

import ehos




def main():
    """ main loop
    
    Args:
      None
    
    Returns:
      None
    
    Raises:
      None

    """
    
    parser = argparse.ArgumentParser(description='deploy_ehos: Deploy ehos onto a openstack server ')

    # magically sets default config files

    parser.add_argument('-v', '--verbose', default=1, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('-B', '--base-yaml',     help="yaml config file to create base image from",   default=ehos.find_config_file('base.yaml'))
    parser.add_argument('config_file', metavar='config-file', nargs=1,   help="yaml formatted config file")

    args = parser.parse_args()

    # as this is an array, and we will ever only get one file set it
    config_file = args.config_file[ 0 ]

    # set the leve of what to print.
    ehos.log_level( args.verbose )

    ehos.init(condor_init=False)
    
    logger.debug("Parsed arguments")

    # readin the config file in as a Munch object
    config = ehos.readin_config_file( config_file )

    # Make some images, one for each cloud
    ehos.connect_to_clouds( config )
    images = ehos.create_images( config, args.base_yaml)
    

    # Add the image name to the config object.
    for cloud in images:
        config.clouds[ cloud ].image = images[ cloud ]
        

    # add a password to the config file if not already set:
    if 'password' not in config.condor or config.condor.password == 'None':
        config.condor.password = ehos.random_string(25)

    # make a backup of the original config_file, and write a new one
    # Rename original yaml file
    os.rename(config_file, "{}.backup".format( config_file ))

    fh = open( config_file, 'w')
    config_text =  Munch.toYAML( config )
    fh.write(  config_text )
    fh.close()
 
    
        
if __name__ == '__main__':
    main()
else:
    print("This is not meant to be used as a library")
    sys.exit(2)
