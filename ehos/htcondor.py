#!/usr/bin/python3
""" 
htcondor specific functions 
 
 
 Kim Brugger (19 Oct 2018), contact: kim@brugger.dk
"""

import sys
import re
import pprint

import ehos.utils

pp = pprint.PrettyPrinter(indent=4)

from enum import IntEnum

import time

import ehos.log_utils as logger


from munch import Munch

import ehos


class Job_status( IntEnum ):
    job_idle                 = 1
    job_running              = 2
    job_removed              = 3
    job_completed            = 4
    job_held                 = 5
    job_transferring_output  = 6
    job_suspended            = 7

class Node_state( IntEnum ):
    node_idle         =  1
    node_starting     =  2
    node_busy         =  3
    node_suspended    =  4
    node_vacating     =  5
    node_killing      =  6
    node_benchmarking =  7
    node_retiring     =  8
    node_lost         =  9 # we have not heard from the server for a while so it is probably lost or dead. It normally takes ~30 min for this to register.



def turn_off_fast(name:str, daemon:str=None):
    """ Turns off all daemons, unless defined by name

        Ideally this should be done by an API call but this "feature" is undocumented

        Args:
          name: name of node to turn off
          daemon: name of daemon, othewise all of them

        Returns:
          None

        Raises:
          None

    """

    if daemon is not None:
        ehos.utils.system_call("condor_off -fast -daemon {} {}".format(daemon, name))
    else:
        ehos.utils.system_call("condor_off -fast {}".format(name))


def wait_for_running( max_timeout=60 ):
    """ wait for htcondor to be running 

    Args:
      max_timeout: max time to wait

    Returns:
      boolean, true for success
    
    Raises:
      RuntimeError if the daemon is not up before the timeout

    """

    logger.info("waiting for the condor daemon ...")
    while( max_timeout >= 0 ):
        try:
            import htcondor

            collector = htcondor.Collector()
            schedd    = htcondor.Schedd()
            security  = htcondor.SecMan()

            return True
        except Exception as e:
            print( e )
            logger.debug("still waiting for the condor daemon to come online")
            time.sleep( 5 )
            max_timeout -= 5

    return False
            
    


def set_pool_password(password:str) -> None:
    """ sets the pool password for condor
    
    Args:
    password to set
    
    Returns:
    None
    
    Raises:
    None
    
    """

    ehos.utils.system_call("condor_store_cred -p {password} -f /var/lock/condor/pool_password".format(password=password))

    
def reload_config() -> None:
    """ seems the lib is slightly broken, so doing this on the command line
    
    
    """
    
    ehos.utils.system_call("condor_reconfig")


class Condor( object ):

    _collector = None
    _schedd    = None
    _security  = None


    def __init__(self):
        """ Init the htcondor connections on this node

        Args:
          None
    
        Returns: 
          None
        
        Raises:
          None
        """

        import htcondor as HTC
        # get some handles into condor, should perhaps wrap them in a module later on
        self._collector = HTC.Collector()
        self._schedd    = HTC.Schedd()
        self._security  = HTC.SecMan()



    
    def job_counts( self ):
        """get the number of active jobs in the queue and group them by status

        The following are the states a job can be in:
          idle, running, removed0, completed, held, transferring_output, suspended and total

        Args:
          None

        Returns:
          counts of jobs in states ( dict )

        Raises:
          None

        """
        status_counts = {"job_total": 0}

        for job_status in Job_status:
            status_counts[ job_status.name ] = 0

        for job in self._schedd.xquery(projection=['ClusterId', 'ProcId', 'JobStatus']):
            status = Job_status( job.get('JobStatus') ).name

            status_counts[ status  ] += 1
            status_counts[ 'job_total' ] += 1

        return Munch(status_counts)



    def nodes(self, max_heard_from_time:int=300 ):
        """get the states of nodes startd known to HTcondor


        Args:
          max_heard_from_time: if we have not heard from a node this long, we expect it is dead

        Returns:
          node and their state ( dict )

        Raises:
          None

        """
        timestamp = ehos.utils.timestamp()

        node_states = {}
        import htcondor as HTC
        
        for node in self._collector.query( HTC.AdTypes.Startd, projection=['Name', 'State', 'Activity', 'LastHeardFRom'] ):
#            print( type( node ))
#            print(  node)

            name = node.get('Name')
#            print("name: '{}'".format( name ))

            # trim off anything after the first . in the string
            if ("." in name):
                name = re.sub(r'(.*?)\..*', r'\1', name)

            slot = None
            host = name
            if "@" in name:
                (slot, host) = name.split("@")

#            logger.debug("Node info: node:{} state:{} Activity:{} last seen:{} secs".format( name, node.get('State'), node.get('Activity'),timestamp - node.get('LastHeardFrom')))

            # When was the last time we heard from this node? Assume lost of longer than max_head_from_time
            if ( timestamp - node.get('LastHeardFrom') > max_heard_from_time):
                logger.debug( "Seems to have lost the connection to {} (last seen {} secs ago)".format( name, timestamp - node.get('LastHeardFrom')))
                node_states[ name ] = 'lost'
                continue

            # This is a bit messy, a node can have child slots, so the
            # counting gets wrong if we look at all node entries.
            #
            # The way to solve this, for now?, is if a node has a child entry
            # (eg: slot1_1@hostname) this takes predicent over the main entry.

            if ( host in node_states ):
                if ( "_" in name):
                    node_states[ host ] = "node_" + node.get('Activity').lower()
            else:
                node_states[ host ] = "node_" + node.get('Activity').lower()



#        logger.debug("Node states: \n{}".format( pp.pformat(node_states)))

        return node_states
    

    def node_counts(self, max_heard_from_time:int=300 ):
        """get the nodes connected to the master and groups them by status

        Available states are: idle, busy, suspended, vacating, killing, benchmarking, retiring

        Args:
          max_heard_from_time: if we have not heard from a node this long, we expect it is dead

        Returns:
          counts of nodes in states ( dict )

        Raises:
          None

        """

        node_counts = {"node_total": 0}

        # init the count dict to 0 for all states
        for node_status in Node_status:
            node_counts[ node_status.name ] = 0

        
        node_states = self.nodes( max_heard_from_time )

        for node in node_states.keys():

            node_counts[ node_states[ node] ] += 1
            node_counts['node_total'] += 1

        return Munch(node_counts)



