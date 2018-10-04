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
from munch import Munch
import re
import tempfile

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
                     'suspended': 0,
                     'total': 0}


    for job in schedd.xquery(projection=['ClusterId', 'ProcId', 'JobStatus']):
        status_counts[ status_codes[  job.get('JobStatus') ]] += 1
        status_counts[ 'total' ] += 1

    return Munch(status_counts)
        

def tmp_execute_config_file(master_ip:str, uid_domain:str, execute_config:str=None):
    """ Create a execute node config file with the master ip inserted into it

    Args:
      master_ip: ip of the master to connect to
      uid_domain: domain name we are using for this
      execute_config: define config template, otherwise find it in the system

    Returns:
      file name with path (str)

    Raises:
      None

    """

    if ( execute_config is None):
        execute_config = ehos.find_config_file('execute.yaml')
    
    # readin the maste file and insert out write_file_block(s)
    execute_content = ehos.readin_whole_file(execute_config)
    
    execute_content = re.sub('{master_ip}', master_ip, execute_content)
    execute_content = re.sub('{uid_domain}', uid_domain, execute_content)

    
    # write new config file to it and close it. As this is an on level
    # file handle the string needs to be encoded into a byte array

    # create a tmpfile/handle
    tmp_fh, tmpfile = tempfile.mkstemp(suffix=".yaml", dir="/tmp/", text=True)
    os.write( tmp_fh, str.encode( execute_content ))
    os.close( tmp_fh )


    return tmpfile


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

    node_states = {}

    timestamp = ehos.timestamp()

    # This is a bit messy, a node can have child slots, so the
    # counting gets wrong if we look at all node entries.
    #
    # The way to solve this, for now?, is if a node has a child entry
    # (eg: slot1_1@hostname) this takes predicent over the main entry.
    
    for node in collector.query(htcondor.AdTypes.Startd):

        print("{}  -- {} -- {}".format( node.get('Name'), node.get('Activity'), timestamp - node.get('LastHeardFrom')))

        if ( timestamp - node.get('LastHeardFrom') > max_heard_from_time):
            ehos.verbose_print( "Seems to have lost the connection to {} (last seen {} secs ago)".format( node.get('Name'), timestamp - node.get('LastHeardFrom')), ehos.INFO)
            continue


        name = node.get('Name')
        
        # trim off anything after the first . in the string
        if ("\." in name):
            name = re.sub(r'(.*?)\..*', r'\1', name)

        (slot, host) = name.split("@")
        

        if ( host in node_states and name.search("_")):
            node_states[ host ] = node.get('Activity').lower()
        else:
            node_states[ host ] = node.get('Activity').lower() 
            

    pp.pprint( node_states )
            
    node_counts = {"idle": 0,
                   "busy": 0,
                   "suspended": 0,
                   "vacating": 0,
                   "killing": 0,
                   "benchmarking": 0,
                   "retiring": 0,
                   "total": 0}


    
    
    for node in node_states.keys():

        
        node_counts[ node_states[ node] ] += 1
        node_counts['total'] += 1

    return Munch(node_counts)



def delete_idle_nodes(collector, nodes:int=1):
    """ Delete idle nodes, by default one node is delete

    Args:
      collector: htcondor collector object

    Returns:
      None

    Raises:
      None
    """

    for node in collector.query(htcondor.AdTypes.Startd, projection=['Name', 'Activity']):
        # we have counted down to 0, such a hack should prob check up front.
        if not nodes:
            return

