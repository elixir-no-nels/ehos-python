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


def set_firewall_rules(config:Munch, group_name:str, internal=False):

    print("Setting up firewall rules under the security group: '{}'".format( group_name))
    
    for cloud in config.clouds:
    
        
        cloud = ehos.get_cloud_connector( cloud )
        groups = cloud.security_groups()

        if ( group_name not in groups):
            
            group = cloud.security_group_create(group_name)
            groups = cloud.security_groups()



        if ( internal  ):
    
            cloud.firewall_add_incoming_rules(name=group_name, rules=[{'port': 22,   'protocol': 'tcp', 'remote_ip_range': '0.0.0.0/0'},
                                                                      {'port': 9618, 'protocol': 'tcp', 'remote_group': group_name},                                                                  
                                                                      {'port': 9618, 'protocol': 'udp', 'remote_group': group_name}, ] )
        else:

            cloud.firewall_add_incoming_rules(name=group_name, rules=[{'port': 22,   'protocol': 'tcp', 'remote_ip_range': '0.0.0.0/0'},
                                                                      {'port': 9618, 'protocol': 'tcp', 'remote_ip_range': '0.0.0.0/0'},                                                                  
                                                                      {'port': 9618, 'protocol': 'udp', 'remote_ip_range': '0.0.0.0/0'}, ] )

def upload_ssh_key(config, keypath:str, name:str='ehos'):

    print("Setting up ssh keys")
    for cloud in config.clouds:
        cloud = ehos.get_cloud_connector( cloud )
        cloud.upload_key( public_key=keypath, name=name)
            

def write_config( config:Munch, config_file:str):

    print("Overwriting config file with new information")
    os.rename(config_file, "{}.backup".format( config_file ))

    fh = open( config_file, 'w')
    config_text =  Munch.toYAML( config )
    fh.write(  config_text )
    fh.close()

        


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

    parser.add_argument('-v', '--verbose', default=4, action="count",  help="Increase the verbosity of logging output")

    parser.add_argument('-B', '--base-yaml',     help="yaml config file to create base image from",   default=ehos.find_config_file('base.yaml'))
    parser.add_argument('-c', '--create-images', action='store_true',     help="Create images, one in each cloud in the configuration file")

    parser.add_argument('-s', '--ssh-key',     help="ssh-key to upload")
    parser.add_argument('-S', '--ssh-key-name',     help="Name of ssh key",   default="ehos_key")
    
    parser.add_argument('-e', '--external-cloud', default=False, action='store_true',   help="Configure firewall rules for an external setup (open to the world)")
    parser.add_argument('-f', '--firewall-name',     help="Name of firewall (security-group)", default='ehos_firewall')

    
    parser.add_argument('config_file', metavar='config-file', nargs=1,   help="yaml formatted config file")

    
    args = parser.parse_args()



    
    # set the leve of what to print.
    ehos.log_level( args.verbose )
    ehos.init(condor_init=False)

    # as this is an array, and we will ever only get one file set it
    config_file = args.config_file[ 0 ]
    # readin the config file in as a Munch object
    config = ehos.readin_config_file( config_file )
    # Make some images, one for each cloud
    ehos.connect_to_clouds( config )

    logger.debug("Parsed arguments")

    changed_config = False
    

    if args.ssh_key is not None:
        upload_ssh_key(config, keypath=args.ssh_key, name=args.ssh_key_name)
        config.ehos.key = args.ssh_key_name
        changed_config = True

    if ( args.external_cloud ):
        set_firewall_rules(config, group_name=args.firewall_name, internal=False)
        config.ehos.security_groups = args.firewall_name
        changed_config = True

    else:
        set_firewall_rules(config, group_name=args.firewall_name, internal=True)
        config.ehos.security_groups = args.firewall_name
        changed_config = True
    
    # add a password to the config file if not already set:
    if 'password' not in config.condor or config.condor.password == 'None':
        print("Setting a password in the config file")
        config.condor.password = ehos.random_string(25)
        changed_config = True

        
    if ( changed_config ):
        write_config( config, config_file)
        changed_config = False
        
    if ( args.create_images):
        print("Creating image(s)")
        images = ehos.create_images( config, args.base_yaml, delete_original=True)
    

        # Add the image name to the config object.
        for cloud in images:
            if images[ cloud ] is None:
                print( "No image created for cloud '{}', fix this before progressing".format( cloud ))
                sys.exit(1)
            config.clouds[ cloud ].image = images[ cloud ]
            changed_config = True



    if ( changed_config ):
        write_config( config, config_file)
    
        
if __name__ == '__main__':
    main()
else:
    print("This is not meant to be used as a library")
    sys.exit(2)
