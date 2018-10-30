#!/usr/bin/python3
# 
# 
# 
# 
# Kim Brugger (20 Sep 2018), contact: kim@brugger.dk

import os
import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)
import time
import datetime
import argparse
import re
import tempfile
import traceback

import logging
logger = logging.getLogger('ehosd')


# python3+ is broken on centos 7, so add the /usr/local/paths by hand
sys.path.append("/usr/local/lib/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))
sys.path.append("/usr/local/lib64/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))

from munch import Munch

import ehos
import ehos.openstack as openstack

nodes_deleted = []
nodes_starting = []
node_names = {}

nodes_created = 0
clouds = []


def connect_to_clouds(config:Munch) -> []:
    """ Connects to the clouds spefified in the config file

    Args:
      config: from the yaml input file
    
    Returns:
      connection names (list)

    Raises:
      RuntimeError if unknown backend
    """

    clouds = {}
    for cloud_name in config.clouds:

        if ( config.clouds[ cloud ].backend == 'openstack'):

            clouds[ cloud_name ] = openstack.Openstack()

            clouds[ cloud_name ].connect( cloud_name=cloud,
                                          auth_url=config.clouds[cloud].auth.auth_url ,
                                          user_domain_name=config.clouds[cloud].user_domain_name,
                                          project_domain_name=config.clouds[cloud].project_domain_name,
                                          username=config.clouds[cloud].auth.username,
                                          password=config.clouds[cloud].auth.password,
                                          project_name=config.clouds[cloud].auth.project_name,
                                          region_name=config.clouds[cloud].region_name,
                                          no_cache=1,)


            
            logger.info("Connected to the {} openStack".format(cloud))
        else:
            print( "Unknown VM backend {}".format( config.clouds[ cloud ].backend ))
            raise RuntimeError
                   
            

    return clouds


def create_execute_config_file(master_ip:str, uid_domain:str, password:str, outfile:str='/usr/local/etc/ehos/execute.yaml', execute_config:str=None):
    """ Create a execute node config file with the master ip and pool password inserted into it

    Args:
      master_ip: ip of the master to connect to
      uid_domain: domain name we are using for this
      password: for the cloud
      outfile: file to write the execute file to
      execute_config: define config template, otherwise find it in the system

    Returns:
      file name with path (str)

    Raises:
      None

    """

    if ( execute_config is None):
        execute_config = ehos.find_config_file('execute.yaml')
    
    print("outfile: '{}".format(outfile))
        
    ehos.alter_file(execute_config, outfile=outfile, patterns=[ (r'{master_ip}',master_ip),
                                                                (r'{uid_domain}', uid_domain),
                                                                (r'{password}',password)])
                                                

    return outfile

def check_execute_nodes_booted():
    """ Remove already booted nodes from the execute tracker

    Args:
      None

    Return:
      None

    Raises:
      None
    """
 
    logger.debug("Check the state of nodes booting")
    
    global nodes_starting
    for node in nodes_starting:
        node_status = ehos.server_log_search( node )
        if (node_status is not None and node_status != []):
            nodes_starting.remove( node )
            logger.info("node {} is now up and running".format( node ))
    

def delete_idle_nodes(collector, nodes:int=1, max_heard_from_time:int=300):
    """ Delete idle nodes, by default one node is delete

    Args:
      collector: htcondor collector object
      nodes: nr of nodes to delete (if possible)
      max_heard_from_time: if we have not heard from a node this long, we expect it is dead

    Returns:
      None

    Raises:
      None
    """

    node_states = get_node_states(collector, max_heard_from_time)

    global nodes_deleted

    # get all nodes that are deletable
    idle_nodes = []
    for node_name in node_states:
        if ( node_states[ node_name ] == 'idle'):

            idle_nodes.append( node_name )

    # check if any are already shutting down and/or idle
    nodes_already_shutting_down = 0
    for idle_node in idle_nodes:
        if idle_node in nodes_deleted:
            nodes_already_shutting_down += 1


    # adjust the number we are to shutdown
    nodes -= nodes_already_shutting_down

    
    for node_name in idle_nodes:
        # check if enough nodes have bee killed already
        if not nodes or nodes < 0:
            return
        try:
            nodes_deleted.append( node_name )
            # This makes housekeeping of deleted nodes easier. Otherwise it can take upto 30 min for the node to be recorded as deleted.
            condor_turn_off_fast( node_name )
            ehos.server_delete( node_name )
        except Exception:
            logger.info( "{} is no longer available for deletion".format(node_name ))
            nodes_deleted.append( node_name )

        nodes -= 1


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
      None
    """

    global nodes_starting
    global nodes_created
    

    for i in range(0, nr ):


        # for round-robin
        ### find the next cloud name
        cloud_name = clouds[ nodes_created%len( clouds )]
        nodes_created += 1

        node_name = ehos.make_node_name(config.ehos.project_prefix, "execute")

        cloud = clouds[ cloud_name ]
        
        try:
            node_id = cloud.server_create( node_name,
                                           image=config.clouds[ cloud_name].ehos.base_image_id,
                                           flavor=config.clouds[ cloud_name].ehos.flavor,
                                           network=config.clouds[ cloud_name].ehos.network,
                                           key=config.clouds[ cloud_name].ehos.key,
                                           security_groups=config.clouds[ cloud_name].ehos.security_groups,
                                           userdata_file=execute_config_file)


            node_names[ node_id ] = node_name
            nodes_starting.append( node_id )
            logger.info("Execute server is booting")
        except Exception as e:
            logger.warning("Could not create execute server")
            logger.info("Error: {}".format(e))
            

    return
                    


def run_daemon( config_file:str="/usr/local/etc/ehos_master.yaml" ):
    """ Creates the ehos daemon loop that creates and destroys nodes etc.
               
    The confirguration file is continously read so it is possible to tweak the behaviour of the system
               
    Args:
      init_file: alternative config_file

    Returns:
      None

    Raises:
      None
    """


    host_id    = ehos.get_node_id()
    host_ip    = ehos.server_ip( host_id, 4)
    uid_domain = ehos.make_uid_domain_name(5)

    ip_range = re.sub(r'(\d+\.\d+\.\d+\.)\d+', r'\1*', host_ip)

    config = ehos.readin_config_file( config_file )

    
    clouds = connect_to_clouds( config )
    
    # first time running this master, so tweak the personal configureation file
    if ( os.path.isfile( '/etc/condor/00personal_condor.config')):

         ehos.alter_file(filename='/etc/condor/00personal_condor.config', patterns=[ (r'{master_ip}',host_ip),
                                                                                     (r'{uid_domain}',uid_domain),
                                                                                     (r'{ip_range}', ip_range)])

         os.rename('/etc/condor/00personal_condor.config', '/etc/condor/config.d/00personal_condor.config')

         # re-read configuration file
         htcondor.reload_config()

    htcondor_security.setPoolPassword( config.condor.password )

    execute_config_file = create_execute_config_file( host_ip, uid_domain, config.condor.password )
#    sys.exit( 1 )
    
    while ( True ):

        config = ehos.readin_config_file( config_file )

        
        # get the current number of nodes
        nodes  = nodes_status(htcondor_collector)
        queue  = queue_status(htcondor_schedd)

        
        logger.debug( "Node data\n" + pp.pformat( nodes ))
        logger.debug( "Queue data\n" + pp.pformat( queue ))

        logger.info("Nr of nodes {} ({} are idle)".format( nodes.total, nodes.idle))
        logger.info("Nr of jobs {} ({} are queueing)".format( queue.total, queue.idle))

        
        # Below the min number of nodes needed for our setup
        if ( nodes.total < config.ehos.nodes_min ):
            logger.info("We are below the min number of nodes, creating {} nodes".format( config.ehos.nodes_min - nodes.total))

            create_execute_nodes(config, execute_config_file, config.ehos.nodes_min - nodes.total)

        ### there are jobs queuing, let see what we should do

        # got jobs in the queue but less than or equal to our idle + spare nodes, do nothing
        elif (  queue.idle and queue.idle <= nodes.idle ):
            logger.info("We got stuff to do, but seems to have enough nodes to cope...")

        # Got room to make some additional nodes
        elif (  queue.idle and nodes.total + config.ehos.nodes_spare <= config.ehos.nodes_max ):
            
            logger.info("We got stuff to do, creating some additional nodes...")

            create_execute_nodes(config, execute_config_file, config.ehos.nodes_max - nodes.total )

        # this one is just a sanity one
        elif ( queue.idle and nodes.total == config.ehos.nodes_max):
            logger.info("We are busy. bu all nodes we are allowed have been created, nothing to do")


        ### Looks like we have an excess of nodes, lets cull some

        # We got extra nodes not needed and we can delete some without going under the min cutoff, so lets get rid of some
        elif ( nodes.total > config.ehos.nodes_min and
               nodes.idle  > config.ehos.nodes_spare ):

            nr_of_nodes_to_delete = min( nodes.total - config.ehos.nodes_min, nodes.idle - config.ehos.nodes_spare)
            
            logger.info("Deleting {} idle nodes...".format( nr_of_nodes_to_delete))
            delete_idle_nodes(htcondor_collector,  nr_of_nodes_to_delete)
            
        else:
            logger.info("The number of execute nodes are running seem appropriate, nothing to change.")

        logger.info("Napping for {} second(s).".format(config.ehos.sleep_min))
        time.sleep( config.ehos.sleep_min)


        
def main():
    """ main loop

    Args:
      None
    
    Returns:
      None
    
    Raises: 
      None
    """

    parser = argparse.ArgumentParser(description='ehosd: the ehos daemon to be run on the master node ')

    parser.add_argument('-v', '--verbose', default=1, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('config_file', metavar='config-file', nargs='?',    help="yaml formatted config file", default=[ehos.find_config_file('ehos.yaml')])


    args = parser.parse_args()

    # as this is an array, and we will ever only get one file set it
    args.config_file = args.config_file[ 0 ]


    ehos.log_level( args.verbose )
    logger.info("Running with config file: {}".format( args.config_file))

    config = ehos.readin_config_file( config_file )

    if ( args.config_file):
        run_daemon( args.config_file )
    else:
        run_daemon(  )



def node_states(self, max_heard_from_time:int=300 ):
    """get the states of nodes

    Available states are: idle, busy, suspended, vacating, killing, benchmarking, retiring

    Args:
      max_heard_from_time: if we have not heard from a node this long, we expect it is dead

    Returns:
      node states ( dict )

    Raises:
      None

    """

    _node_states = {}

    global nodes_deleted
    global nodes_starting

    check_execute_nodes_booted()
    for node in nodes_starting:
        _node_states[ node_names[ node ] ] = 'starting'

    timestamp = ehos.timestamp()

    server_list = ehos.server_list()

    for node in collector.query(htcondor.AdTypes.Startd):

        name = node.get('Name')
        print("name: '{}'".format( name ))

        # trim off anything after the first . in the string
        if ("." in name):
            name = re.sub(r'(.*?)\..*', r'\1', name)

        slot = None
        host = name
        if "@" in name:
            (slot, host) = name.split("@")


        logger.debug("Node info: node:{} state:{} Activity:{} last seen:{} secs".format( name, node.get('State'), node.get('Activity'),timestamp - node.get('LastHeardFrom')))

        if host in nodes_deleted:
            continue

        # See if the server exists in the openstack list
        if( host not in server_list ):
            logger.info( "-- >> Node {} not in the server_list, set is as deleted ".format( host ))
            nodes_deleted.append( host )
            continue

        # When was the last time we heard from this node? Assume dead?
        if ( timestamp - node.get('LastHeardFrom') > max_heard_from_time):
            logger.info( "Seems to have lost the connection to {} (last seen {} secs ago)".format( name, timestamp - node.get('LastHeardFrom')))
            nodes_deleted.append( name )
            continue


        # This is a bit messy, a node can have child slots, so the
        # counting gets wrong if we look at all node entries.
        #
        # The way to solve this, for now?, is if a node has a child entry
        # (eg: slot1_1@hostname) this takes predicent over the main entry.

        if ( host in _node_states ):
            if ( "_" in name):
                _node_states[ host ] = node.get('Activity').lower()
        else:
            _node_states[ host ] = node.get('Activity').lower() 



    logger.debug("Node states: \n{}".format( pp.pformat(_node_states)))

    return _node_states

        

if __name__ == '__main__':
    main()
else:
    print("Not to be run as a library")
    sys.exit( 1 )
          
    
