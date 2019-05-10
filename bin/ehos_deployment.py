#!/usr/bin/env python3
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

import ehos.utils

pp = pprint.PrettyPrinter(indent=4)

import ehos.log_utils as logger


from munch import Munch

import ehos
import ehos.instances



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

    content = ehos.utils.readin_whole_file(filename)

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



def write_master_yaml( config:Munch, master_filename:str, execute_filename:str=None, directory:str='/usr/local/etc/ehos/'):
    """ Makes the yaml file that will be passed on to the master 

    Args: 
      config: the ehos config file (as read in )
      master_filename: filename of the master config
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
                                        
    if ( execute_filename is not None):
        write_file_block += make_write_file_block_from_file( execute_filename, 'execute.yaml',directory)

    # readin the maste file and insert out write_file_block(s)
    master_content = ehos.utils.readin_whole_file(master_filename)
    master_content = re.sub('#{write_files}', write_file_block, master_content)

    
    # write new config file to it and close it. As this is an on level
    # file handle the string needs to be encoded into a byte array

    # create a tmpfile/handle
    tmp_fh, tmpfile = tempfile.mkstemp(suffix=".yaml", dir="/tmp/", text=True)
    os.write( tmp_fh, str.encode( master_content ))
    os.close( tmp_fh )

    return tmpfile


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
    parser.add_argument('-m', '--master-yaml', help="yaml config file to create master image from", default=ehos.utils.find_config_file('master.yaml'))
    parser.add_argument('-e', '--execute-yaml', help="yaml config file for execute node from", required=False, default=ehos.utils.find_config_file('execute.yaml'))
    #parser.add_argument('-c', '--config-dir',    help="Where to write config files to on the master", required=False, default='/usr/local/etc/ehos/')

    parser.add_argument('-l', '--logfile', default=None, help="Logfile to write to, default is stdout")
    parser.add_argument('-v', '--verbose', default=4, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('config_file', metavar='config-file', nargs=1,   help="yaml formatted config file")

    args = parser.parse_args()

    # as this is an array, and we will ever only get one file set it
    config_file = args.config_file[ 0 ]

    # set the leve of what to print.
    logger.init(name='ehos_deployment', log_file=args.logfile )
    logger.set_log_level( args.verbose )
    logger.debug("Parsed arguments")

    # readin the config file in as a Munch object
    config = ehos.utils.readin_config_file(config_file)

    # Make some images, one for each cloud
    instances = ehos.instances.Instances()
    clouds = ehos.connect_to_clouds( config )
    instances.add_clouds( clouds )


    if 'password' not in config.condor or config.condor.password == 'None':
        config.condor.password = ehos.utils.random_string(25)
        
    tmp_master_config_file = write_master_yaml( config, args.master_yaml, args.execute_yaml, '/usr/local/etc/ehos/')
    
    logger.debug("Written tmp config file to: {}".format( tmp_master_config_file))

    master_id, master_ip = ehos.create_master_node(instances, config, tmp_master_config_file)

    print(" Master node created IP: {} ID: {}".format( master_ip, master_id))

    

    
        
if __name__ == '__main__':
    main()
else:
    print("This is not meant to be used as a library")
    sys.exit(2)
