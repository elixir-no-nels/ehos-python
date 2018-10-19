#!/usr/bin/python3
""" 
htcondor specific functions 
 
 
 Kim Brugger (19 Oct 2018), contact: kim@brugger.dk
"""

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)

import htcondor

htcondor_collector = None
htcondor_schedd    = None
htcondor_security  = None



def init():

    global htcondor_collector
    global htcondor_schedd
    global htcondor_security

    # get some handles into condor, should perhaps wrap them in a module later on
    htcondor_collector = htcondor.Collector()
    htcondor_schedd    = htcondor.Schedd()

    htcondor_security  = htcondor.SecMan()



    
    

    
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


