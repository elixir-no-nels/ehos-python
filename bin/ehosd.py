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

# python3+ is broken on centos 7, so add the /usr/local/paths by hand
sys.path.append("/usr/local/lib/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))
sys.path.append("/usr/local/lib64/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))



from munch import Munch


import htcondor
import openstack

import ehos


nodes_deleted = []
nodes_starting = []
node_names = {}

def queue_status(schedd):
    """get the number of jobs in the queue and group them by status

    The following are the states a job can be in:
      idle, running, removed0, completed, held, transferring_output, suspended

    Args:
      schedd: htcondor schedd connector

    Returns:
      counts of jobs in states ( dict )

    Raises:
      None

    """


    status_codes = {1: 'idle',
                    2: 'running',
                    3: 'removed',
                    4: 'completed',
                    5: 'held',
                    6: 'transferring_output',
                    7: 'suspended'}

    
    status_counts = {'idle': 0,
                     'running': 0,
                     'removed': 0,
                     'completed': 0,
                     'held': 0,
                     'transferring_output': 0,
                     'suspended': 0,
                     'total': 0}


    for job in schedd.xquery(projection=['ClusterId', 'ProcId', 'JobStatus']):
        status_counts[ status_codes[  job.get('JobStatus') ]] += 1
        status_counts[ 'total' ] += 1

    return Munch(status_counts)
        

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
 
    ehos.verbose_print("Check the state of nodes booting", ehos.DEBUG)
    
    global nodes_starting
    for node in nodes_starting:
        node_status = ehos.server_log_search( node, "The EHOS execute node is")
        if (node_status is not None and node_status != []):
            nodes_starting.remove( node )
            ehos.verbose_print("node {} is now up and running".format( node ), ehos.INFO)
    

            

def get_node_states(collector, max_heard_from_time:int=300 ):
    """get the states of nodes
    
    Available states are: idle, busy, suspended, vacating, killing, benchmarking, retiring

    Args:
      collector: htcondor collector object
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

        
        ehos.verbose_print("Node info: node:{} state:{} Activity:{} last seen:{} secs".format( name, node.get('State'), node.get('Activity'),timestamp - node.get('LastHeardFrom')), ehos.DEBUG+2)

        if host in nodes_deleted:
            continue

        # See if the server exists in the openstack list
        if( host not in server_list ):
            ehos.verbose_print( "-- >> Node {} not in the server_list, set is as deleted ".format( host ), ehos.INFO)
            nodes_deleted.append( host )
            continue

        # When was the last time we heard from this node? Assume dead?
        if ( timestamp - node.get('LastHeardFrom') > max_heard_from_time):
            ehos.verbose_print( "Seems to have lost the connection to {} (last seen {} secs ago)".format( name, timestamp - node.get('LastHeardFrom')), ehos.INFO)
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
            

            
    ehos.verbose_print("Node states: \n{}".format( pp.pformat(_node_states)), ehos.DEBUG )
            
    return _node_states
            

def nodes_status(collector, max_heard_from_time:int=300 ):
    """get the nodes connected to the master and groups them by status
    
    Available states are: idle, busy, suspended, vacating, killing, benchmarking, retiring

    Args:
      collector: htcondor collector object
      max_heard_from_time: if we have not heard from a node this long, we expect it is dead

    Returns:
      counts of nodes in states ( dict )

    Raises:
      None

    """


    node_counts = {"idle": 0,
                   "starting": 0,
                   "busy": 0,
                   "suspended": 0,
                   "vacating": 0,
                   "killing": 0,
                   "benchmarking": 0,
                   "retiring": 0,
                   "total": 0}


    node_states = get_node_states(collector, max_heard_from_time)
    
    for node in node_states.keys():
        
        node_counts[ node_states[ node] ] += 1
        node_counts['total'] += 1

    return Munch(node_counts)



def condor_turn_off_fast(name:str):
    """ Turns off a startd daemon as defined by name

    Ideally this should be done by an API call but this "feature" is undocumented

    Args:
      name: name of node to turn off

    Returns:
      None

    Raises:
      None

    """
    ehos.system_call("condor_off -fast {}".format(name))
#    node = collector.locate(htcondor.DaemonTypes.Master, name=name)

#    htcondor.send_command( n, htcondor.DaemonCommands.DaemonOffFast)



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
            ehos.verbose_print( "{} is no longer available for deletion".format(node_name ), ehos.INFO)
            nodes_deleted.append( node_name )

        nodes -= 1


    return


def check_config_file(config:Munch):
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
            ehos.verbose_print("{} not set or set to 'None' in the configuration file".format(value), ehos.FATAL)
            sys.exit(1)


    
    defaults = {'submission_nodes': 1,
                'project_prefix': 'EHOS',
                'nodes_max': 4,
                'nodes_min': 2,
                'nodes_spare': 2,
                'sleep_min': 10,
                'sleep_max': 60}

    for value in defaults.keys():
        
        if value not in config.ehos:
            ehos.verbose_print("{} not set in configuration file, setting it to {}".format(value, defaults[ value ]), ehos.WARN)
            config.ehos[ value ] = defaults[ value ]


    if ( config.ehos.nodes_min < config.ehos.nodes_spare):
            ehos.verbose_print("configuration min-nodes smaller than spare nodes, changing min-nodes to {}".format(config.ehos.nodes_min), ehos.WARN)
            config.ehos.nodes_min = config.ehos.nodes_spare
        

def readin_config_file(config_file:str) -> Munch:
    """ reads in and checks the config file 

    Args:
      config_file: yaml formatted config files
    
    Returns:
      config (munch )
    
    Raises:
      None
    """

    # Continuously read in the config file making it possible to tweak the server as it runs. 
    with open(config_file, 'r') as stream:
        config = Munch.fromYAML(stream)
        stream.close()

        check_config_file(config)


    return config
        

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
    

    for i in range(0, nr ):

        node_name = "{}-node-{}".format(config.ehos.project_prefix, ehos.datetimestamp())


        # print( " - ".join( map( str, [node_name,
        #                               config.ehos.base_image_id,
        #                               config.ehos.flavor,
        #                               config.ehos.network,
        #                               config.ehos.key,
        #                               config.ehos.security_groups,
        #                               execute_config_file])))


        
        try:
            node_id = ehos.server_create( node_name,
                                          image=config.ehos.base_image_id,
                                          flavor=config.ehos.flavor,
                                          network=config.ehos.network,
                                          key=config.ehos.key,
                                          security_groups=config.ehos.security_groups,
                                          userdata_file=execute_config_file)


            node_name = re.sub("_","-",node_name).lower()
            node_names[ node_id ] = node_name
            nodes_starting.append( node_id )
            ehos.verbose_print("Execute server is booting",  ehos.INFO)
        except Exception as e:
            ehos.verbose_print("Could not create execute server",  ehos.WARN)
            ehos.verbose_print("Error: {}".format(e),  ehos.INFO)
            

    return
                    


def run_daemon(config_file:str="/usr/local/etc/ehos_master.yaml", logfile:str=None):
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

    config = readin_config_file( config_file )

    # get some handles into condor, should perhaps wrap them in a module later on
    htcondor_collector = htcondor.Collector()
    htcondor_schedd    = htcondor.Schedd()

    htcondor_security  = htcondor.SecMan()

    
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

        config = readin_config_file( config_file )

        
        # get the current number of nodes
        nodes  = nodes_status(htcondor_collector)
        queue  = queue_status(htcondor_schedd)

        
        ehos.verbose_print( "Node data\n" + pp.pformat( nodes ), ehos.DEBUG)
        ehos.verbose_print( "Queue data\n" + pp.pformat( queue ), ehos.DEBUG)

        ehos.verbose_print("Nr of nodes {} ({} are idle)".format( nodes.total, nodes.idle), ehos.INFO)
        ehos.verbose_print("Nr of jobs {} ({} are queueing)".format( queue.total, queue.idle), ehos.INFO)

        
        # Below the min number of nodes needed for our setup
        if ( nodes.total < config.ehos.nodes_min ):
            ehos.verbose_print("We are below the min number of nodes, creating {} nodes".format( config.ehos.nodes_min - nodes.total) , ehos.INFO)

            create_execute_nodes(config, execute_config_file, config.ehos.nodes_min - nodes.total)

        ### there are jobs queuing, let see what we should do

        # got jobs in the queue but less than or equal to our idle + spare nodes, do nothing
        elif (  queue.idle and queue.idle <= nodes.idle ):
            ehos.verbose_print("We got stuff to do, but seems to have enough nodes to cope...", ehos.INFO)

        # Got room to make some additional nodes
        elif (  queue.idle and nodes.total + config.ehos.nodes_spare <= config.ehos.nodes_max ):
            
            ehos.verbose_print("We got stuff to do, creating some additional nodes...", ehos.INFO)

            create_execute_nodes(config, execute_config_file, config.ehos.nodes_max - nodes.total )

        # this one is just a sanity one
        elif ( queue.idle and nodes.total == config.ehos.nodes_max):
            ehos.verbose_print("We are busy. bu all nodes we are allowed have been created, nothing to do", ehos.INFO)


        ### Looks like we have an excess of nodes, lets cull some

        # We got extra nodes not needed and we can delete some without going under the min cutoff, so lets get rid of some
        elif ( nodes.total > config.ehos.nodes_min and
               nodes.idle  > config.ehos.nodes_spare ):

            nr_of_nodes_to_delete = min( nodes.total - config.ehos.nodes_min, nodes.idle - config.ehos.nodes_spare)
            
            ehos.verbose_print("Deleting {} idle nodes...".format( nr_of_nodes_to_delete), ehos.INFO)
            delete_idle_nodes(htcondor_collector,  nr_of_nodes_to_delete)
            
        else:
            ehos.verbose_print("The number of execute nodes are running seem appropriate, nothing to change.", ehos.INFO)

        ehos.verbose_print("Napping for {} second(s).".format(config.ehos.sleep_min), ehos.INFO)
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

    parser = argparse.ArgumentParser(description='ehosd: the ehos daemon to be run on the HTcondor master node ')

    parser.add_argument('-v', '--verbose', default=1, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('config_file', metavar='config-file', nargs='?',    help="yaml formatted config file", default=[ehos.find_config_file('ehos.yaml')])


    args = parser.parse_args()

    # as this is an array, and we will ever only get one file set it
    args.config_file = args.config_file[ 0 ]


    ehos.verbose_print("Running with config file: {}".format( args.config_file), ehos.INFO)
    # readin the config file in as a Munch object
    with open(args.config_file, 'r') as stream:
        config = Munch.fromYAML(stream)
    stream.close()
    
    ehos.connect( auth_url=config.cloud.auth_url ,
                  user_domain_name=config.cloud.user_domain_name,
                  project_domain_name=config.cloud.project_domain_name,
                  username=config.cloud.username,
                  password=config.cloud.password,
                  project_name=config.cloud.project_name,
                  region_name=config.cloud.region_name,
                  no_cache=1,
    )
    ehos.verbose_level( args.verbose )
    ehos.verbose_print("Connected to openStack", ehos.INFO)
    
    
    if ( args.config_file):
        run_daemon( args.config_file )
    else:
        run_daemon()




if __name__ == '__main__':
    main()
else:
    print("Not to be run as a library")
    sys.exit( 1 )
          
    
