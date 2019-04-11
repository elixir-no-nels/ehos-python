#!/usr/bin/env python3
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
import random

from munch import Munch

import ehos.log_utils as logger

# Not sure if this is still needed.
import logging
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('keystoneauth').setLevel(logging.CRITICAL)
logging.getLogger('stevedore').setLevel(logging.CRITICAL)
logging.getLogger('concurrent').setLevel(logging.CRITICAL)
logging.getLogger('openstack').setLevel(logging.CRITICAL)
logging.getLogger('dogpile').setLevel(logging.CRITICAL)




condor    = None
instances = None

def init(condor_init:bool=True):
    """ init function for the module, connects to the htcondor server and sets up the instance tracking module

    Args:
      condor_init: wether to init the condor module or not.
    
    Returns:
      None
    
    Raises:
      None
    """

    # Some odd bug as the name space gets polluted when I install the module multiple times
    import ehos.instances as I

    global condor
    global instances


    if ( condor_init ):
        import ehos.htcondor 
        condor  = ehos.htcondor.Condor()

    instances = I.Instances()

    
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

    import ehos.openstack

    for cloud_name in config.clouds:

        config.clouds[ cloud_name ].backend = 'openstack'
        
        # Ignore the backend setting, as we only support openstack right now.
        if ( 1 or config.clouds[ cloud_name ].backend == 'openstack'):

            cloud_config = config.clouds[ cloud_name ]

            cloud = ehos.openstack.Openstack()
            cloud.connect( cloud_name=cloud_name,
                           **cloud_config)

            instances.add_cloud( cloud_name, cloud )
            logger.debug("Successfully connected to the {} openStack service".format( cloud_name ))

        else:
            logger.critical( "Unknown VM backend {}".format( config.clouds[ cloud ].backend ))
            raise RuntimeError( "Unknown VM backend {}".format( config.clouds[ cloud ].backend ))
                   
    return None


def get_cloud_connector( name:str):
    """ returns the connector for the cloud, mainly used for debugging 

    Args:
      name of cloud to return connector for

    Returns:
      connector object for cloud

    Raises:
      None
    """

    return instances.get_cloud( name )


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

#    for node in instances.get_nodes(state=['booting', 'active', 'stopping', 'unknown']):
    for node in instances.get_nodes():

#        print( node )

        # Not known in the clouds or status != active, set is as deleted.
        if node['id'] not in cloud_servers or cloud_servers[ node['id']] != 'active':
            instances.set_state( node['id'], state='deleted')
            instances.set_status( node['id'], status='lost')

        # these are in states that are not helpful for us, so ignore them for now
        elif node['state' ] in ['suspended', 'killing', 'retiring', 'lost']:
            if ( instances.find( name = condor_node ) is not None ):
                instances.set_state( node_id=server_id, state='deleted' )
                instances.set_status( node['id'], status='lost')
            continue

        elif node[ 'state' ] == 'booting':
            # often htcondor knows about the server before it is fully booted up
            if node['name'] in condor_nodes:
                instances.set_state( node['id'], 'active')
#            else:
                # Looking for the "server is running" keywords in the server log
#                node_status = clouds[ node['cloud']].server_log_search()
#                if (node_status is not None and node_status != []):
#                    instances.set_status( node['id'], status='running')
        else:
            instances.set_state( node['id'], 'active')
            
            
        

        

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
    nr -= len( instances.get_nodes( state=['stopping']))

    # We have already tagged the number of nodes to be deleted so be
    # conservative and see if we still need to do this later on
    if ( nr <= 0 ):
        logger.debug( 'A suitable amount of nodes are already being killed')
        return
    
    # loop through the nodes that are deletable
    for node_name in condor_nodes:
        
        node = instances.find( name = node_name )
        if node is None:
            continue

#        if node_name != 'ehos-v1-execute-20181107t071902':
#            continue
        
#        print( node )
        if ( node[ 'status' ] == 'idle' and node['state'] in ['active', 'booting']):
            logger.debug("Killing node {}".format( node_name ))
            
            condor.turn_off_fast( node_name )
            cloud = instances.get_cloud( node['cloud'])
            
            volumes = cloud.volumes_attached_to_server(node['id'])
            cloud.detach_volumes_from_server(node['id'])

            for volume in volumes:
            
                cloud.volume_delete( volume )
            
            
            cloud.server_delete( node['id'] )

            instances.set_state( node['id'], 'stopping')
            instances.set_status( node['id'], 'retiring')

            nr -= 1
            if ( nr <= 0 ):
                return
        else:
            logger.debug("Cannot kill node {} it is {}/{}".format( node_name, node['status'],node['state'] ))

            

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

    nr = 1

    node_names = []


    for i in range(0, nr ):

        cloud_name = None
        clouds = list(instances.get_clouds().keys())

        clouds_usable = []
        
        for cloud_name in clouds:
            cloud = instances.get_cloud( cloud_name )
            resources = cloud.get_resources_available()
            if ( resources['ram'] > config.ehos_daemon.min_ram*1024 and
                 resources['cores'] > config.ehos_daemon.min_cores and
                 resources['instances'] > config.ehos_daemon.min_instances ):
                clouds_usable.append( cloud_name )

        clouds = clouds_usable
                
        if ( clouds == []):
            logger.warn('No resources available to make a new node')
            
                

        
        # for round-robin
        ### find the next cloud name
        if ( config.ehos_daemon.node_allocation == 'round-robin'):

            nodes_created = len( instances.get_nodes())

            if nodes_created == 0:
                cloud_name = clouds[ 0 ]
            else:
                cloud_name = clouds[ nodes_created%len( clouds )]
            
            node_name = make_node_name(config.ehos.project_prefix, "execute")

        elif ( config.ehos.deamon.node_allocation == 'random'):
            cloud_name = random.choice( clouds )
        elif (  config.ehos.deamon.node_allocation == 'fill first'):
            cloud_name = clouds[ 0 ]

        else:
            logger.critical("Unknown node allocation method ({})".format( config.ehos-daemon.node_allocation ))
            raise RuntimeError("Unknown node allocation method ({})".format( config.ehos-daemon.node_allocation ))


        cloud = instances.get_cloud( cloud_name )

        logger.debug( "Using image {}".format( config.clouds[ cloud_name ].image ))
        
        try:
            config.ehos.image= config.clouds[ cloud_name ].image
            
            node_id = cloud.server_create( name=node_name,
                                           userdata_file=execute_config_file,
                                           **config.ehos )

            if ( 'scratch_size' in config.ehos and
                 config.ehos.scratch_size is not None and
                 config.ehos.scratch_size != 'None'):

                try:
                    volume_id = cloud.volume_create(size=config.ehos.scratch_size, name=node_name)
                    cloud.attach_volume( node_id, volume_id=volume_id)
                except:
                    logger.warning("Could not create execute server, not enough disk available, deleting the instance.")
                    cloud.server_delete( node_id )

                    
            instances.add_node( id=node_id, name=node_name, cloud=cloud_name, status='starting', state='booting')
            logger.debug("Execute server {}/{} is booting".format( node_id, node_name))
            node_names.append(node_name)

        except Exception as e:
            logger.warning("Could not create execute server")
            logger.debug("Error: {}".format(e))

                            

    return node_names





