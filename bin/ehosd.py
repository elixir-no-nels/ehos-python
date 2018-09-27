#!/usr/bin/python3
# 
# 
# 
# 
# Kim Brugger (20 Sep 2018), contact: kim@brugger.dk

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)
import time
import datetime
import argparse
from munch import Munch
import re

import htcondor
import openstack

import ehos



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
                     'suspended': 0}


    for job in schedd.xquery(projection=['ClusterId', 'ProcId', 'JobStatus']):
        status_counts[ status_codes[  job.get('JobStatus') ]] += 1

    return Munch(status_counts)
        

def nodes_status(collector):
    """get the nodes connected to the master and groups them by status
    
    Available states are: idle, busy, suspended, vacating, killing, benchmarking, retiring

    Args:
      collector: htcondor schedd connector

    Returns:
      counts of nodes in states ( dict )

    Raises:
      None

    """


    node_counts = {"idle": 0,
                  "busy": 0,
                  "suspended": 0,
                  "vacating": 0,
                  "killing": 0,
                  "benchmarking": 0,
                   "retiring": 0,
                   "total": 0}

    
    for node in collector.query(htcondor.AdTypes.Startd, projection=['Name', 'Status', 'Activity', 'JobId', 'RemoteOwner']):
        node_counts[ node.get('Activity').lower() ] += 1
        node_counts['total'] += 1

    return Munch(node_counts)



def delete_idle_nodes(schedd, nodes:int=1):
    """ Delete idle nodes, by default one node is delete

    Args:
      schedd: htcondor schedd connector

    Returns:
      None

    Raises:
      None
    """

    for node in collector.query(htcondor.AdTypes.Startd, projection=['Name', 'Status', 'Activity', 'JobId', 'RemoteOwner']):
        # we have counted down to 0, such a hack should prob check up front.
        if not nodes:
            return

        if ( node.get('Status').lower() == 'idle'):
            ehos.server_delete( node.get('Name') )
        nodes -= 1


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


    server_id = get_node_id()
    
    server_IP = ehos.server_ip( server_id, 4)

    print( server_id )
    print( server_IP )

    ehos.alter_file(filename='/etc/condor/condor_config', patterns=[ (r'CONDOR_HOST = .*\n',"CONDOR_HOST = {IP}\n".format( host_ip)),
                                                                     (r'DAEMON_LIST = .*\n',"DAEMON_LIST = COLLECTOR, MASTER, NEGOTIATOR, SCHEDD\n")])

    # re-read the configuration
    ehos.system_call('condor_reconfig')
    

    # get some handles into condor, should perhaps wrap them in a module later on
    htcondor_collector = htcondor.Collector()
    htcondor_schedd    = htcondor.Schedd()
    


    while ( True ):

        # Continuously read in the config file making it possible to tweak the server as it runs. 
        with open(config_file, 'r') as stream:
            config = Munch.fromYAML(stream)
        stream.close()

        # get the current number of nodes
        nodes  = nodes_status(htcondor_collector)
        queue  = queue_status(htcondor_schedd)


        pp.pprint( nodes )
        pp.pprint( queue )
        

        
        # got jobs in the queue, and we can create some node(s) as we have not reached the max number yet
        if ( queue.idle and nodes.total < config.ehos.maxnodes):
            for i in range(0, config.ehos.maxnodes - nodes.total):
                node_id = ehos.server_create( "{}-node-{}".format(config.ehos.project_prefix, ehos.datetimestamp()),
                                              image=config.ehos.base_image_id,
                                              flavor=config.ehos.flavor,
                                              network=config.ehos.network,
                                              key=config.ehos.key,
                                              security_groups=config.ehos.security_groups)
                #                                    userdata_file='configs/executer.yaml')


                
        # there are nothing in the queue, and we have idle nodes, so lets get rid of some of them
        elif ( queue.idle == 0 and nodes.idle >= config.ehos.redundantnodes):
            delete_idle_nodes(htcondor_schedd,  nodes.idle - config.ehos.redundantnodes)

        elif ( nodes.total == config.ehos.maxnodes):
            print( "All nodes we are allowed have been created, nothing to do")

        elif ( nodes.total < config.ehos.minnodes):
            print( "we are below the min number of nodes, create some")

            for i in range(0, config.ehos.minnodes - nodes.total):
                node_id = ehos.server_create( "{}-node-{}".format(config.ehos.project_prefix, ehos.datetimestamp()),
                                              image=config.ehos.base_image_id,
                                              flavor=config.ehos.flavor,
                                              network=config.ehos.network,
                                              key=config.ehos.key,
                                              security_groups=config.ehos.security_groups)
                #                                    userdata_file='configs/executer.yaml')


            
        else:
            print("The minimum number of execute nodes are running, do nothing.")


        time.sleep( config.ehos.sleep_max)


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

    parser.add_argument('-v', '--verbose', default=False, action='store_true',  help="Verbose output")
    parser.add_argument('config_file', metavar='config-file', nargs=1,   help="yaml formatted config file")


    args = parser.parse_args()

    # as this is an array, and we will ever only get one file set it
    args.config_file = args.config_file[ 0 ]


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

    
    if ( args.verbose):
        print("Parsed arguments")
    
    if ( args.config_file):
        run_daemon( args.config_file )
    else:
        run_daemon()




if __name__ == '__main__':
    main()
else:
    print("Not to be run as a library")
    sys.exit( 1 )
          
    
