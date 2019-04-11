#!/usr/bin/env python3

# small script that runs 10 jobs each sleeping between 60 and 300 seconds

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)

import argparse

import random
import socket

# python3+ is broken on centos 7, so add the /usr/local/paths by hand
sys.path.append("/usr/local/lib/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))
sys.path.append("/usr/local/lib64/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))

import htcondor

def main():


    parser = argparse.ArgumentParser(description='deploy_ehos: Deploy ehos onto a openstack server ')

    # magically sets default config files
    parser.add_argument('-n', '--number-of-jobs', help="Number of jobs to submit", default=15)
    parser.add_argument('-s', '--sleeptime',      help="fixed sleep time (all jobs sleep the same amount )", default=30)
    parser.add_argument('-r', '--range',          help="sleep will be a randon number in this range, eg: 20,30",       required=False)


    args = parser.parse_args()


    min_sleep = args.sleeptime
    max_sleep = args.sleeptime
    
    if args.range is not None:
        try:
            min_sleep, max_sleep = map( int, args.range.split(","))
        except:
            print( "Range needs to be in the following format 20,50 not {}".format(args.range))
            sys.exit(10)

    if ( min_sleep > max_sleep):
        min_sleep, max_sleep = max_sleep, min_sleep
            
    collector = htcondor.Collector()
    schedd = htcondor.Schedd()

    for i in range(0,12):
    
        sub = htcondor.Submit()
        sub['executable'] = '/bin/sleep'
        sub['arguments'] = "{}s".format( random.randint(min_sleep,max_sleep))

        with schedd.transaction() as txn:
            sub.queue( txn )



if __name__ == '__main__':
    main()
else:
    print("This is not meant to be used as a library")
    sys.exit(2)
        