def create_images( config:Munch,config_file:str, delete_original:bool=False):
    """ Create a number of images to be used later to create nodes

    Args:
       config: config settings
       config_file: config file for base system
       delete_original, delete the server after image creation

    Returns:
      dict of cloud-name : image-id
    
    Raises:
      RuntimeError if unknown node-allocation method
    """

    clouds = list(instances.get_clouds().keys())

    images = {}
    
    for cloud_name in clouds:
        cloud = instances.get_cloud( cloud_name )

        logger.info("Creating base server in cloud '{}'".format( cloud_name ))

        node_name = make_node_name(config.ehos.project_prefix, "base")


        resources = cloud.get_resources_available()
        if ( resources['ram'] > config.ehos_daemon.min_ram*1024 and
             resources['cores'] > config.ehos_daemon.min_cores and
             resources['instances'] > config.ehos_daemon.min_instances ):

            vm_id = cloud.server_create( name=node_name,
                                         userdata_file=config_file,
                                         **config.ehos )

        
            logger.info("Created vm server, waiting for it to come online")


            # Wait for the server to come online and everything have been configured.    
            cloud.wait_for_log_entry(vm_id, "The EHOS vm is up after ")
            logger.info("VM server is now online")
            
            image_name = make_node_name(config.ehos.project_prefix, "image")
            image_id = cloud.make_image_from_server( vm_id,  image_name )
            
            logger.info("Created image {} from {}".format( image_name, node_name ))
            
            images[ cloud_name ] = image_id

            if ( delete_original):
                cloud.server_delete( vm_id )
        else:
            logger.warn("Not enough resources available in '{}'  to create VM".format( cloud_name))
            images[ cloud_name ] = None

                
    return images


def create_master_node( config:Munch,master_file:str):
    """ Create a number of images to be used later to create nodes

    Args:
       config: config settings
       master_file: config file for master node
       execute_file: config file for execute nodes

    Returns:
      the master_id (uuid)
    
    Raises:
      RuntimeError if unknown node-allocation method
    """

    clouds = list(instances.get_clouds().keys())

    if len (clouds ) == 1:
        logger.debug( "only one cloud configured, will use that for the master node regardless of configuration")
        config.ehos_daemon.master_cloud = clouds[ 0 ]
        
    if 'master_cloud' not in config.ehos_daemon or config.ehos_daemon == 'None':
        logger.fatal( "Cloud instance for hosting the master node is not specified in the config file")
        sys.exit( 2 )
    
    cloud_name = config.ehos_daemon.master_cloud

    if ( cloud_name not in clouds):
        print( "Unknown cloud instance {}, it is not found in the config file".format( cloud_name ))

    cloud = instances.get_cloud( cloud_name )

    master_name = make_node_name(config.ehos.project_prefix, "master")

    config.ehos.image = config.clouds[ cloud_name ].image
    
    master_id = cloud.server_create( name=master_name,
                                     userdata_file=master_file,
                                     **config.ehos )

        
    logger.info("Created master node, waiting for it to come online. This can take upto 15 minutes")

    
    # Wait for the server to come online and everything have been configured.    
    cloud.wait_for_log_entry(master_id, "The EHOS vm is up after ", timeout=1300)
    logger.info("Master node is now online")

    logger.info( "Master IP addresse is {}".format( cloud.server_ip( master_id )))
    

    return master_id, cloud.server_ip( master_id )




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


def get_host_name() -> str:
    """ gets the host name

    Args:
      None

    Returns:
      full host name

    Raises:
      None
    """
    return socket.getfqdn()


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
      raise RuntimeError("instance file ({}) does not exists".format( filename))
    

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
            raise RuntimeError("{} not set or set to 'None' in the configuration file".format(value))


    
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
      config ( munch )
    
    Raises:
      None
    """

    with open(config_file, 'r') as stream:
        config = Munch.fromYAML(stream)
        stream.close()

    if 'hostname' not in config.ehos_daemon:
        config.ehos_daemon.hostname = get_host_name()

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
                    "{}/../etc".format( script_dir ),
                    'etc/',
                    'etc/ehos',
                    '/usr/share/ehos/',
                    '/usr/local/share/ehos/',
                    "{}/../share".format( script_dir ),
                    'share/',
                    'share/ehos',
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

