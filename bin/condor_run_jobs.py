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

import htcondor


collector = htcondor.Collector()
schedd = htcondor.Schedd()

for i in range(1,10):
    
    sub = htcondor.Submit()
    sub['executable'] = '/bin/sleep'
    sub['arguments'] = "{}s".format( random.randint(60,300))
    with schedd.transaction() as txn:
        sub.queue(txn)