#        pp.pprint( node )
        
        if ( node.get('Activity').lower() == 'idle'):
            node_name = node.get('Name')
            if ( "@" in  node_name):
                node_name = re.sub(r'.*\@', r'', node_name)
            else:
                ehos.verbose_print( "Odd node name {}".format( node_name), ehos.WARN)

            # Tell condor to drop a node before killing it, otherwise it will stick around in the condor node list
            ehos.system_call("condor_off -fast -name {}".format( node_name ))
            if ( re.search(r"\.", node_name)):
                 node_name = re.sub(r'(.*?)\..*', r'\1', node_name)
            
            try:
                ehos.server_delete( node_name )
            except:
                ehos.verbose_print( "{} is no longer available for deletion".format(node_name ), ehos.INFO)

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


    host_id    = ehos.get_node_id()
    host_ip    = ehos.server_ip( host_id, 4)
    uid_domain = ehos.make_uid_domain_name(5)

    ip_range = re.sub(r'(\d+\.\d+\.\d+\.)\d+', r'\1*', host_ip)

    # first time running this master, so tweak the personal configureation file
    if ( os.path.isfile( '/etc/condor/00personal_condor.config')):


         ehos.alter_file(filename='/etc/condor/00personal_condor.config', patterns=[ (r'{master_ip}',host_ip),
                                                                                     (r'{uid_domain}',uid_domain),
                                                                                     (r'{ip_range}', ip_range)])

         os.rename('/etc/condor/00personal_condor.config', '/etc/condor/config.d/00personal_condor.config')

         # re-read configuration file
         ehos.system_call('condor_reconfig')

    # get some handles into condor, should perhaps wrap them in a module later on
    htcondor_collector = htcondor.Collector()
    htcondor_schedd    = htcondor.Schedd()
    
    execute_config_file = tmp_execute_config_file( host_ip, uid_domain )

    
    while ( True ):

        # Continuously read in the config file making it possible to tweak the server as it runs. 
        with open(config_file, 'r') as stream:
            config = Munch.fromYAML(stream)
        stream.close()

        # get the current number of nodes
        nodes  = nodes_status(htcondor_collector)
        queue  = queue_status(htcondor_schedd)

        ehos.verbose_print( "Node data\n" + pp.pformat( nodes ), ehos.DEBUG)
        ehos.verbose_print( "Queue data\n" + pp.pformat( queue ), ehos.DEBUG)
        

        ehos.verbose_print("Nr of nodes {} ({} are idle)".format( nodes.total, nodes.idle), ehos.INFO)
        ehos.verbose_print("Nr of jobs {} ({} are queueing)".format( queue.total, queue.idle), ehos.INFO)
        

        
        #
        if ( nodes.total < config.ehos.minnodes):
            ehos.verbose_print("We are below the min number of nodes, create some", ehos.INFO)


            for i in range(0, config.ehos.minnodes - nodes.total):
                node_id = ehos.server_create( "{}-node-{}".format(config.ehos.project_prefix, ehos.datetimestamp()),
                                              image=config.ehos.base_image_id,
                                              flavor=config.ehos.flavor,
                                              network=config.ehos.network,
                                              key=config.ehos.key,
                                              security_groups=config.ehos.security_groups,
                                              userdata_file=execute_config_file)

                ehos.wait_for_log_entry(node_id, "The EHOS execute node is")
                ehos.verbose_print("Execute server is now online",  ehos.INFO)
        
        # got jobs in the queue, and we can create some node(s) as we have not reached the max number yet
        elif ( queue.idle and nodes.total < config.ehos.maxnodes):
            ehos.verbose_print("We got stuff to do, making some nodes...", ehos.INFO)

            for i in range(0, config.ehos.maxnodes - nodes.total):
                node_id = ehos.server_create( "{}-node-{}".format(config.ehos.project_prefix, ehos.datetimestamp()),
                                              image=config.ehos.base_image_id,
                                              flavor=config.ehos.flavor,
                                              network=config.ehos.network,
                                              key=config.ehos.key,
                                              security_groups=config.ehos.security_groups,
                                              userdata_file=execute_config_file)

                ehos.wait_for_log_entry(node_id, "The EHOS execute node is")
                ehos.verbose_print("Execute server is now online",  ehos.INFO)
                
        # there are nothing in the queue, and we have idle nodes, so lets get rid of some of them
        elif ( queue.idle == 0 and nodes.idle >= config.ehos.redundantnodes):
            delete_idle_nodes(htcondor_collector,  nodes.idle - config.ehos.redundantnodes)
            
            ehos.verbose_print("Deleting idle nodes...", ehos.INFO)

        elif ( nodes.total == config.ehos.maxnodes):
            ehos.verbose_print("All nodes we are allowed have been created, nothing to do", ehos.INFO)

        else:
            print()
            ehos.verbose_print("The minimum number of execute nodes are running, do nothing.", ehos.INFO)

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
    parser.add_argument('config_file', metavar='config-file', nargs=1,   help="yaml formatted config file", default=ehos.find_config_file('ehos.yaml'))


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
          
    
