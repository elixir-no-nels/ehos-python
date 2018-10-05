from flask import Flask
from flask import render_template

import openstack

import ehos

def queue_status():
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

    
    status_counts = {'idle': 10,
                     'running': 1,
                     'removed': 0,
                     'completed': 0,
                     'held': 0,
                     'transferring_output': 0,
                     'suspended': 0,
                     'total': 11}


    status_counts['idle_p'] = status_counts['idle']/status_counts['total']*100.0
    status_counts['running_p'] = status_counts['running']/status_counts['total']*100.0
    
    return status_counts


def get_node_states():
    """get the states of nodes
    
    Available states are: idle, busy, suspended, vacating, killing, benchmarking, retiring

    Args:
      collector: htcondor collector object
      max_heard_from_time: if we have not heard from a node this long, we expect it is dead

    Returns:
      node states ( dict )

    Raises:
      None

    """

    _node_states = {   'ehos-v1-node-20181005t072610': 'idle',
                       'ehos-v1-node-20181005t074725': 'busy',
                       'ehos-v1-node-20181005t074736': 'idle',
                       'ehos-v1-node-20181005t074810': 'idle'}
    
            
    return _node_states
            

app = Flask(__name__)

@app.route('/')

def index():



    host_id    = '6f4967d5-706e-4f58-8287-74796c8fff26'
    host_ip    = '158.37.63.101'

    context = {'host_id': host_id,
               'host_ip': host_ip}
    

    context['nodes']  = get_node_states()
    context['queue']  = queue_status()

    
    

    
    return render_template('ehos/index.html', info=context)

