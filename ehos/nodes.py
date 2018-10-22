#!/usr/bin/python3
""" 
  for tracking nodes 
 
 
 Kim Brugger (22 Oct 2018), contact: kim@brugger.dk
"""

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)



class Nodes(object):


    _nodes =

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



    def add( self, id:str, name:str, cloud:str, status:str='starting')-> None:
        """ Adds a node to the class 

        Args:
          id: vm id of the node (should prob be a uuid)
          name: human readable name of node
          cloud: name of cloud where the node lives
          status: status of the node, default is 'starting'

        Returns:
          None
        
        Raises:
          RuntimeError if node id or name  already exist
        """


        if ( id in self._nodes ):
            raise RuntimeError

        if ( name in self._name_to_id ):
            raise RuntimeError
        
        self._nodes{ id } = { 'name'  : name,
                              'cloud' : cloud,
                              'status': status}

        if cloud not in self._clouds:
            self._clouds[ cloud ] = set()

        self._clouds[ cloud ].append( id )

        self._name_id_to[ name ] = id
        

    def get_nodes(self, status:str=None) -> List :
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
            if status is None:
                node_ids.append( node_id )
                
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

        return self._nodes[ node_id ]


    def name2id(self, node_name:str) -> str:
        """ translate a node name to a node id

        Args:
          node_name: name of node

        Returns 
          node id (str)
        
        Raises:
          RuntimeError if unknown node_name
        """

        if ( node_id not in self._name_to_id ):
            raise RuntimeError

        return self._name_to_id[ node_id ]
    
    def nodes_in_cloud( self, cloud_name:str) -> List:
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
            return self._clouds[ cloud_name ]


    def find( self, id:str=None, name:str):
        """ find a node either by id or name

        Args:
          id: node vm id
          name: human readable node name
        
        returns 
          node info: (id, name, cloud_name, status)
        """


        if id is not None:
            return id, self._nodes[ id ][ 'name' ],self._nodes[ id ][ 'cloud_name' ], self._nodes[ id ][ 'status' ]
        


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

        self._nodes[ node_id][ 'status'] = status

        

        
