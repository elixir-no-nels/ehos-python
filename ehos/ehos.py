#!/usr/bin/python
# 
# 
# 
# 
# Kim Brugger (14 Sep 2018), contact: kim@brugger.dk

import os
import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)
import traceback
import random
import string
import time
import time
import datetime
import re
import shutil
import shlex
from typing import List, Tuple
import subprocess
import socket

from munch import Munch

import logging
logger = logging.getLogger('ehos')



import ehos.openstack
import ehos.htcondor 
import ehos.instances as I

global condor
condor    = None
global instances
instances = None


def init():
    """ init function for the module, connects to the htcondor server and sets up the instance tracking module

    Args:
      None
    
    Returns:
      None
    
    Raises:
      None
    """

    global condor
    global instances

    condor  = ehos.htcondor.Condor()
    instances = I.Instances()


#    print(condor)
#    print( instances )
    
def connect_to_clouds(config:Munch) -> None:
    """ Connects to the clouds spefified in the config file

    Args:
      config: from the yaml input file
    
    Returns:
      connection names (list)

    Raises:
      RuntimeError if unknown backend
    """

    global instances

    for cloud_name in config.clouds:

        if ( config.clouds[ cloud_name ].backend == 'openstack'):

            cloud_config = config.clouds[ cloud_name ]

            cloud = ehos.openstack.Openstack()
            cloud.connect( cloud_name=cloud_name,
                           **cloud_config)
            
            instances.add_cloud( cloud_name, cloud )

            logger.info("Successfully connected to the {} openStack service".format( cloud_name ))
        else:
            logger.critical( "Unknown VM backend {}".format( config.clouds[ cloud ].backend ))
            raise RuntimeError
                   
    return None


def update_node_states( max_heard_from_time:int=300 ):
    """ Update the status of nodes.

    This will update the nodes object based on information from HTcondor and the vm backends.

    Args:
      max_heard_from_time: if we have not heard from a node this long, we expect it is dead (~30 min is default)
    
    Returns:
      None

    Raises:
      None
    """

    global instances

    # Get a list of servers running on the VMs
    cloud_servers = {}
    cloud_server_name_to_id = {}
    cloud_servers_to_cloud = {}
    for cloud_name, connector in instances.get_clouds().items():
        server_list = connector.server_list()

        for server_id in server_list:
            server = server_list[ server_id ]

            cloud_servers[ server_id ] = server[ 'status']
            cloud_server_name_to_id[  server['name'] ] = server[ 'id']

            cloud_servers_to_cloud[ server_id ] = cloud_name
            

    node_count = {'idle' : 0,
                  'busy' : 0,
                  'total': 0}

    # The list of nodes known to htcondor        
    condor_nodes = condor.nodes()
    # Add the nodes known to condor if they are not already registered in the instances class
    for condor_node in condor_nodes:

        # This can happen if the server is restarted and condor
        # retains information about old nodes that have since been
        # deleted from the cloud(s)
        if ( condor_node not in cloud_server_name_to_id ):
            continue


        server_id  = cloud_server_name_to_id[ condor_node ]

        # the node is unknown to our instances, so add it
        if ( instances.find( name = condor_node ) is None):
#            print( server_id, condor_node, cloud_servers_to_cloud[ server_id ], cloud_servers[ server_id], condor_nodes[condor_node] )
            instances.add_node( id=server_id, name=condor_node, cloud=cloud_servers_to_cloud[ server_id ] , state=cloud_servers[ server_id], status=condor_nodes[condor_node] )


        instances.set_status( node_id= server_id, status=condor_nodes[condor_node])



    for node in instances.get_nodes(state=['booting', 'running', 'stopping', 'unknown']):

