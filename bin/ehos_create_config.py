#!/usr/bin/python3
""" 
 
The goal of this script is to ease the config generation by using an existing keystone file 
 
 Kim Brugger (06 Jan 2019), contact: kim@brugger.dk
"""

import sys
import os
import argparse
import re
import tempfile

import pprint
pp = pprint.PrettyPrinter(indent=4)

import logging
logger = logging.getLogger('deploy_ehos')


from munch import Munch

import ehos


def get_keystone_info(filename:str):

    res = {}
    
    fh = open( filename, 'r')
    for line in fh.readlines():
        line = line.rstrip()
        key, value = None, None
        # weed out comments
        line = re.sub(r'#.*','', line)
        
        # Ignore empty lines
        if line == '' or re.match(r'^\s+$', line):
            continue
        
        _,  key, value = re.split(r'[ =]', line)
        res[ key ] = value

    return res



def find_suitable_image( handle, names ):

    images = handle.get_images( name='centos')

    if images == []:
        raise RuntimeError('Could not find a suitable CentOS 7 image to use')


    for image in images:
        for name in names:
            if (name.lower() in map( str.lower, image['tags'])):
                return image
    

    raise RuntimeError('Could not find a suitable CentOS 7 image to use')


def find_suitable_flavour( handle, min_ram, min_cpus ):
    flavours = handle.get_flavours()

    flavours = sorted( flavours, key=lambda k: k['ram'], reverse=False)
    

    for flavour in flavours:
        if ( flavour['ram'] >= min_ram and
             flavour['cpus'] >= min_cpus ) :
            return flavour

    raise RuntimeError('Could not find a vm flavour that satisfy the minimum requirements')


def main():
    """ main loop
    
    Args:
      None
    
    Returns:
      None
    
    Raises:
      None

    """
    
    parser = argparse.ArgumentParser(description='make_ehos_config_file.py: make a ehos.yaml config file from an existing keystone file ')

    # magically sets default config files
    parser.add_argument('config_template', metavar='config-template', nargs=1, help="yaml config template", default=ehos.find_config_file('ehos.yaml.template'))
    parser.add_argument('keystone_file', metavar='keystone-file', nargs=1,   help="openstack keystone file")

    args = parser.parse_args()

    # as this is an array, and we will ever only get one file set it
    args.config_template = args.config_template[ 0 ]
    args.keystone_file = args.keystone_file[ 0 ]


    logger.debug("Parsed arguments")

    # readin the config file in as a Munch object
    template = ehos.readin_config_file( args.config_template )

    keystone  = get_keystone_info( args.keystone_file )
#    pp.pprint( keystone )
                         
    template['clouds'][ 'default' ][ 'auth_url'] = keystone[ 'OS_AUTH_URL' ]
    template['clouds'][ 'default' ][ 'password'] = keystone[ 'OS_PASSWORD']
    template['clouds'][ 'default' ][ 'username'] = keystone[ 'OS_USERNAME']
    
    template['clouds'][ 'default' ][ 'project_domain_name' ] = keystone[ 'OS_PROJECT_DOMAIN_NAME']
    template['clouds'][ 'default' ][ 'user_domain_name' ] = keystone[ 'OS_USER_DOMAIN_NAME']
    template['clouds'][ 'default' ][ 'project_name' ]= keystone[ 'OS_PROJECT_NAME']
    template['clouds'][ 'default' ][ 'region_name']= keystone[ 'OS_REGION_NAME']
    


#    pp.pprint( template )
    
    ehos.init(condor_init=False)
    ehos.connect_to_clouds( template )
    
    default = ehos.get_cloud_connector( 'default' )

    image = find_suitable_image( default, ['centos7', 'centos 7' ])
    flavour = find_suitable_flavour( default,
                                     min_ram=template.ehos_daemon.min_ram*1024,
                                     min_cpus=template.ehos_daemon.min_cores)

#    pp.pprint( image )
#    pp.pprint( flavour )
#    sys.exit()

    template.ehos.image   = image['name']
    template.ehos.flavor = flavour['name']

    
    template.condor.password = ehos.random_string(25)
        


    print( Munch.toYAML( template ))

        
    sys.exit( -1 )
        
if __name__ == '__main__':
    main()
else:
    print("This is not meant to be used as a library")
    sys.exit(2)
