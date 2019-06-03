#!/usr/bin/env python3
#
#
#
#
# Kim Brugger (20 Sep 2018), contact: kim@brugger.dk


import os
import sys
import argparse
import re
import tempfile
import traceback
import pprint

from munch import Munch

import ehos
import ehos.htcondor
import ehos.log_utils as logger
import ehos.tick_utils as Tick
import ehos.utils


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

    if execute_config is None:
        execute_config = ehos.utils.find_config_file('execute.yaml')

    ehos.utils.patch_file(execute_config, outfile=outfile, patterns=[(r'{master_ip}', master_ip),
                                                                     (r'{uid_domain}', uid_domain),
                                                                     (r'{password}',password)])


    return outfile




def htcondor_setup_config_file( uid_domain  ):
    """ checks if this is a new instance of the ehosdm if it is tweak the htcondor config file and reload it

    Args:
      htcondor (obj): ehos.htcondor class

    Returns:
      None

    Raises:
      None
    """

    # first time running this master, so tweak the personal configureation file
    if ( os.path.isfile( '/etc/condor/00personal_condor.config')):

        ehos.utils.system_call("systemctl stop condor")
        #         uid_domain = ehos.make_uid_domain_name(5)
        host_ip    = ehos.utils.get_host_ip()
        host_name = ehos.utils.get_host_name()

        ehos.utils.patch_file(filename='/etc/condor/00personal_condor.config', patterns=[(r'{master_ip}', host_ip),
                                                                                         (r'{uid_domain}', uid_domain),])

        os.rename('/etc/condor/00personal_condor.config', '/etc/condor/config.d/00personal_condor.config')

        ehos.utils.system_call("systemctl start condor")
        ehos.htcondor.wait_for_running()



def main():

    parser = argparse.ArgumentParser(description='ehosd: the ehos daemon to be run on the master node ')

    parser.add_argument('-l', '--logfile', default=None, help="Logfile to write to, default is stdout")
    parser.add_argument('-v', '--verbose', default=4, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('config_file', metavar='config-file', nargs='?', help="yaml formatted config file", default=ehos.utils.find_config_file('ehos.yaml'))


    args = parser.parse_args()

    # as this is an array, and we will ever only get one file set it
    #    args.config_file = args.config_file[ 0 ]

    logger.init(name='ehosd', log_file=args.logfile )
    logger.set_log_level( args.verbose )
    logger.set_log_level( 5 )

    host_ip    = ehos.utils.get_host_ip()

    config = ehos.utils.get_configuration(args.config_file)


    uid_domain = ehos.utils.make_uid_domain_name(5)

    htcondor_setup_config_file( uid_domain=uid_domain )

    create_execute_config_file( host_ip, uid_domain, config.condor.password, outfile=config.daemon.execute_config )
    ehos.htcondor.set_pool_password( config.condor.password )


if __name__ == '__main__':
    main()
else:
    print("Not to be run as a library")
    sys.exit( 1 )