#        print( node )


        if node['name'] not in cloud_server_name_to_id:
            instances.set_state( node['id'], state='deleted')
            continue
        

        # these are in states that are not helpful for us, so ignore them for now
        if condor_nodes[ condor_node ] in ['suspended', 'killing', 'retiring', 'lost']:
            if ( instances.find( name = condor_node ) is not None ):
                instances.set_state( id=server_id, state='deleted' )
            continue


        if node[ 'status' ] == 'booting':
            # often htcondor knows about the server before it is fully booted up
            if node['name'] in condor_nodes:
                instances.set_state( node['id'], 'running')
            else:
                # Looking for the "server is running" keywords in the server log
                node_status = clouds[ node['cloud']].server_log_search()
                if (node_status is not None and node_status != []):
                    instances.set_status( node['id'], status='running')

        
        # Not known in the clouds or status != active, set is as deleted.
        if node['id'] not in cloud_servers or cloud_servers[ node['id']] != 'active':
            instances.set_state( node['id'], state='deleted')

        

    return instances.node_state_counts()
    
    

def delete_idle_nodes(nr:int=1, max_heard_from_time:int=300):
    """ Delete idle nodes, by default one node is deleted

    Args:
      nr: nr of nodes to delete (if possible)
      max_heard_from_time: if we have not heard from a node this long, we expect it is dead

    Returns:
      None

    Raises:
      None
    """

    global instances
    
    condor_nodes = condor.nodes( max_heard_from_time )

    # Subtract the ones that are currently stopping
    nr -= len( instances.get_nodes( status=['stopping']))

    # We have already tagged the number of nodes to be deleted so be
    # conservative and see if we still need to do this later on
    if ( nr <= 0 ):
        logger.info( 'A suitable amount of nodes are already being killed')
        return
    
    # loop through the nodes that are deletable
    for node_name in condor_nodes:
        
        node = instances.find( name = node_name )
        if ( node[ 'status' ] == 'idle' and node['state'] == 'active'):
            logger.info("Killing node {}".format( node_name ))
            
            condor.turn_off_fast( node_name )
            cloud = instances.get_cloud( node['cloud'])
            cloud.server_delete( node['id'] )

            instances.set_state( node['id'], 'stopping')
            instances.set_status( node['id'], 'retiring')

            nr -= 1
            if ( nr <= 0 ):
                return
        else:
            logger.info("Cannot kill node {} it is {}/{}".format( node_name, node['status'],node['state'] ))

            

    return


def create_execute_nodes( config:Munch,execute_config_file:str, nr:int=1):
    """ Create a number of execute nodes

    Args:
       config: config settings
       config_file: config file for node
       nr: nr of nodes to spin up (default 1)

    Returns:
      None
    
    Raises:
      RuntimeError if unknown node-allocation method
      None
    """

    global nodes
    

    for i in range(0, nr ):


#        print( config.ehos_daemon )

        # for round-robin
        ### find the next cloud name
        if ( config.ehos_daemon.node_allocation == 'round-robin'):
            clouds = list(instances.get_clouds().keys())
#            print( clouds )
            nodes_created = len( instances.get_nodes())

            if nodes_created == 0:
                cloud_name = clouds[ 0 ]
            else:
                cloud_name = clouds[ nodes_created%len( clouds )]
            
            node_name = ehos.make_node_name(config.ehos.project_prefix, "execute")
            
            cloud = instances.get_cloud( cloud_name )
            
            try:
                node_id = cloud.server_create( name=node_name,
                                               userdata_file=execute_config_file,
                                               **config.ehos )

                instances.add_node( id=node_id, name=node_name, cloud=cloud_name, status='starting')
                logger.info("Execute server {}/{} is booting".format( node_id, node_name))
                
            except Exception as e:
                logger.warning("Could not create execute server")
                logger.info("Error: {}".format(e))
#                print( execute_config_file)
#                print( config.ehos)
#                sys.exit( 1 )

        else:
            logger.critical("Unknown node allocation method ({})".format( config.ehos-daemon.node_allocation ))
            raise RuntimeError
                            

    return



# ===================== Low level generic function =====================


def get_host_ip() -> str:
    """ gets the host ip address

    Args:
      None

    returns:
      Host Ip 4 address

    Raises:
      None
    """

    
    return socket.gethostbyname(socket.getfqdn()) 



def timestamp() -> int:
    """ gets a sec since 1.1.1970

    "Args:
      None

    Returns:
      Secs since the epoc
    
    Raises:
      None
    """

    return int(time.time())


