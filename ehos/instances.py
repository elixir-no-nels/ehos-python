#!/usr/bin/python3
""" 
  for tracking nodes 
 
 
 Kim Brugger (22 Oct 2018), contact: kim.brugger@uib.no
"""

import sys
import pprint
from munch import Munch

import ehos.log_utils as logger
import ehos.vm
import ehos.htcondor
import ehos.instances_db as db


class Instances(object):

    def __init__(self):
        """ Init function for the nodes class

        Args:
          None

        Returns:
          None
        
        Raises:
          None

        """

        self._nodes = {}
        self._clouds = {}
        self._name_to_id = {}

        self._db = None

    def connect(self, url: str) -> None:
        """ connects to a database instance

        Args:
        url: as specified by sqlalchemy ( {driver}://{user}:{password}@{host}:{port}/{dbase}
        """

        self._db = db.InstancesDB()
        self._db.connect( url )

    def disconnect(self) -> None:
        """ connects to a database instance

        Args:
        url: as specified by sqlalchemy ( {driver}://{user}:{password}@{host}:{port}/{dbase}
        """

        self._db.disconnect( )



    def add_cloud(self, name: str, instance) -> None:
        """ adds a cloud to the class
        
        Args:
          name: name of the cloud
          instance: an connection object to the cloud

        Returns:
          None

        Raises:
          RuntimeError if cloud already exists
        """

        if name in self._clouds:
            raise RuntimeError("Cloud {} is already present in instances".format(name))

        self._clouds[name] = instance
        if self._db is not None:
            self._db.cloud_id(name=name)


    def add_clouds(self, clouds:{}):
        for cloud_name in clouds:
            self.add_cloud(cloud_name, clouds[ cloud_name])

    def get_cloud(self, name: str):
        """ returns a cloud instance 
        
        Args:
          name: name of the cloud

        Returns:
          instance (obj?)

        Raises:
          RuntimeError if cloud dont exist 
        """

        if name not in self._clouds:
            raise RuntimeError("Unknown cloud name {}".format(name))

        return self._clouds[ name ]

    def clouds(self) -> {}:
        """ returns a copy of the cloud dict
        
        Args:
          None

        Returns:
          clouds (dict)

        Raises:
          None
        """

        return self._clouds.copy()

    def cloud_names(self) -> []:
        """ get a list of cloud names

        Args:
          None

        Returns:
          node dict (name, cloud, vm_state, 'node_state')

        Raises:
          RuntimeError if unknown node_id
        """

        return list(self._clouds.keys())

    def add_node(self, id:str, name:str, cloud:str, vm_state:str = 'vm_booting', node_state='node_starting') -> None:
        """ Adds a node to the class 

        Args:
          id: vm id of the node (should prob be a uuid)
          name: human readable name of node
          cloud: name of cloud where the node lives
          vm_state: VM state of the node, default is 'vm_booting'
          node_state: condor 'node_state' of the node, default is 'busy'

        Returns:
          None
        
        Raises:
          RuntimeError if unknown cloud, node id/name already exist, illegal vm_state or 'node_state'
        """

        if (cloud not in self._clouds):
            raise RuntimeError

        if (id in self._nodes):
            raise RuntimeError

        if (name in self._name_to_id):
            raise RuntimeError

        if (self.valid_vm_state(vm_state) == False):
            raise RuntimeError("Illegal vm_state '{}'".format(vm_state))

        if (self.valid_node_state(node_state) == False):
            raise RuntimeError("Illegal node_state '{}'".format(node_state))

        self._nodes[id] = {'id': id,
                           'name': name,
                           'cloud': cloud,
                           'vm_state': vm_state,
                           'node_state': node_state}

        self._name_to_id[name] = id

        if (self._db is not None):
            self._db.add_node(id, name, cloud, vm_state, node_state)

    def get_node(self, id: str) -> {}:
        """ get a nodes based on its id

        Args:
          id: id of the node

        Returns:
          node dict (id, name, cloud, vm_state, 'node_state')

        Raises:
          RuntimeError if unknown node_id
        """

        if (id not in self._nodes):
            raise RuntimeError

        return Munch(self._nodes[id])

    def get_nodes(self, vm_state=[], node_state=[], cloud=[]) -> {}:
        """ get a list of nodes, can be filtered based on 'node_state' names

        Args:
          state: (optional) for filtering on vm state
          node_state: (optional) for filtering on condor node_state
          cloud: (optional) for filtering on cloud name 

        Returns:
          list of node dict (name, cloud, node_state)

        Raises:
          RuntimeError if unknown node_id
        """

        vm_state = list(filter(None, vm_state))
        node_state = list(filter(None, node_state))
        cloud = list(filter(None, cloud))

        if vm_state is not None and vm_state != []:
            for s in vm_state:
                if self.valid_vm_state(s) == False:
                    raise RuntimeError("Illegal vm_state: '{}'".format(s))

        if node_state is not None and node_state != []:
            for s in node_state:
                if self.valid_node_state(s) == False:
                    raise RuntimeError("Illegal node_state {}".format(s))

        if cloud is not None and cloud != []:
            for c in cloud:
                if c not in self._clouds:
                    raise RuntimeError("Unknown cloud {}".format(c))

        res = []
        for node in self._nodes:
            if ((vm_state is None or vm_state == []) and (node_state is None or node_state == []) and (cloud is None or cloud == [])):
                res.append(Munch(self._nodes[node]))

            elif self._nodes[node]['vm_state'] in vm_state or self._nodes[node]['node_state'] in node_state or self._nodes[node][
                'cloud'] in cloud:
                res.append(Munch(self._nodes[node]))

        return res

    def node_state_counts(self) -> {}:
        """ returns the states of nodes split into clouds

        Args:
          None

        Returns:
          dict of states and their counts + a total 

        Raises:
          None
        """

        template = {'node_idle': 0,
                    'node_busy': 0,
                    'node_total': 0,
                    'node_other': 0}

        res = {'all': template.copy()}

        for node in self.get_nodes(vm_state=['vm_active', 'vm_booting']):

            if node['cloud'] not in res:
                res[node['cloud']] = template.copy()

            #            pp.pprint( node )

            if (node['node_state'] == 'node_idle'):
                res['all']['node_idle'] += 1
                res['all']['node_total'] += 1

                res[node['cloud']]['node_idle'] += 1
                res[node['cloud']]['node_total'] += 1

            elif (node['node_state'] in ['node_busy', 'node_starting', 'node_vacating', 'node_benchmarking']):
                res['all']['node_busy'] += 1
                res['all']['node_total'] += 1

                res[node['cloud']]['node_busy'] += 1
                res[node['cloud']]['node_total'] += 1
            else:
                res['all']['node_other'] += 1

                res[node['cloud']]['node_other'] += 1

        return Munch(res)

    def get_node_ids(self, vm_state: str = None, node_state: str = None, cloud: str = None) -> []:
        """ get a list of nodes, can be filtered based on node_state

        Args:
          vm_state: (optional) for filtering on vm_state
          node_state: (optional) for filtering on condor node_state

        Returns:
          list of node ids

        Raises:
          None
        """

        node_ids = []

        for node in self.get_nodes(vm_state=[vm_state], node_state=[node_state], cloud=[cloud]):
            node_ids.append(node['id'])

        return node_ids

    def get_node_names(self, vm_state: str = None, node_state: str = None, cloud: str = None) -> []:
        """ get a list of node names, can be filtered based on node_state

        Args:
          vm_state: (optional) for filtering on vm-state
          node_state: (optional) for filtering on condor node_state

        Returns:
          list of node names

        Raises:
          None
        """

        node_names = []

        for node in self.get_nodes(vm_state=[vm_state], node_state=[node_state], cloud=[cloud]):
            node_names.append(node['name'])

        return node_names

    def vm_id2name(self, node_id: str) -> str:
        """ translate a node id to a node name

        Args:
          node_id: vm id of node

        Returns 
          node name (str)
        
        Raises:
          RuntimeError if unknown node_id
        """

        if (node_id not in self._nodes):
            raise RuntimeError

        return self._nodes[node_id]['name']

    def vm_name2id(self, node_name: str) -> str:
        """ translate a node name to a node id

        Args:
          node_name: name of node

        Returns 
          node id (str)
        
        Raises:
          RuntimeError if unknown node_name
        """

        if (node_name not in self._name_to_id):
            raise RuntimeError

        return self._name_to_id[node_name]

    def nodes_in_cloud(self, cloud_name: str) -> []:
        """ returns a list of node ids in a given cloud 

        Args:
          node_name: name of cloud to return data from
        
        Returns:
          list of node ids, returns [] if no nodes in cloud

        Raises:
          None
        """

        if (cloud_name not in self._clouds):
            return []


        else:
            res = []
            for node in self.get_nodes(cloud=[cloud_name]):
                res.append(node['id'])

            return res

    def find(self, id: str = None, name: str = None):
        """ find a node either by id or name

        Args:
          id: node vm id
          name: human readable node name
        
        returns 
          node info: (id, name, cloud_name, vm_state, node_state), None if id/name does not exist

        raises:
 

        """

        if (name is not None):
            try:
                id = self.vm_name2id(name)
            except:
                return None
        #            raise RuntimeError("Node name not found {}".format( name))

        if id not in self._nodes:
            return None
        #            raise RuntimeError("Unknown node id {}".format( id ))

        if id is not None:
            return self._nodes[id]

    def vm_state(self, node_id: str):
        """ get vm state for a node
        
        Args:
          node_id: id of the node

        Returns:
          None
        
        Raises:
          RuntimeError if unknown node id
        """

        if (node_id not in self._nodes):
            raise RuntimeError

        return self._nodes[node_id]['vm_state']

    def valid_vm_state(self, vm_state: str) -> bool:
        """ check that a state has a valid value

        Args:
          state to check

        Returns 
          boolean 

        Raises
          None
        """

        #        logger.debug("Testing the state validity of {}".format( state ))

        if (vm_state not in ehos.vm.State.__members__):
            return False

        return True

    def valid_node_state(self, node_state: str) -> bool:
        """ check that a state has a valid value

        Args:
          node_state to check

        Returns 
          boolean 

        Raises
          None
        """

        #        logger.debug("Testing the node_state validity of {}".format( node_state ))

        if (node_state not in ehos.htcondor.Node_state.__members__):
            return False

        return True

    def set_vm_state(self, node_id: str, vm_state: str):
        """ set vm node_state for a node
        
        Args:
          node_id: id of the node
          vm_state: new node_state of the node

        Returns:
          None
        
        Raises:
          RuntimeError if unknown node id or illegal vm_state name
        """

        if (node_id not in self._nodes):
            logger.warn("Unknown Node {}".format(node_id))

 #           return
            raise RuntimeError("Unknown node {}".format(node_id))

        if (self.valid_vm_state(vm_state) == False):
            #print( vm_state )
            raise RuntimeError("Illegal vm_state {}".format(vm_state))

        #        if ( self._nodes[ node_id][ 'vm_state'] == vm_state ):
        #            return

        logger.debug("Node {}/{} vm_state changed to {} from {}".format(node_id, self._nodes[node_id]['name'],
                                                                     self._nodes[node_id]['vm_state'], vm_state))

        self._nodes[node_id]['vm_state'] = vm_state

    def get_node_state(self, node_id: str):
        """ get condor node_state for a node
        
        Args:
          node_id: id of the node

        Returns:
          None
        
        Raises:
          RuntimeError if unknown node id
        """

        if (node_id not in self._nodes):
            raise RuntimeError

        return self._nodes[node_id]['node_state']

    def set_node_state(self, node_id: str, node_state: str):
        """ set condor node_state for a node
        
        Args:
          node_id: id of the node
          node_state: new node_state of the node

        Returns:
          None
        
        Raises:
          RuntimeError if unknown node id
        """

        if (node_id not in self._nodes):
            raise RuntimeError

        if (self._nodes[node_id]['node_state'] == node_state):
            return

        if (self.valid_node_state(node_state) == False):
            raise RuntimeError("Illegal node_state {}".format(node_state))

        logger.debug("Node {}/{} node_state changed from {} to {}".format(node_id, self._nodes[node_id]['name'],
                                                                      self._nodes[node_id]['node_state'], node_state))

        self._nodes[node_id]['node_state'] = node_state


    def update(self, nodes):

        clouds = self.clouds()
        vms = ehos.vm_list( clouds )
        vm_names = {vms[q]['name']:q for q in vms}
        #print( vm_names )
        for node in nodes:

            # This can happen if the server is restarted and condor
            # retains information about old nodes that have since been
            # deleted from the cloud(s)
            if ( node not in vm_names ):
                continue

            vm_id = vm_names[ node ]
