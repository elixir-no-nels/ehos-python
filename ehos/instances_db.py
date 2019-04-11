import ehos.db_utils as db
import ehos.log_utils as logger

class InstancesDB(object):

    def __init__(self, url):
        self._db = db.DB( url )



    def add_name(self, table:str, name:str):
        """ low level function for adding a name to a table

        Args:
          table: table to add to
          name: the name to get/add

        returns:
          None

        Raises:
          None
        """

        self._db.do("insert into {table} (name) VALUES ('{name}');".format(table=table, name=name))
        return self.get_name_id( table, name )




    def get_name_id(self, table:str, name:str):
        """ low level function for getting a name if present in database, otherwise add the entry.

        Args:
          table: table to add to
          name: the name to get/add

        returns:
          None

        Raises:
          None
        """

        rows = self._db.get_as_dict("select * from {table} where name = '{name}';".format(table=table, name=name))


        if len( rows) > 0:
            return rows[ 0 ]['id']

        else:
            return self.add_name( table, name )



    def get_state_id(self,  state:str ) -> int:
        """ get or create  the id corresponding to the state

        Args:
          State of a node

        Returns
          state-id (int)

        Raises:
          None
        """

        return self.get_name_id('node_state', state)


    def get_status_id(self,  status:str ) -> int:
        """ get or create  the id corresponding to the state

        Args:
          Status of a node

        Returns
          status-id (int)

        Raises:
          None
        """

        return self.get_name_id('node_status', status)


    def get_cloud_id(self,  name:str ) -> int:
        """ get or create  the id corresponding to the state

        Args:
          name of cloud

        Returns
          cloud-id (int)

        Raises:
          None
        """

        return self.get_name_id('cloud', name)


    def get_node_id(self, id:str) -> int:
        """ gets a node-id if node exists

        Args:
          id

        Returns:
          db-id if exists, else None

        Raises:
          None
        """

        rows = self._db.get_as_dict("select * from node where uuid = '{id}';".format(id=id))


        if len( rows) > 0:
            return rows[ 0 ]['id']

        else:
            return None






    def add_node(self, id:str, name:str, cloud:str, state:str= 'booting', status='starting')-> None:
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


        node_state_id  = self.get_state_id( state )
        node_status_id = self.get_status_id( status )
        cloud_id       = self.get_cloud_id( cloud )


        node_id = self.get_node_id(id)

        if ( node_id is None):

            query = "insert into node (uuid, name, cloud_id, node_status_id, node_state_id) VALUES ('{uuid}', '{name}', {cloud_id}, {node_status_id}, {node_state_id});"

            self._db.do(query.format(uuid=id,
                                     name=name,
                                     cloud_id=cloud_id,
                                     node_status_id=node_status_id,
                                     node_state_id=node_state_id))
        else:
            self.update_node( id, state=state, status=status)


    def update_node(self, uuid:str, state:str=None, status=None)-> None:
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
            node_state_id  = self.get_state_id( state )

            query = "update node set node_state_id={node_state_id} where uuid='{uuid}';"

            print( "running {}".format( query.format(uuid=uuid,
                                                     node_state_id=node_state_id)))


            self._db.do(query.format(uuid=uuid,
                                     node_state_id=node_state_id))

        if ( status is not None):
            node_status_id  = self.get_status_id( status )

            query = "update node set node_status_id={node_status_id} where uuid='{uuid}';"

            print( "running {}".format( query.format(uuid=uuid,
                                                     node_status_id=node_status_id)))


            self._db.do(query.format(uuid=uuid,
                                     node_status_id=node_status_id))




    def node_list(self ) -> {}:
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

        nodes = self._db.get_as_dict( query )
        for node in nodes:
            cloud_name = node['cloud_name']
            if cloud_name not in res:
                res[ cloud_name ] = []
            res[ cloud_name ].append( node )


        return res





