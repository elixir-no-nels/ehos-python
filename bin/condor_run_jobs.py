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


collector = htcondor.Collector()
schedd = htcondor.Schedd()

for i in range(0,20):
    
    sub = htcondor.Submit()
    sub['executable'] = '/bin/sleep'
    sub['arguments'] = "{}s".format( random.randint(30,60))
    with schedd.transaction() as txn:
        sub.queue(txn)