#            print( "VM ID : ", vm_id)

            # the node is unknown to our instances, so add it
            if ( self.find( name = node ) is None ):
#                print(vm_id, node, vms[ vm_id ]['cloud_name'], vms[ vm_id ]['vm_state'], nodes[ node ])
                self.add_node(id=vm_id, name=node, cloud=vms[ vm_id ]['cloud_name'], vm_state=vms[ vm_id ]['vm_state'], node_state=nodes[ node ])
            else:
                self.set_node_state( node_id=vm_id, node_state=nodes[ node ])

        print( self.get_nodes())

        for node in self.get_nodes():

            # Not known in the clouds or node_state != vm_active, set is as vm_deleted.
            if node['id'] not in vms:# or vms[ node['id']]['vm_state'] != 'vm_active':
                #print('del 1')
                self.set_vm_state(node_id=node['id'], vm_state='vm_deleted')
                self.set_node_state( node_id=node['id'], node_state='node_lost')

            # these are in states that are not helpful for us, so ignore them for now
            elif node['node_state' ] in ['node_suspended', 'node_killing', 'node_retiring', 'node_lost']:
                #print("del 2")
                self.set_vm_state(node_id=node['id'], vm_state='vm_deleted')
                self.set_node_state( node_id=node['id'], node_state='node_lost')

            elif node[ 'vm_state' ] == 'vm_booting':
                # often htcondor knows about the server before it is fully booted up
                self.set_vm_state(node_id=node['id'], vm_state='vm_active')
            else:
                self.set_vm_state(node_id=node['id'], vm_state='vm_active')



