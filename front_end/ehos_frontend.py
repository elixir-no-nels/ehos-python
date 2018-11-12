#!/usr/bin/python3
""" 
 
 
 
 Kim Brugger (12 Nov 2018), contact: kim@brugger.dk
"""

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)



import re
import os

# python3+ is broken on centos 7, so add the /usr/local/paths by hand
sys.path.append("/usr/local/lib/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))
sys.path.append("/usr/local/lib64/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))


from flask import Flask
from flask import render_template




from munch import Munch

sys.path.append("/tmp/ehos-python/")

pp.pprint( sys.path )

import ehos

import ehos.htcondor
import ehos.instances


app = Flask(__name__)

@app.route('/')

def index():


    host_id    = '6f4967d5-706e-4f58-8287-74796c8fff26'
    host_ip    = '158.37.63.101'

    context = {'host_id': host_id,
               'host_ip': host_ip,
               'nodes': {}}
    

    
    i = ehos.instances.Instances()
    i.connect( 'postgresql://ehos:ehos@127.0.0.1:5432/ehos_instances')

    nodes = i.node_list_db()
    
    for cloud in nodes:
        context['nodes'][cloud] = []
        for node in nodes[ cloud ]:
            if node[ 'state'] not in ['active', 'booting', 'retiring']:
                continue 
            context['nodes'][ cloud ].append( node )

    
    
    
    if ( 10 ):
        ehos.init()
        condor  = ehos.htcondor.Condor()
        context['queue']  = condor.job_counts()
    else:
        context['queue'] = {'idle': 10, 'running': 2, 'total': 12}


    context['queue']['idle_p'] = 0
    context['queue']['running_p'] = 0
    
    if ( context['queue']['total'] > 0 ):
        context['queue']['idle_p'] =  context['queue']['idle']/context['queue']['total']*100.0
        context['queue']['running_p'] =  context['queue']['running']/context['queue']['total']*100.0

    
    
    return render_template('ehos/index.html', info=context)



if __name__ == '__main__':
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

