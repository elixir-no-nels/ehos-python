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
        
        self._nodes{ id } = { 'name': name,
                              'cloud': cloud, }

        if cloud not in self._clouds:
            
            self._clouds[ cloud ] = set()

        self._clouds[ cloud ].append( id )

        self._name_id_to[ name ] = id
        

        
