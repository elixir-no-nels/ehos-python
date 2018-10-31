#!/usr/bin/python3
""" 
  for tracking nodes 
 
 
 Kim Brugger (22 Oct 2018), contact: kim@brugger.dk
"""

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)

import logging
logger = logging.getLogger('ehos.instances')



from munch import Munch


class Instances(object):


    _nodes = {}
    _clouds = {}
    
    _name_to_id = {}

    def __init__( self ):
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




    def add_cloud(self, name:str, instance) -> None:
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
            raise RuntimeError
        
        self._clouds[ name ] = instance


    def get_cloud( self, name:str):
        """ returns a cloud instance 
        
        Args:
          name: name of the cloud

        Returns:
          instance (obj?)

        Raises:
          RuntimeError if cloud dont exist 
        """

        if name not in self._clouds:
            raise RuntimeError
        
        return self._clouds[ name ]
        
    def get_clouds( self) -> {}:
        """ returns a copy of the cloud dict
        
        Args:
          None

        Returns:
          clouds (dict)

        Raises:
          None
        """

        
        return self._clouds.copy()

    def get_cloud_names(self) -> [] :
        """ get a list of cloud names

        Args:
          None

        Returns:
          node dict (name, cloud, status)

        Raises:
          RuntimeError if unknown node_id
        """

        return list(self._clouds.keys())
        

    def add_node( self, id:str, name:str, cloud:str, status:str='starting')-> None:
        """ Adds a node to the class 

        Args:
          id: vm id of the node (should prob be a uuid)
          name: human readable name of node
          cloud: name of cloud where the node lives
          status: status of the node, default is 'starting'

        Returns:
          None
        
        Raises:
          RuntimeError if unknown cloud, or node id/name already exist
        """

        if (cloud not in self._clouds):
            raise RuntimeError
        
        if ( id in self._nodes ):
            raise RuntimeError

        if ( name in self._name_to_id ):
            raise RuntimeError
        
        self._nodes[ id ] = { 'id': id,
                              'name'  : name,
                              'cloud' : cloud,
                              'status': status}

        self._name_to_id[ name ] = id
        

    def get_node(self, id:str) -> {} :
        """ get a nodes based on its id

        Args:
          id: id of the node

        Returns:
          node dict (id, name, cloud, status)

        Raises:
          RuntimeError if unknown node_id
        """

        if ( id not in self._nodes ):
            raise RuntimeError


        return Munch(self._nodes[ id ])


    def get_nodes(self, status=[], cloud=[]) -> {} :
        """ get a list of nodes, can be filtered based on status names

        Args:
          status: (optional) for filtering on status 
          cloud: (optional) for filtering on cloud name 

        Returns:
          list of node dict (name, cloud, status)

        Raises:
          RuntimeError if unknown node_id
        """


        res = []
        for node in self._nodes:
            if self._nodes[ node ][ 'status' ] in status or self._nodes[ node ]['cloud'] in cloud:
                res.append( Munch(self._nodes[ node ] ))
        

        return res        

        
    def get_node_ids(self, status:str=None) -> [] :
        """ get a list of nodes, can be filtered based on status

        Args:
          status: (optional) for filtering on status 

        Returns:
          list of node ids

        Raises:
          None
        """


        node_ids = []

        for node_id in self._nodes:
            # No filtering, get all nodes
            if status is None:
                node_ids.append( node_id )
            # Check if the status fits with what we are filtering on
            elif self._nodes[ node_id ]['status'] == status:
                node_ids.append( node_id )

        return node_ids



    def id2name(self, node_id:str) -> str:
        """ translate a node id to a node name

        Args:
          node_id: vm id of node

        Returns 
          node name (str)
        
        Raises:
          RuntimeError if unknown node_id
        """

        if ( node_id not in self._nodes ):
            raise RuntimeError

        return self._nodes[ node_id ]['name']


    def name2id(self, node_name:str) -> str:
        """ translate a node name to a node id

        Args:
          node_name: name of node

        Returns 
          node id (str)
        
        Raises:
          RuntimeError if unknown node_name
        """

        if ( node_name not in self._name_to_id ):
            raise RuntimeError

        return self._name_to_id[ node_name ]
    
    def nodes_in_cloud( self, cloud_name:str) -> []:
        """ returns a list of node ids in a given cloud 

        Args:
          node_name: name of cloud to return data from
        
        Returns:
          list of node ids, returns [] if no nodes in cloud

        Raises:
          None
        """

        if ( cloud_name not in self._clouds ):
            return []


        else:
            res = []
            for node in self.get_nodes(cloud=[cloud_name]):
                res.append( node[ 'id' ] )

            return res


    def find( self, id:str=None, name:str=None):
        """ find a node either by id or name

        Args:
          id: node vm id
          name: human readable node name
        
        returns 
          node info: (id, name, cloud_name, status)
        """


        if ( name is not None):
            id = self.name2id( name )

        if id is not None:
            return id, self._nodes[ id ][ 'name' ],self._nodes[ id ][ 'cloud' ], self._nodes[ id ][ 'status' ]
        


    def get_status(self, node_id:str):
        """ get status for a node
        
        Args:
          node_id: id of the node

        Returns:
          None
        
        Raises:
          RuntimeError if unknown node id
        """

        if ( node_id not in self._nodes):
            raise RuntimeError

        return self._nodes[ node_id][ 'status']

        
    def set_status(self, node_id:str, status:str):
        """ set status for a node
        
        Args:
          node_id: id of the node
          status: new status of the node

        Returns:
          None
        
        Raises:
          RuntimeError if unknown node id
        """

        if ( node_id not in self._nodes):
            raise RuntimeError

        
        logger.info("Node {}/{} status changed to {}".format( node_id, self._nodes[ node_id ][ 'name' ], status))

        self._nodes[ node_id][ 'status'] = status

        

        
