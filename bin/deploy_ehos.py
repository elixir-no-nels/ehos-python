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



def make_write_file_block_from_file(filename:str, outname:str, directory:str='/usr/local/etc/ehos/'):
    """ makes a yaml write_file content block 
    
    Simple wrapper function so the block can come from a file rather than as a string

    Args:
      filename: file to enter as content
      outname: the filename the yaml points to
      directory: the directory the yaml points to

    Returns
      write_file block for a yaml file (str)

    Raises:
      None    

    """

    content = ehos.readin_whole_file(filename)

    return make_write_file_block(content, outname, directory)


def make_write_file_block(content:str, outname:str, directory:str='/usr/local/etc/ehos/'):
    """ makes a yaml write_file content block 
    
    Args:
      content: what to enter as content into the block
      outname: the filename the yaml points to
      directory: the directory the yaml points to

    Returns
      write_file block for a yaml file (str)

    Raises:
      None    

    """

    block = """-   content: |
{content}
    path: {filepath}
    owner: root:root
    permissions: '0644'
"""

    # pad the write_file_block with 8 whitespaces to ensure yaml integrity
    content = re.sub("\n", "\n        ", "        "+content)

    
    block = re.sub('{filepath}', "{}/{}".format(directory, outname), block)
    block = re.sub('{content}', "{}".format(content), block)

    return block



def write_master_yaml( config:Munch, master_filename:str, submit_filename:str=None, execute_filename:str=None, directory:str='/usr/local/etc/ehos/'):
    """ Makes the yaml file that will be passed on to the master 

    Args: 
      config: the ehos config file (as read in )
      master_filename: filename of the master config
      submit_filename: bespoke ehos.yaml file
      execute_filename: bespoke ehos.yaml file
      directory: where to store the config files on the master server

    Returns
      filename (will full path) of merged config file

    Raises:
      None
    """


    # make the munch back to yaml format (string)
    config_text =  Munch.toYAML( config )
    
    write_file_block = make_write_file_block(config_text, "ehos.yaml", directory)
                                        
    if ( submit_filename is not None):
        write_file_block += make_write_file_block_from_file( submit_filename, 'submit.yaml', directory)

    if ( execute_filename is not None):
        write_file_block += make_write_file_block_from_file( execute_filename, 'execute.yaml',directory)



    # readin the maste file and insert out write_file_block(s)
    master_content = ehos.readin_whole_file(master_filename)
    master_content = re.sub('{write_files}', write_file_block, master_content)

    
    # write new config file to it and close it. As this is an on level
    # file handle the string needs to be encoded into a byte array

    # create a tmpfile/handle
    tmp_fh, tmpfile = tempfile.mkstemp(suffix=".yaml", dir="/tmp/", text=True)
    os.write( tmp_fh, str.encode( master_content ))
    os.close( tmp_fh )


    return tmpfile


def create_base_image(args:dict, config:Munch):
    """ Creates a base image

    Args:
      args: the argparse dict 
      config: the configuration 

    Returns:
      base_image_id (str)

    Raises:
      None
    """

    ehos.verbose_print("Creating base server",  ehos.INFO)

    base_id = ehos.server_create( "{}-base".format(config.ehos.project_prefix),
                                  image=config.ehos.base_image,
                                  flavor=config.ehos.flavor,
                                  network=config.ehos.network,
                                  key=config.ehos.key,
                                  security_groups=config.ehos.security_groups,
                                  userdata_file=args.base_yaml)
    
    ehos.verbose_print("Created base server, waiting for it to come online",  ehos.INFO)


    # Wait for the server to come online and everything have been configured.    
    ehos.wait_for_log_entry(base_id, "The EHOS base system is up")
    ehos.verbose_print("Base server is now online",  ehos.INFO)
            
    base_image_id = ehos.make_image_from_server( base_id, "{}-image".format(config.ehos.project_prefix) )
    ehos.verbose_print("Created base image",  ehos.INFO)
        
    # delete the vanilla server.
    ehos.server_delete( base_id )
    ehos.verbose_print("Deleted base server",  ehos.INFO)
    # cheating a bit here but it makes the downstream bit easier
    return base_image_id


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
    parser.add_argument('-b', '--base-image-id', help="use this image as the base image")
    parser.add_argument('-m', '--master-yaml',   help="yaml config file to create master image from", default=ehos.find_config_file('master.yaml'))
    parser.add_argument('-B', '--base-yaml',     help="yaml config file to create base image from",   default=ehos.find_config_file('base.yaml'))
    parser.add_argument('-e', '--execute-yaml',  help="yaml config file for execute node from",       required=False)
    parser.add_argument('-s', '--submit-yaml',   help="yaml config file for submit node from",        required=False)
    parser.add_argument('-c', '--config-dir',    help="Where to write config files to on the master", required=False, default='/usr/local/etc/ehos/')

    parser.add_argument('-v', '--verbose', default=1, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('config_file', metavar='config-file', nargs=1,   help="yaml formatted config file")

    args = parser.parse_args()

    # as this is an array, and we will ever only get one file set it
    args.config_file = args.config_file[ 0 ]

    # set the leve of what to print.
    ehos.verbose_level( args.verbose )

    ehos.verbose_print("Parsed arguments", ehos.DEBUG)

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
    
    # No base id have been provided, so we will build one
    if (not args.base_image_id and config.ehos.base_image_id == 'None'):
        config.ehos.base_image_id = create_base_image( args, config )

    elif (args.base_image_id is not None ):
        ehos.verbose_print( "using the base-image-id given on the command line", ehos.INFO)
        config.ehos.base_image_id = args.base_image_id

    elif(config.ehos.base_image_id != 'None'):
        ehos.verbose_print( "using the base-image-id from the config file", ehos.INFO)
        
        
    tmp_master_config_file = write_master_yaml( config, args.master_yaml, args.submit_yaml, args.execute_yaml, args.config_dir)
    

    ehos.verbose_print("Written tmp file to: {}".format( tmp_master_config_file), ehos.DEBUG)
    
    # create the master node, That is it nothing more to do here.
    base_id = ehos.server_create( "{}-master".format(config.ehos.project_prefix),
                                  image=config.ehos.base_image_id,
                                  flavor=config.ehos.flavor,
                                  network=config.ehos.network,
                                  key=config.ehos.key,
                                  security_groups=config.ehos.security_groups,
                                  userdata_file=tmp_master_config_file)
    

    ehos.verbose_print("Created master node", ehos.INFO)
    # Wait for the server to come online and everything have been configured.    
    ehos.wait_for_log_entry(base_id, "The EHOS master is")
    ehos.verbose_print("Master server is now online",  ehos.INFO)

 
    
        
if __name__ == '__main__':
    main()
else:
    print("This is not meant to be used as a library")
    sys.exit(2)