def datetimestamp() -> str:
    """ Creates a timestamp so we can make unique server names

    Args:
      none
    
    Returns:
      timestamp (string)

    Raises:
      none
    """
    ts = time.time()
    ts = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%dT%H%M%S')

    return ts


def random_string(N:int=10) -> str:
    """ Makes a random string the length of N

    Args:
      length: length of random string, default is 10 chars

    Returns:
      random string (str)

    Raises:
      None
    """

    chars=string.ascii_lowercase + string.ascii_uppercase + string.digits

    res = ""
    
    for _ in range( N ):
        res += random.SystemRandom().choice(chars)

    return res
        

def make_node_name(prefix="ehos", name='node') -> str:
    """ makes a nodename with a timestamp in it, eg: prefix-name-datetime    

    Furthermore, ensures the name will correspond to a hostname, eg making _ to -, and lowercase letters

    Args:
      prefix: prefix for name
      name: type of node, eg executer

    Returns:
      name generated

    Raises:
      None
    """

    node_name = "{}-{}-{}".format(prefix, name, datetimestamp())
    node_name = re.sub("_","-",node_name)
    node_name = node_name.lower()

    return node_name
    

def get_node_id(filename:str='/var/lib/cloud/data/instance-id') -> str:
    """ Cloud init stores the node id on disk so it possible to use this for us to get host information that way

    Ideally this would have been done using the cloud_init library, but that is python2 only, so this is a bit of a hack

    Args:
      filename: should only be changed when testing the function

    Returns:
      node id (string)
    
    Raises:
      if the instance not found raise a RuntimeError
    """

    
    if ( not os.path.isfile( filename )):
      raise RuntimeError
    

    fh = open(filename, 'r')
    id  = fh.readline().rstrip("\n")
    fh.close()

    return id

def check_config_file(config:Munch) -> bool:
    """ Check the integrity of the config file and make sure the values are valid

    The function will set defaults if values are missing and adjust incorrect values, eg spare-nodes > min-nodes

    Args:
      config: the read in config file

    Returns:
      config (Munch)

    Raises:
      Runtime error on faulty or missing settings
    """
    
    for value in ['flavor', 'base_image_id', 'network', 'key', 'security_groups']:
        
        if value not in config.ehos or config.ehos[ value ] == 'None':
            logger.fatal("{} not set or set to 'None' in the configuration file".format(value))
            raise RuntimeError


    
    defaults = {'submission_nodes': 1,
                'project_prefix': 'EHOS',
                'nodes_max': 4,
                'nodes_min': 2,
                'nodes_spare': 2,
                'sleep_min': 10,
                'sleep_max': 60}

    for value in defaults.keys():
        
        if value not in config.ehos:
            logger.warning("{} not set in configuration file, setting it to {}".format(value, defaults[ value ]))
            config.ehos[ value ] = defaults[ value ]


    if ( config.ehos.nodes_min < config.ehos.nodes_spare):
            logger.warm("configuration min-nodes smaller than spare nodes, changing min-nodes to {}".format(config.ehos.nodes_min))
            config.ehos.nodes_min = config.ehos.nodes_spare

    return True

def readin_config_file(config_file:str) -> Munch:
    """ reads in and checks the config file 

    Args:
      config_file: yaml formatted config files
    
    Returns:
      config (munch )
    
    Raises:
      None
    """

    with open(config_file, 'r') as stream:
        config = Munch.fromYAML(stream)
        stream.close()

    return config


def readin_whole_file(filename:str) -> str:
    """ reads in a whole file as a single string

    Args:
      filename: name of file to read

    Returns
      file contents (str)

    Raises:
      None
    """

    with open( filename, 'r') as fh:
        lines = "".join(fh.readlines())
        fh.close()
    
    return lines

    
def find_config_file( filename:str, dirs:List[str]=None) -> str:
    """ Depending on the setup the location of config files might change. This helps with this, first hit wins!

    The following location are used by default: /etc/ehos/, /usr/local/etc/ehos, /usr/share/ehos/, configs/

    Args:
      filename: file to find
      dirs: additional list of directories to search through

    Return:
      Full path to the file (str)

    Raises:
      RuntimeError if file not found
    """

    script_dir = os.path.dirname(os.path.abspath( filename))

    default_dirs = ['/etc/ehos/',
                    '/usr/local/etc/ehos',
                    '/usr/share/ehos/',
                    '/usr/local/share/ehos/',
                    "{}/../configs".format( script_dir ),
                    'configs',
                    './']

    
    if dirs is not None:
        dirs += default_dirs
    else:
        dirs = default_dirs
        
    for dir in dirs:
        full_path = "{}/{}".format( dir, filename)
        if os.path.isfile(full_path):
            return full_path

    raise RuntimeError("File {} not found".format( filename ))

