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

import ehos.vm
import ehos.htcondor
import records


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
        self._db = None



    def connect(self, url:str) -> None:
        """ connects to a database instance 
        
        Args:
        url: as specified by sqlalchemy ( {driver}://{user}:{password}@{host}:{port}/{dbase}
        
        Returns:
        none
        
        Raises:
        RuntimeError on failure.
        

        """
        
        self._db = records.Database( url )    
        


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
            raise RuntimeError("Cloud {} is already present in instances".format( name ))
        
        self._clouds[ name ] = instance

        if ( self._db is not None ):
            self._get_cloud_id( name=name)

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
            raise RuntimeError("Unknown cloud name {}".format( name ))
        
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
          node dict (name, cloud, state, status)

        Raises:
          RuntimeError if unknown node_id
        """

        return list(self._clouds.keys())
        

    def add_node( self, id:str, name:str, cloud:str, state:str='booting', status='starting')-> None:
        """ Adds a node to the class 

        Args:
          id: vm id of the node (should prob be a uuid)
          name: human readable name of node
          cloud: name of cloud where the node lives
          state: VM state of the node, default is 'booting'
          status: condor status of the node, default is 'busy'

        Returns:
          None
        
        Raises:
          RuntimeError if unknown cloud, node id/name already exist, illegal state or status
        """

        if (cloud not in self._clouds):
            raise RuntimeError
        
        if ( id in self._nodes ):
            raise RuntimeError

        if ( name in self._name_to_id ):
            raise RuntimeError

        if ( self.valid_state( state ) == False):
            raise RuntimeError("Illegal state '{}'".format( state ))
        
        if ( self.valid_status( status ) == False):
            raise RuntimeError("Illegal status '{}'".format( status ))        

        
        self._nodes[ id ] = { 'id': id,
                              'name'  : name,
                              'cloud' : cloud,
                              'state' : state,
                              'status': status}

        self._name_to_id[ name ] = id

        if ( self._db is not None ):
            self._add_node_to_db( id, name, cloud, state, status)
        

        
    def get_node(self, id:str) -> {} :
        """ get a nodes based on its id

        Args:
          id: id of the node

        Returns:
          node dict (id, name, cloud, state, status)

        Raises:
          RuntimeError if unknown node_id
        """

        if ( id not in self._nodes ):
            raise RuntimeError


        return Munch(self._nodes[ id ])


    def get_nodes(self, state=[], status=[], cloud=[]) -> {} :
        """ get a list of nodes, can be filtered based on status names

        Args:
          state: (optional) for filtering on vm state
          status: (optional) for filtering on condor status 
          cloud: (optional) for filtering on cloud name 

        Returns:
          list of node dict (name, cloud, status)

        Raises:
          RuntimeError if unknown node_id
        """

        state  = list(filter(None, state))
        status = list(filter(None, status))
        cloud  = list(filter(None, cloud))

        
        if state is not None and state != []:
            for s in state:
                if self.valid_state(s) == False:
                    raise RuntimeError("Illegal state {}".format(s))
                                       
        if status is not None and status != []:
            for s in status:
                if self.valid_status(s) == False:
                    raise RuntimeError("Illegal status {}".format(s))
            
        
        if cloud is not None and cloud != []:
            for c in cloud:
                if c not in self._clouds:
                    raise RuntimeError("Unknown cloud {}".format( c ))


        
        res = []
        for node in self._nodes:
            if ((state is None or state == []) and (status is None or status == []) and (cloud is None or cloud == [])):
                res.append( Munch(self._nodes[ node ] ))
                
            elif self._nodes[ node ][ 'state' ] in state or self._nodes[ node ][ 'status' ] in status or self._nodes[ node ]['cloud'] in cloud:
                res.append( Munch(self._nodes[ node ] ))
        

        return res        


    def node_state_counts(self ) -> {}:
        """ returns the states of nodes split into clouds

        Args:
          None

        Returns:
          dict of states and their counts + a total 

        Raises:
          None
        """

        template = { 'idle': 0,
                     'busy': 0,
                     'total':0,
                     'other':0 }


        res = { 'all': template.copy() }
        
        for node in self.get_nodes(state=['active', 'booting']):

            if node[ 'cloud' ] not in res:
                res[ node[ 'cloud' ] ] = template.copy()

            
#            pp.pprint( node )
            
            if ( node['status'] == 'idle'):
                res[ 'all' ][ 'idle'  ] += 1
                res[ 'all' ][ 'total' ] += 1

                res[ node[ 'cloud' ] ][ 'idle'  ] += 1
                res[ node[ 'cloud' ] ][ 'total' ] += 1

            elif ( node['status'] in ['busy', 'starting', 'vacating', 'benchmarking']):
                res[ 'all' ][ 'busy'  ] += 1
                res[ 'all' ][ 'total' ] += 1

                res[ node[ 'cloud' ] ][ 'busy'  ] += 1
                res[ node[ 'cloud' ] ][ 'total' ] += 1
            else:
                res[ 'all' ][ 'other'  ] += 1

                res[ node[ 'cloud' ] ][ 'other'  ] += 1
                
        return Munch(res)
                

    def get_node_ids(self, state:str=None, status:str=None, cloud:str=None) -> [] :
        """ get a list of nodes, can be filtered based on status

        Args:
          state: (optional) for filtering on vm state
          status: (optional) for filtering on condor status 

        Returns:
          list of node ids

        Raises:
          None
        """


        node_ids = []

        for node in self.get_nodes(state=[state], status=[status], cloud=[cloud]):
            node_ids.append( node['id'] )

        return node_ids



    def get_node_names(self, state:str=None, status:str=None, cloud:str=None) -> [] :
        """ get a list of node names, can be filtered based on status

        Args:
          state: (optional) for filtering on vm state 
          status: (optional) for filtering on condor status 

        Returns:
          list of node names

        Raises:
          None
        """


        node_names = []

        for node in self.get_nodes(state=[state], status=[status], cloud=[cloud]):
            node_names.append( node['name'] )

        return node_names

    

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
          node info: (id, name, cloud_name, state, status), None if id/name does not exist

        raises:
 

        """

        try:
            if ( name is not None):
                id = self.name2id( name )
        except:
            return None
