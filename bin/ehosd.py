#!/usr/bin/env python3
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
import requests


# python3+ is broken on centos 7, so add the /usr/local/paths by hand
#sys.path.append("/usr/local/lib/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))
#sys.path.append("/usr/local/lib64/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))



from munch import Munch

import ehos
import ehos.htcondor
import ehos.log_utils as logger
import ehos.tick_utils as Tick


condor = None
tick   = None
log_fh = None

#condor = ehos.htcondor.Condor()



def log_nodes( names:list) -> None:
    ''' writes the names of nodes created to the log_fh if open '''

    if log_fh is None:
        return

    for name in names:
       log_fh.write("{}\n".format(name))

    sys,flush()

def setup_tick( config ):
    if 'influxdb' in config:
        print( "sending startup entry to influxdb")
        global tick
        tick = Tick.Tick(url = config.influxdb.url, database=config.influxdb.db,
                         user=config.influxdb.username, passwd=config.influxdb.password)

        tick.write_points({"measurement": 'ehos',
                           "tags": {'host': config.ehos_daemon.hostname,
                                    },
                           "fields": {'starting_daemon': 1 }})


def open_node_logfile( config ):
    if 'node_log' in config.ehos_daemon:
        global log_fh
        log_fh = open(config.ehos_daemon.node_log, 'a')


def run_daemon( config_file:str="/usr/local/etc/ehos.yaml" ):
    """ Creates the ehos daemon loop that creates and destroys nodes etc.
               
    The confirguration file is continously read so it is possible to tweak the behaviour of the system
               
    Args:
      init_file: alternative config_file

    Returns:
      None

    Raises:
      None
    """


    config = ehos.readin_config_file( config_file )
    ehos.init()

    setup_tick(config)
    open_node_logfile( config )
    global condor
    condor = ehos.htcondor.Condor()

    ehos.connect_to_clouds( config )


    while ( True ):

        config = ehos.readin_config_file( config_file )

        # get the current number of nodes
        nodes  = ehos.update_node_states()
        jobs   = condor.job_counts()

        # just care about the overall number of nodes, not how many in each cloud
        nodes = Munch(nodes[ 'all' ])

        logger.debug( "Node data\n" + pp.pformat( nodes ))
        logger.debug( "Jobs data\n" + pp.pformat( jobs  ))

        logger.info("Nr of nodes {} ({} are idle)".format( nodes.total, nodes.idle))
        logger.info("Nr of jobs {} ({} are queueing)".format( jobs.total, jobs.idle))


        if 'influxdb' in config:
            tick.write_points({"measurement": 'ehos',
                               "tags": {'host':config.ehos_daemon.hostname},
                               "fields": {'nodes_busy': nodes.busy,
                                          'nodes_idle':nodes.idle,
                                          'jobs_running': jobs.running,
                                          'jobs_idle': jobs.idle,}})

        
        # Below the min number of nodes needed for our setup
        if ( nodes.total < config.ehos_daemon.nodes_min ):
            logger.info("We are below the min number of nodes, creating {} nodes".format( config.ehos_daemon.nodes_min - nodes.total))

            node_names = ehos.create_execute_nodes(config, config.ehos_daemon.execute_config, config.ehos_daemon.nodes_min - nodes.total)
            log_nodes( node_names )

        ### there are jobs queuing, let see what we should do

        # got jobs in the queue but less than or equal to our idle + spare nodes, do nothing
        elif (  jobs.idle and jobs.idle <= nodes.idle ):
            logger.info("We got stuff to do, but seems to have excess nodes to cope...")

            nr_of_nodes_to_delete = min( nodes.total - config.ehos_daemon.nodes_min, nodes.idle -jobs.idle , nodes.idle - config.ehos_daemon.nodes_spare)
            
            logger.info("Deleting {} idle nodes... (1)".format( nr_of_nodes_to_delete))
            ehos.delete_idle_nodes(nr_of_nodes_to_delete)

            
        # Got room to make some additional nodes
        elif (  jobs.idle and nodes.total + config.ehos_daemon.nodes_spare <= config.ehos_daemon.nodes_max ):
            
            logger.info("We got stuff to do, creating some additional nodes...")

            node_names = ehos.create_execute_nodes(config, config.ehos_daemon.execute_config, config.ehos_daemon.nodes_max - nodes.total )
            log_nodes( node_names )


        # this one is just a sanity one
        elif ( jobs.idle and nodes.total == config.ehos_daemon.nodes_max):
            logger.info("We are busy. but all nodes we are allowed have been created, nothing to do")


        elif (  jobs.idle ):
            logger.info("We got stuff to do, but seems to have nodes to cope...")

            
        ### Looks like we have an excess of nodes, lets cull some

        # We got extra nodes not needed and we can delete some without going under the min cutoff, so lets get rid of some
        elif ( nodes.total > config.ehos_daemon.nodes_min and
               nodes.idle  > config.ehos_daemon.nodes_spare ):

            nr_of_nodes_to_delete = min( nodes.total - config.ehos_daemon.nodes_min, nodes.idle - config.ehos_daemon.nodes_spare)
            
            logger.info("Deleting {} idle nodes... (2)".format( nr_of_nodes_to_delete))
            ehos.delete_idle_nodes(nr_of_nodes_to_delete)
            
        else:
            logger.info("The number of execute nodes are running seem appropriate, nothing to change.")

        logger.info("Napping for {} second(s).".format(config.ehos_daemon.sleep))
        time.sleep( config.ehos_daemon.sleep)




        
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

    parser.add_argument('-l', '--logfile', default=None, help="Logfile to write to, default is stdout")
    parser.add_argument('-v', '--verbose', default=4, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('config_file', metavar='config-file', nargs='?',    help="yaml formatted config file", default=ehos.find_config_file('ehos.yaml'))


    args = parser.parse_args()

    # as this is an array, and we will ever only get one file set it
#    args.config_file = args.config_file[ 0 ]

    logger.init(name='ehosd', log_file=args.logfile )
    logger.set_log_level( args.verbose )

    logger.info("Running with config file: {}".format( args.config_file))
    run_daemon( args.config_file )


if __name__ == '__main__':
    main()
else:
    print("Not to be run as a library")
    sys.exit( 1 )
          
    
