import re


from flask import Flask
from flask import render_template

from munch import Munch

import htcondor
import openstack

import ehos

nodes_deleted = []

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



    if status_counts['idle']:
        status_counts['idle_p'] =  status_counts['idle']/status_counts['total']*100.0

    if status_counts['running']:
        status_counts['running_p'] = status_counts['running']/status_counts['total']*100.0
        
    return status_counts


def get_node_states(collector, max_heard_from_time:int=300 ):
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

    _node_states = {}

    timestamp = ehos.timestamp()

    server_list = ehos.server_list()
    
    for node in collector.query(htcondor.AdTypes.Startd):

        name = node.get('Name')

        # trim off anything after the first . in the string
        if ("." in name):
            name = re.sub(r'(.*?)\..*', r'\1', name)

        (slot, host) = name.split("@")
        
        ehos.verbose_print("Node info: node:{} state:{} Activity:{} last seen:{} secs".format( name, node.get('State'), node.get('Activity'),timestamp - node.get('LastHeardFrom')), ehos.DEBUG+2)

        if host in nodes_deleted:
            continue

        # See if the server exists in the openstack list
        if( host not in server_list ):
            ehos.verbose_print( "-- >> Node {} not in the server_list, set is as deleted ".format( host ), ehos.INFO)
            nodes_deleted.append( host )
            continue

        # When was the last time we heard from this node? Assume dead?
        if ( timestamp - node.get('LastHeardFrom') > max_heard_from_time):
            ehos.verbose_print( "Seems to have lost the connection to {} (last seen {} secs ago)".format( name, timestamp - node.get('LastHeardFrom')), ehos.INFO)
            nodes_deleted.append( name )
            continue

        
        # This is a bit messy, a node can have child slots, so the
        # counting gets wrong if we look at all node entries.
        #
        # The way to solve this, for now?, is if a node has a child entry
        # (eg: slot1_1@hostname) this takes predicent over the main entry.
        
        if ( host in _node_states ):
            if ( "_" in name):
                _node_states[ host ] = node.get('Activity').lower()
        else:
            _node_states[ host ] = node.get('Activity').lower() 
            
    return _node_states
            

app = Flask(__name__)

@app.route('/')

def index():


    config_file = ehos.find_config_file('ehos.yaml')
    with open(config_file, 'r') as stream:
        config = Munch.fromYAML(stream)

    
    ehos.connect( auth_url=config.cloud.auth_url ,
                  user_domain_name=config.cloud.user_domain_name,
                  project_domain_name=config.cloud.project_domain_name,
                  username=config.cloud.username,
                  password=config.cloud.password,
                  project_name=config.cloud.project_name,
                  region_name=config.cloud.region_name,
                  no_cache=1,
    )
    ehos.verbose_level( 5 )
    ehos.verbose_print("Connected to openStack", ehos.INFO)

    

    host_id    = ehos.get_node_id()
    host_ip    = ehos.server_ip( host_id, 4)
    

    context = {'host_id': host_id,
               'host_ip': host_ip}
    
    htcondor_collector = htcondor.Collector()
    htcondor_schedd    = htcondor.Schedd()


    context['nodes']  = get_node_states(htcondor_collector)
    context['queue']  = queue_status(htcondor_schedd)

    
    return render_template('ehos/index.html', info=context)
