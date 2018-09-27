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

from munch import Munch

import ehos

def wrap_yaml( template:str, config:str ):
    """ inserts config (str) into the the template (file) at the {configuration} tag

    Args:
      template: path to the yaml template file to use
      config: contents of the yaml config file to embed into the template
    
    Returns:
      the template with the config file embedded into it (str)

    Raises:
      None

    """

    fh = open(template, 'r')
    lines = "".join(fh.readlines())

    # pad the config with 8 whitespaces to ensure yaml integrity
    config = re.sub("\n", "\n        ", "        "+config)

    # replace our keywork with the config content
    lines = re.sub('{configuration}', config, lines)
    

    return lines




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

    parser.add_argument('-b', '--base-image-id',  help="use this image as the base image")
    parser.add_argument('-B', '--base-yaml',   help="yaml config file to create base image from")
    parser.add_argument('-m', '--master-yaml', required=True, default='configs/master-config.yaml', help="yaml config file to create master image from")
    parser.add_argument('-v', '--verbose', default=False, action='store_true',  help="Verbose output")
    parser.add_argument('config_file', metavar='config-file', nargs=1,   help="yaml formatted config file")

    args = parser.parse_args()

    # as this is an array, and we will ever only get one file set it
    args.config_file = args.config_file[ 0 ]
    
    if ( args.verbose):
        print("Parsed arguments")
    
    
    # readin the config file in as a Munch object
    with open(args.config_file, 'r') as stream:
        config = Munch.fromYAML(stream)


    # connect to the openstack
    ehos.connect( auth_url=config.cloud.auth_url ,
                  user_domain_name=config.cloud.user_domain_name,
                  project_domain_name=config.cloud.project_domain_name,
                  username=config.cloud.username,
                  password=config.cloud.password,
                  project_name=config.cloud.project_name,
                  region_name=config.cloud.region_name,
                  no_cache=config.cloud.no_cache,
    )

    if ( args.verbose):
        print("Connected to openStack")

    
    # we are building a base server and image from a build file
    if args.base_yaml:
            
        base_id = ehos.server_create( "{}-base".format(config.ehos.project_prefix),
                                      image=config.ehos.base_image,
                                      flavor=config.ehos.flavor,
                                      network=config.ehos.network,
                                      key=config.ehos.key,
                                      security_groups=config.ehos.security_groups,
                                      userdata_file=args.base_yaml)

        if ( args.verbose):
            print("Created base server, waiting for it to come online")


        # Wait for the server to come online and everything have been configured.    
        ehos.wait_for_log_entry("The EHOS base system is up")
        if ( args.verbose):
            print("Base server is now online")
            
            
        base_image_id = ehos.make_image_from_server( base_id, "{}-image".format(config.ehos.project_prefix) )

        if ( args.verbose):
            print("Created base image")
        # delete the vanilla server.
        ehos.server_delete( base_id )
        if ( args.verbose):
            print("Deleted base server")
        # cheating a bit here but it makes the downstream bit easier
        args.base_base_id = base_image_id
        config.ehos.base_image_id = args.base_base_id

        
    # make the munch back to yaml format (string)
    config_text =  Munch.toYAML(config)
        
    # create a tmpfile/handle
    tmp_fh, tmpfile = tempfile.mkstemp(suffix=".yaml", dir="/tmp/", text=True)
        
    # write new config file to it and close it. As this is an on level
    # file handle the string needs to be encoded into a byte array
    os.write( tmp_fh, str.encode(wrap_yaml( args.master_yaml, config_text )))
    os.close( tmp_fh )
    if ( args.verbose):
        print("Written tmp file to: {}".format( tmpfile))
    
    # create the master node, That is it nothing more to do here.
    master_id = ehos.server_create( "{}-master".format(config.ehos.project_prefix),
                                    image='GOLD CentOS 7',
                                    flavor='m1.medium',
                                    network='dualStack',
                                    key='mykey',
                                    security_groups='kbr',
                                    userdata_file=tmpfile)


    if ( args.verbose):
        print("Created master node")


        
if __name__ == '__main__':
    main()
else:
    print("This is not meant to be used as a library")
    sys.exit(2)