#            raise RuntimeError("Node name not found {}".format( name))
            
        if id  not in self._nodes :
            return None
#            raise RuntimeError("Unknown node id {}".format( id ))
            
        if id is not None:
            return self._nodes[ id ]
        


    def get_state(self, node_id:str):
        """ get vm state for a node
        
        Args:
          node_id: id of the node

        Returns:
          None
        
        Raises:
          RuntimeError if unknown node id
        """

        if ( node_id not in self._nodes):
            raise RuntimeError

        return self._nodes[ node_id][ 'state']



    def valid_state( self, state:str) -> bool:
        """ check that a state has a valid value

        Args:
          state to check

        Returns 
          boolean 

        Raises
          None
        """

#        logger.debug("Testing the state validity of {}".format( state ))

        
        if ( state not in ehos.vm.State.__members__ ):
            return False

        return True


    def valid_status( self, status:str) -> bool:
        """ check that a state has a valid value

        Args:
          status to check

        Returns 
          boolean 

        Raises
          None
        """

#        logger.debug("Testing the status validity of {}".format( status ))

        
        if ( status not in ehos.htcondor.Node_status.__members__ ):
            return False

        return True
    
        
    
    
    def set_state(self, node_id:str, state:str):
        """ set vm status for a node
        
        Args:
          node_id: id of the node
          state: new status of the node

        Returns:
          None
        
        Raises:
          RuntimeError if unknown node id or illegal state name
        """

        if ( node_id not in self._nodes):
            raise RuntimeError("Unknown node {}".format( node_id ))

        if ( self.valid_state( state ) == False):
            raise RuntimeError("Illegal state {}".format( state ))
        
#        if ( self._nodes[ node_id][ 'state'] == state ):
#            return

        logger.info("Node {}/{} state changed to {} from {}".format( node_id, self._nodes[ node_id ][ 'name' ], self._nodes[ node_id ][ 'state' ], state))

        self._nodes[ node_id][ 'state'] = state
        
        self._update_node( node_id, state=state)

        
    def get_status(self, node_id:str):
        """ get condor status for a node
        
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
        """ set condor status for a node
        
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
        
        if (self._nodes[ node_id][ 'status'] == status):
            return


        if ( self.valid_status( status ) == False):
            raise RuntimeError("Illegal status {}".format( status ))
        
        
        logger.info("Node {}/{} status changed from {} to {}".format( node_id, self._nodes[ node_id ][ 'name' ], self._nodes[ node_id ][ 'status' ], status))

        self._nodes[ node_id][ 'status'] = status
        self._update_node( node_id, status=status)

        

        
