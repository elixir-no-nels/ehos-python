#!/usr/bin/python3

# small script that runs 10 jobs each sleeping between 60 and 300 seconds

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)
import time
import pprint as pp
pp = pprint.PrettyPrinter(indent=4)

import random
import socket

# python3+ is broken on centos 7, so add the /usr/local/paths by hand
sys.path.append("/usr/local/lib/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))
sys.path.append("/usr/local/lib64/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))

import htcondor

def main():


parser = argparse.ArgumentParser(description='deploy_ehos: Deploy ehos onto a openstack server ')

    # magically sets default config files
    parser.add_argument('-m', '--master-yaml',   help="yaml config file to create master image from", default=ehos.find_config_file('master.yaml'))
    parser.add_argument('-e', '--execute-yaml',  help="yaml config file for execute node from",       required=False, default=ehos.find_config_file('execute.yaml'))
    parser.add_argument('-c', '--config-dir',    help="Where to write config files to on the master", required=False, default='/usr/local/etc/ehos/')

    parser.add_argument('-v', '--verbose', default=1, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('config_file', metavar='config-file', nargs=1,   help="yaml formatted config file")

    args = parser.parse_args()



collector = htcondor.Collector()
schedd = htcondor.Schedd()

for i in range(0,12):
    
    sub = htcondor.Submit()
    sub['executable'] = '/bin/sleep'
#    sub['arguments'] = "{}s".format( random.randint(40,90))
    sub['arguments'] = "{}s".format( random.randint(20,40))
    with schedd.transaction() as txn:
        sub.queue(txn)



if __name__ == '__main__':
    main()
else:
    print("This is not meant to be used as a library")
    sys.exit(2)
        
