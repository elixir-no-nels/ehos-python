#!/usr/bin/python3
# 
# 
# 
# 
# Kim Brugger (20 Sep 2018), contact: kim@brugger.dk

import sys
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

    stream = open('ehos.yaml', 'r')
    config = Munch.fromYAML(stream)
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
    parser.add_argument('config_file', metavar='config-file', nargs=1,   help="yaml formatted config file")

    args = parser.parse_args()

    # as this is an array, and we will ever only get one file set it
    args.config_file = args.config_file[ 0 ]
    

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
                  no_cache=1,
    )

    # we are building a base server and image from a build file
    if args.base_yaml:
            
        base_id = ehos.server_create( "{}-base".format(config.ehos.project_prefix),
                                      image=config.ehos.image_id,
                                      flavor=config.ehos.flavor,
                                      network=config.ehos.network,
                                      key=config.ehos.key,
                                      security_groups=config.ehos.security_groups,
                                      userdata_file=args.base_yaml)


        image_id = ehos.make_image_from_server( base_id, "{}-image".format(config.ehos.project_prefix) )
        # cheating a bit here but it makes the downstream bit easier 
        args.base_image = image_id
        # delete the vanilla server.
        ehos.server_delete( base_id )

    config.ehos.image_id = args.base_id

    configuration =  Munch.toYAML(config)
    
    print( wrap_yaml( configuration ))
    
    sys.exit(1)




    stream = open('ehos_run.yaml', 'w')
    stream.write(Munch.toYAML(config))    # Write a YAML representation of data to 'document.yaml'.
    stream.close()

    
    
    master_id = ehos.server_create( "{}-master".format(config.ehos.project_prefix),
                                    image='GOLD CentOS 7',
                                    flavor='m1.medium',
                                    network='dualStack',
                                    key='mykey',
                                    security_groups='kbr',
                                    userdata_file='vm-configs/vanilla-condor.sh')



if __name__ == '__main__':
    main()
else:
    print("This is not meant to be used as a library")
    sys.exit(2)
