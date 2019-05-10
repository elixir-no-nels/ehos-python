#!/usr/bin/env python3
# 
# 
# 
# 
# Kim Brugger (20 Sep 2018), contact: kim@brugger.dk

import pprint
import sys

import ehos.utils

pp = pprint.PrettyPrinter(indent=4)
import time
import argparse
from munch import Munch

# python3+ is broken on centos 7, so add the /usr/local/paths by hand
#sys.path.append("/usr/local/lib/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))
#sys.path.append("/usr/local/lib64/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))



import ehos
import ehos.htcondor
import ehos.instances
import ehos.log_utils as logger
import ehos.tick_utils as Tick


condor    = None
tick      = None
log_fh    = None
instances = None


def log_nodes( names:[]) -> None:
    ''' writes the names of nodes created to the log_fh if filehandle is open'''

    if log_fh is None:
        return

    for name in names:
       log_fh.write("{}\n".format(name))

    sys.stdout.flush()

def setup_tick( config ):
    if 'influxdb' in config:
        print( "sending startup entry to influxdb")
        global tick
        tick = Tick.Tick(url = config.influxdb.url, database=config.influxdb.db,
                         user=config.influxdb.username, passwd=config.influxdb.password)

        tick.write_points({"measurement": 'ehos',
                           "tags": {'host': config.daemon.hostname,
                                    },
                           "fields": {'starting_daemon': 1 }})


def setup_db_backend( config ):
    if 'database' in config.daemon:
        ehos.instances_connect_to_database(config.daemon.database)


def open_node_logfile( config ):
    if 'node_log' in config.daemon:
        global log_fh
        log_fh = open(config.daemon.node_log, 'a')



def init( instance_url:str=None ):
    ''' setup the environment '''
    global condor
    global instances


    condor  = ehos.htcondor.Condor()
    instances = ehos.instances.Instances()

    if instance_url is not None:
        instances.connect( instance_url )




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


    config = ehos.utils.readin_config_file(config_file)

    setup_tick(config)
    open_node_logfile( config )
    setup_db_backend( config )

    global condor
    condor = ehos.htcondor.Condor()

    clouds = ehos.connect_to_clouds( config )
    global instances
    instances = ehos.instances.Instances()
    instances.add_clouds( clouds )

    new_nodes = []

    while ( True ):

        config = ehos.utils.readin_config_file(config_file)

        # get the current number of nodes
        instances.update(condor.nodes())
        nodes = instances.node_state_counts()
        jobs   = condor.job_counts()

        # just care about the overall number of nodes, not how many in each cloud
        nodes = Munch(nodes[ 'all' ])

        logger.debug( "Node data\n" + pp.pformat( nodes ))
        logger.debug( "Jobs data\n" + pp.pformat( jobs  ))

        logger.info("Nr of nodes {} ({} are idle)".format( nodes.node_total, nodes.node_idle))
        logger.info("Nr of jobs {} ({} are queueing)".format( jobs.job_total, jobs.job_idle))

        if ('purge_floating_ips' in config.daemon ):
            new_nodes = ehos.remove_floating_ips(instances, new_nodes )


        if 'influxdb' in config:
            tick.write_points({"measurement": 'ehos',
                               "tags": {'host':config.daemon.hostname},
                               "fields": {'nodes_busy': nodes.node_busy,
                                          'nodes_idle':nodes.node_idle,
                                          'jobs_running': jobs.job_running,
                                          'jobs_idle': jobs.job_idle,}})

        
        # Below the min number of nodes needed for our setup
        if ( nodes.node_total < config.daemon.nodes_min ):
            logger.info("We are below the min number of nodes, creating {} nodes".format( config.daemon.nodes_min - nodes.node_total))

            node_names = ehos.create_execute_nodes(instances, config, config.daemon.execute_config, config.daemon.nodes_min - nodes.node_total)
            log_nodes( node_names )
            new_nodes += node_names

        ### there are jobs queuing, let see what we should do

        # got jobs in the queue but less than or equal to our idle + spare nodes, do nothing
        elif jobs.job_idle and jobs.job_idle <= nodes.node_idle:
            logger.info("We got stuff to do, but seems to have excess nodes to cope...")

            nr_of_nodes_to_delete = min( nodes.node_total - config.daemon.nodes_min, nodes.node_idle -jobs.job_idle , nodes.node_idle - config.daemon.nodes_spare)
            
            logger.info("Deleting {} idle nodes... (1)".format( nr_of_nodes_to_delete))
            ehos.delete_idle_nodes(instances, condor.nodes(), nr_of_nodes_to_delete)

            
        # Got room to make some additional nodes
        elif (  jobs.job_idle and nodes.node_total + config.daemon.nodes_spare <= config.daemon.nodes_max ):
            
            logger.info("We got stuff to do, creating some additional nodes...")

            node_names = ehos.create_execute_nodes(instances, config, config.daemon.execute_config, config.daemon.nodes_max - nodes.node_total )
            log_nodes( node_names )


        # this one is just a sanity one
        elif ( jobs.job_idle and nodes.node_total == config.daemon.nodes_max):
            logger.info("We are busy. but all nodes we are allowed have been created, nothing to do")


        elif (  jobs.job_idle ):
            logger.info("We got stuff to do, but seems to have nodes to cope...")

            
        ### Looks like we have an excess of nodes, lets cull some

        # We got extra nodes not needed and we can delete some without going under the min cutoff, so lets get rid of some
        elif ( nodes.node_total > config.daemon.nodes_min and
               nodes.node_idle  > config.daemon.nodes_spare ):

            nr_of_nodes_to_delete = min( nodes.node_total - config.daemon.nodes_min, nodes.node_idle - config.daemon.nodes_spare)
            
            logger.info("Deleting {} idle nodes... (2)".format( nr_of_nodes_to_delete))
            ehos.delete_idle_nodes(instances, condor.nodes(), nr_of_nodes_to_delete)
            
        else:
            logger.info("The number of execute nodes are running seem appropriate, nothing to change.")

        logger.info("Napping for {} second(s).".format(config.daemon.sleep))
        time.sleep( config.daemon.sleep)




        
def main():

    parser = argparse.ArgumentParser(description='ehosd: the ehos daemon to be run on the master node ')

    parser.add_argument('-l', '--logfile', default=None, help="Logfile to write to, default is stdout")
    parser.add_argument('-v', '--verbose', default=4, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('config_file', metavar='config-file', nargs='?', help="yaml formatted config file", default=ehos.utils.find_config_file('ehos.yaml'))


    args = parser.parse_args()
    logger.init(name='ehosd', log_file=args.logfile )
    logger.set_log_level( args.verbose )

    logger.info("Running with config file: {}".format( args.config_file))
    run_daemon( args.config_file )


if __name__ == '__main__':
    main()
else:
    print("Not to be run as a library")
    sys.exit( 1 )
          
    
