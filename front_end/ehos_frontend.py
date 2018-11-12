#!/usr/bin/python3
""" 
 
 
 
 Kim Brugger (12 Nov 2018), contact: kim@brugger.dk
"""

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)



import re
import os

from flask import Flask
from flask import render_template

from munch import Munch

import ehos.instances
#import ehos.htcondor


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
                     'idle_p': 0,
                     'running': 0,
                     'running_p': 0,
                     'removed': 0,
                     'completed': 0,
                     'held': 0,
                     'transferring_output': 0,
                     'suspended': 0,
                     'total': 0}


    for job in schedd.xquery(projection=['ClusterId', 'ProcId', 'JobStatus']):
        status_counts[ status_codes[  job.get('JobStatus') ]] += 1
        status_counts[ 'total' ] += 1


        
    return status_counts

            

app = Flask(__name__)

@app.route('/')

def index():


    host_id    = '6f4967d5-706e-4f58-8287-74796c8fff26'
    host_ip    = '158.37.63.101'

    context = {'host_id': host_id,
               'host_ip': host_ip}
    

    
    i = ehos.instances.Instances()
    i.connect( 'postgresql://ehos:ehos@127.0.0.1:5432/ehos_instances')
    context['nodes']  = i.node_list_db()
               
    #    ehos.init()
    #    condor  = ehos.htcondor.Condor()
    #    context['queue']  = condor.job_counts()

    context['queue'] = {'idle': 10, 'running': 2, 'total': 12}


    context['queue']['idle_p'] =  context['queue']['idle']/context['queue']['total']*100.0

    context['queue']['running_p'] =  context['queue']['running']/context['queue']['total']*100.0

    
    
    return render_template('ehos/index.html', info=context)



if __name__ == '__main__':
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