def alter_file(filename:str, pattern:str=None, replace:str=None, patterns:List[ Tuple[ str, str]]=None, outfile:str=None):
    """ Alter a file by searching for a pattern (str or regex) and replace it

    The function further more make a backup copy of the original file

    Args:
      filename: The file to change
      pattern: the pattern (str/regex) to search for in the file
      replace: what to replace the pattern with
      patterns: a list of replacements to be done
      outfile: alternative file to write to, will not create a backup of the original file

    Returns:
      None

    Raises:
      RuntimeError if no pattern

    """

    # this is foobared but I cannot find the strength to do this right 
    if ( pattern is None and
         replace is None and
         patterns is None):


        #  or

        #  ( patterns is not None and
        #    (pattern is not None or
        #     replace is not None))

        # or
        
        #  ( pattern is None or
        #    replace is None )):
        
        raise RuntimeError('Wrong use of alter_file function parameters, provide either a pattern and a replace or a list of patterns')
    
    # first make a copy of the file

    if ( outfile is None ):
        shutil.copy( filename, "{}.original".format( filename ))
    
    # open and read in the while file as a single string
    with open( filename, 'r') as fh:
        lines = "".join(fh.readlines())
        fh.close()

    if patterns is None:
        patterns = [ (pattern, replace) ]

    for pattern, replace in patterns:
#        print( pattern, " ---> ", replace )
        # replace the pattern with the replacement string
        lines = re.sub(pattern, replace, lines)

    if ( outfile is None ):

        with  open(filename, 'w') as fh:
            fh.write( lines )
            fh.close()
    else:
        with  open(outfile, 'w') as fh:
            fh.write( lines )
            fh.close()
        


def log_level(new_level:int) -> int:
    """ Set the log level, value is forced with in the [1-5] range

    levels correspond to: DEBUG=5,  INFO=4 WARN=3, ERROR=2 and CRITICAL=1

    Args:
      level: when to report

    Returns:
      None

    Raises:
      None

    """
    if new_level < 1:
        new_level = 1
    elif new_level > 5:
        new_level = 5

    if new_level   == 1:
        logging.basicConfig(level=logging.CRITICAL)
    elif new_level == 2:
        logging.basicConfig(level=logging.ERROR)
    elif new_level == 3:
        logging.basicConfig(level=logging.WARNING)
    elif new_level == 4:
        logging.basicConfig(level=logging.INFO)
    elif new_level == 5:
        logging.basicConfig(level=logging.DEBUG)
        

    return new_level
        
def system_call(command:str) -> int:
    """ runs a system command

    Args:
      command to run

    Returns:
      None

    Raises:
      None
    
    """

    return(subprocess.call(shlex.split( command ), shell=False))
        
        

def make_uid_domain_name(length:int=3):
    """ Makes a 'random' uid domain name

    Args:
      length: domain length
    
    Returns:
      uid domain name (str)

    Raises:
      RuntimeError if length is longer than our word list

    """

    quote = "Piglet was so excited at the idea of being Useful that he forgot to be frightened any more, and when Rabbit went on to say that Kangas were only Fierce during the winter months, being at other times of an Affectionate Disposition, he could hardly sit still, he was so eager to begin being useful at once"

#    quote = "The more he looked inside the more Piglet wasnt there"
    quote = re.sub(",", "", quote);

    words = list(set( quote.lower().split(" ")))

    if (len(words) < length):
        raise RuntimeError( 'length required is longer than dictonary used')
        
    choices = []
    while( True ):
        word = random.choice(words)

        if word in choices:
            continue
            
        choices.append( word )

        if (len( choices ) == length):
            break
        
    return('.'.join(choices))



