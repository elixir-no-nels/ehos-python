import sys
# python3+ is broken on centos 7, so add the /usr/local/paths by hand
import ehos.utils

sys.path.append("/usr/local/lib/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))
sys.path.append("/usr/local/lib64/python{}.{}/site-packages/".format( sys.version_info.major, sys.version_info.minor))

import pytest

from unittest.mock import Mock, patch

from munch import Munch

import htcondor
import classad

#import ehos
import ehos.htcondor as C
import ehos



def test_job_status():

    assert C.Job_status.job_idle                 == 1
    assert C.Job_status.job_running              == 2
    assert C.Job_status.job_removed              == 3
    assert C.Job_status.job_completed            == 4
    assert C.Job_status.job_held                 == 5
    assert C.Job_status.job_transferring_output  == 6
    assert C.Job_status.job_suspended            == 7

    
def test_job_status_reverse():

    assert C.Job_status(1) == C.Job_status.job_idle
    assert C.Job_status(2) == C.Job_status.job_running
    assert C.Job_status(3) == C.Job_status.job_removed
    assert C.Job_status(4) == C.Job_status.job_completed
    assert C.Job_status(5) == C.Job_status.job_held
    assert C.Job_status(6) == C.Job_status.job_transferring_output
    assert C.Job_status(7) == C.Job_status.job_suspended



def test_node_state():

    assert C.Node_state.node_idle         == 1
    assert C.Node_state.node_starting     == 2
    assert C.Node_state.node_busy         == 3
    assert C.Node_state.node_suspended    == 4
    assert C.Node_state.node_vacating     == 5
    assert C.Node_state.node_killing      == 6
    assert C.Node_state.node_benchmarking == 7
    assert C.Node_state.node_retiring     == 8
    assert C.Node_state.node_lost         == 9
    

def test_node_state_reverse():

    assert C.Node_state(1) == C.Node_state.node_idle
    assert C.Node_state(2) == C.Node_state.node_starting
    assert C.Node_state(3) == C.Node_state.node_busy
    assert C.Node_state(4) == C.Node_state.node_suspended
    assert C.Node_state(5) == C.Node_state.node_vacating
    assert C.Node_state(6) == C.Node_state.node_killing
    assert C.Node_state(7) == C.Node_state.node_benchmarking
    assert C.Node_state(8) == C.Node_state.node_retiring
    assert C.Node_state(9) == C.Node_state.node_lost
    


#def test_init():
#    c = C.Condor()


# Fake xquery to be used by the next job test function. Returns the number of job equal to the status.
def fake_job_query(self, **kwargs):

    res = []
    ca = "[ ServerTime = {ts}; JobStatus= {st}; ProcId = 0; ClusterId = 991; ]"

    now = ehos.utils.timestamp()
    
    for job_status in C.Job_status:
        for i in range(0, job_status.value):
            res.append( classad.ClassAd(ca.format( ts= now, st=job_status.value)))

    return res

    
@patch.object(htcondor.Schedd, 'xquery', fake_job_query)
def test_job_counts():

    c = C.Condor()

    job_counts = c.job_counts()
    assert {'idle': 1,
            'running': 2,
            'removed': 3,
            'completed': 4,
            'held': 5,
            'transferring_output': 6,
            'suspended': 7,
            'total': 28,} == dict( job_counts )

    
# Fake xquery to be used by the next job test function. Returns the number of job equal to the status.
def fake_node_query(self, types, **kwargs):

    res = []
    ca = """[ Name = "{name}"; Activity= "{act}"; LastHeardFrom = {ts}; State = "{st}"; ]"""

    now = ehos.utils.timestamp()
    
    res.append( classad.ClassAd(ca.format( name='node1-test.tyt', act='Idle',         ts=now,     st='Unclaimed')))
    res.append( classad.ClassAd(ca.format( name='node2-test.tyt', act='Starting',     ts=now,     st='Unclaimed')))
    res.append( classad.ClassAd(ca.format( name='node3-test.tyt', act='busy',         ts=now,     st='Unclaimed')))
    res.append( classad.ClassAd(ca.format( name='node4-test.tyt', act='suspended',    ts=now,     st='Unclaimed')))
    res.append( classad.ClassAd(ca.format( name='node5-test.tyt', act='vacating',     ts=now,     st='Unclaimed')))
    res.append( classad.ClassAd(ca.format( name='node6-test.tyt', act='killing',      ts=now,     st='Unclaimed')))
    res.append( classad.ClassAd(ca.format( name='node7-test.tyt', act='Benchmarking', ts=now,     st='Unclaimed')))
    res.append( classad.ClassAd(ca.format( name='node8-test.tyt', act='retiring',     ts=now,     st='Unclaimed')))
    res.append( classad.ClassAd(ca.format( name='node9-test.tyt', act='Idle',         ts=now-600, st='Unclaimed')))

    return res

@patch.object(htcondor.Collector, 'query', fake_node_query)
def test_nodes():
    c = C.Condor()

    nodes = c.nodes()
    print( nodes )
    assert nodes == {'node1-test': 'idle',
                     'node2-test': 'starting',
                     'node3-test': 'busy',
                     'node4-test': 'suspended',
                     'node5-test': 'vacating',
                     'node6-test': 'killing',
                     'node7-test': 'benchmarking',
                     'node8-test': 'retiring',
                     'node9-test': 'lost' }



@patch.object(htcondor.Collector, 'query', fake_node_query)
def test_node_counts():
    c = C.Condor()

    nodes = c.node_counts()
    print( nodes )
    assert dict(nodes) == {'idle'         : 1,
                           'starting'     : 1,
                           'busy'         : 1,
                           'suspended'    : 1,
                           'vacating'     : 1,
                           'killing'      : 1,
                           'benchmarking' : 1,
                           'retiring'     : 1,
                           'lost'         : 1,
                           'total'        : 9}


    
