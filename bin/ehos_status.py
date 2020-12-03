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
import argparse
import socket
import ehos.log_utils as logger
from munch import Munch

# python3+ is broken on centos 7, so add the /usr/local/paths by hand
#sys.path.append("/usr/local/lib/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))
#sys.path.append("/usr/local/lib64/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))



import ehos
import ehos.htcondor
import ehos.instances


def get_hostname() -> str:
    return socket.getfqdn()



def main():

    parser = argparse.ArgumentParser(description='ehos_status: print ehos status in telegraf format')
    parser.add_argument('config_files', metavar='config-files', nargs='+', help="yaml formatted config files", default=ehos.utils.find_config_file('ehos.yaml'))
    args = parser.parse_args()

    logger.init(name='ehosd' )
    logger.set_log_level( 0 )

    config = ehos.utils.get_configurations(args.config_files)
    condor = ehos.htcondor.Condor()
    clouds = ehos.connect_to_clouds( config )
    instances = ehos.instances.Instances()
    instances.add_clouds( clouds )

    # get the current number of nodes
    instances.update(condor.nodes())
    nodes = instances.node_state_counts()
    nodes = Munch(nodes[ 'all' ])
    jobs   = condor.job_counts()

    hostname = get_hostname()

    print(f"condor,host={hostname} jobs_total={jobs.get('job_total', 0)},jobs_idle={jobs.get('job_idle',0)},jobs_running={jobs.get('job_running', 0)},jobs_suspended={jobs.get('job_suspended', 0)}")
    print(f"ehos,host={hostname} nodes_total={nodes.get('node_total', 0)},nodes_idle={nodes.get('node_idle',0)},nodes_busy={nodes.get('node_busy', 0)}")

if __name__ == '__main__':
    main()
else:
    print("Not to be run as a library")
    sys.exit( 1 )