################ DB functions #########################



    def _add_name(self, table:str, name:str):
        """ low level function for adding a name to a table

        Args:
          table: table to add to
          name: the name to get/add
        
        returns:
          None
        
        Raises:
          None
        """
        
        self._db.query("insert into {table} (name) VALUES ('{name}');".format(table=table, name=name))
        return ( self._get_name_id( table, name ))
            
            

            
    def _get_name_id(self, table:str, name:str):
        """ low level function for getting a name if present in database, otherwise add the entry.
            
        Args:
          table: table to add to
          name: the name to get/add
            
        returns:
          None
            
        Raises:
          None
        """

        rows = self._db.query("select * from {table} where name = '{name}';".format(table=table, name=name)).as_dict()

    
        if len( rows) > 0:
            return rows[ 0 ]['id']
        
        else:
            return self._add_name( table, name )
        

            
    def _get_state_id(self,  state:str ) -> int:
        """ get or create  the id corresponding to the state

        Args:
          State of a node 

        Returns
          state-id (int)

        Raises:
          None
        """

        return self._get_name_id('node_state', state)

    
    def _get_status_id(self,  status:str ) -> int:
        """ get or create  the id corresponding to the state

        Args:
          Status of a node 

        Returns
          status-id (int)

        Raises:
          None
        """

        return self._get_name_id('node_status', status)

    
    def _get_cloud_id(self,  name:str ) -> int:
        """ get or create  the id corresponding to the state

        Args:
          name of cloud

        Returns
          cloud-id (int)

        Raises:
          None
        """

        return self._get_name_id('cloud', name)


    def _get_node_id(self, id:str) -> int:
        """ gets a node-id if node exists

        Args:
          id
        
        Returns:
          db-id if exists, else None

        Raises:
          None
        """

        rows = self._db.query("select * from node where uuid = '{id}';".format(id=id)).as_dict()

    
        if len( rows) > 0:
            return rows[ 0 ]['id']
        
        else:
            return None
        
        
        
    
        
            
    def _add_node_to_db( self, id:str, name:str, cloud:str, state:str='booting', status='starting')-> None:
        """ Adds a node to the class 

        Args:
          id: vm id of the node (should prob be a uuid)
          name: human readable name of node
          cloud: name of cloud where the node lives
          state: VM state of the node, default is 'booting'
          status: condor status of the node, default is 'busy'

        Returns:
          None
        
        Raises:
          RuntimeError if unknown cloud, node id/name already exist, illegal state or status
        """

        
        node_state_id  = self._get_state_id( state )
        node_status_id = self._get_status_id( status )
        cloud_id       = self._get_cloud_id( cloud )


        node_id = self._get_node_id(id)

        if ( node_id is None):
                
            query = "insert into node (uuid, name, cloud_id, node_status_id, node_state_id) VALUES ('{uuid}', '{name}', {cloud_id}, {node_status_id}, {node_state_id});"

            self._db.query(query.format(uuid=id,
                                        name=name,
                                        cloud_id=cloud_id,
                                        node_status_id=node_status_id,
                                        node_state_id=node_state_id))
        else:
            self._update_node( id, state=state, status=status)

            
    def _update_node(self, uuid:str, state:str=None, status=None)-> None:
        """ Adds a node to the class 

        Args:
          id: vm id of the node (should prob be a uuid)
          state: VM state of the node, default is 'booting'
          status: condor status of the node, default is 'busy'

        Returns:
          None
        
        Raises:
          RuntimeError if unknown cloud, node id/name already exist, illegal state or status
        """


        if ( state is not None):
            node_state_id  = self._get_state_id( state )

            query = "update node set node_state_id={node_state_id} where uuid='{uuid}';"

            print( "running {}".format( query.format(uuid=uuid,
                                        node_state_id=node_state_id)))
            
            
            self._db.query(query.format(uuid=uuid,
                                        node_state_id=node_state_id))

        if ( status is not None):
            node_status_id  = self._get_status_id( status )

            query = "update node set node_status_id={node_status_id} where uuid='{uuid}';"

            print( "running {}".format( query.format(uuid=uuid,
                                        node_status_id=node_status_id)))
            

            self._db.query(query.format(uuid=uuid,
                                        node_status_id=node_status_id))




    def node_list_db(self ) -> {}:
        """ returns the states of nodes split into clouds

        Args:
          None

        Returns:
          dict of list of nodes

        Raises:
          None
        """

        template = { 'idle': 0,
                     'busy': 0,
                     'total':0,
                     'other':0 }


        res = { 'all': template.copy() }
        

        query =  "select uuid, n.name, state.name as state, status.name as status, c.name as cloud_name "
        query += "from node n, cloud c, node_status status, node_state state "
        query += "where n.cloud_id = c.id and n.node_state_id = state.id and n.node_status_id = status.id;";

        res = {}
    
        nodes = self._db.query( query ).as_dict()
        for node in nodes:
            cloud_name = node['cloud_name']
            if cloud_name not in res:
                res[ cloud_name ] = []
            res[ cloud_name ].append( node )


        return res

                

            
