import ehos.db_utils as db
import ehos.log_utils as logger

class DB(object):



    def connect(self, url:str) -> None:
        self._db = db.DB( url )

    def disconnect(self) -> None:

        if self._db is not None:
            self._db.close()

    def vm_state_id(self, vm_state:str) -> int:
        """ get or create  the id corresponding to the vm_state

        Args:
          State of a node

        Returns
          state-id (int)

        Raises:
          None
        """

        return self._db.add_unique('vm_state', {'name':vm_state}, key='name')



    def node_state_id(self, node_state:str) -> int:
        """ get or create  the id corresponding to the node_state

        Args:
          Status of a node

        Returns
          status-id (int)

        Raises:
          None
        """

        return self._db.add_unique('node_state', {'name':node_state}, key='name')


    def clouds( self, **values ):

        return self._db.get('cloud', **values)



    def cloud_id(self, name:str) -> int:
        """ get or create  the id corresponding to the cloud

        Args:
          name of cloud

        Returns
          cloud-id (int)

        Raises:
          None
        """

        return self._db.add_unique('cloud', {'name':name}, key='name')


    def nodes( self, **values ):

        q =  "SELECT node.id,node.uuid, node.name, node.image, node_state.name AS node_state, vm_state.name AS vm_state FROM node, node_state, vm_state "
        q += "WHERE node.node_state_id = node_state.id AND node.vm_state_id = vm_state.id"

        for key in values:
            q += " AND node.{} = {}".format( key, values[ key ])

        return self._db.get_as_dict( q )


    def node_states(self):

        return self._db.get('node_state')

    def vm_states( self ):

        return self._db.get('vm_state')



    def node_id(self, id:str) -> int:
        """ gets a node-id if node exists

        Args:
          id

        Returns:
          db-id if exists, else None

        Raises:
          None
        """

        rows = self._db.get_as_dict("SELECT * FROM node WHERE uuid = '{id}';".format(id=id))

        if len( rows) > 0:
            return rows[ 0 ]['id']
        else:
            return None


    def add_node(self, id:str, name:str, image:str, cloud:str, vm_state:str= 'vm_booting', node_state='starting')-> None:
        """ Adds a node to the class

        Args:
          id: vm id of the node (should prob be a uuid)
          name: human readable name of node
          image: uuid of image
          cloud: name of cloud where the node lives
          vm_state: VM vm_state of the node, default is 'vm_booting'
          node_state: condor status of the node, default is 'busy'

        Returns:
          None

        Raises:
          RuntimeError if unknown cloud, node id/name already exist, illegal vm_state or status
        """


        vm_state_id    = self.vm_state_id(vm_state)
        node_state_id  = self.node_state_id(node_state)
        cloud_id       = self.cloud_id(cloud)

        node_id = self.node_id(id)


        if ( node_id is None):

            query = "INSERT INTO node (uuid, name, image, cloud_id, node_state_id, vm_state_id) VALUES ('{uuid}', '{name}', '{image}', {cloud_id}, {node_state_id}, {vm_state_id});"




            self._db.do(query.format(uuid=id,
                                     name=name,
                                     image=image,
                                     cloud_id=cloud_id,
                                     node_state_id=node_state_id,
                                     vm_state_id=vm_state_id))
        else:
            self.update_node(id, vm_state=vm_state, node_state=node_state)


    def update_node(self, uuid:str, vm_state:str=None, node_state=None)-> None:
        """ Adds a node to the class

        Args:
          id: vm id of the node (should prob be a uuid)
          vm_state: VM state of the node, default is 'booting'
          node_state: condor node_state of the node, default is 'busy'

        Returns:
          None

        Raises:
          RuntimeError if unknown cloud, node id/name already exist, illegal state or node_state
        """


        if ( vm_state is not None):
            vm_state_id  = self.vm_state_id(vm_state)

            query = "UPDATE node SET vm_state_id={vm_state_id} WHERE uuid='{uuid}';"

            self._db.do(query.format(uuid=uuid,
                                     vm_state_id=vm_state_id))

        if ( node_state is not None):
            node_state_id  = self.node_state_id(node_state)

            query = "UPDATE node SET node_state_id={node_state_id} WHERE uuid='{uuid}';"

            self._db.do(query.format(uuid=uuid,
                                     node_state_id=node_state_id))



    def settings(self, **values ):
        settings = self._db.get('setting', **values)

        config = {}

        for name, value in settings:
            print( name, value)
            #names = name.split('.')
            #for sub_name in names:


    def set_setting(self, name, value):
        """ Adds a node to the class

        Args:
            id: vm id of the node (should prob be a uuid)
            name: human readable name of node
            cloud: name of cloud where the node lives
            vm_state: VM vm_state of the node, default is 'vm_booting'
            node_state: condor status of the node, default is 'busy'

        Returns:
            None

        Raises:
            RuntimeError if unknown cloud, node id/name already exist, illegal vm_state or status
        """


        setting_id = self.setting_id(name)


        if ( setting_id is None):

            query = "INSERT INTO setting (name, value) VALUES ('{name}', '{value}');"

            self._db.do(query.format(uuid=id,
                                     name=name,
                                     value=value))
        else:
            query = "UPDATE setting SET value={value} WHERE name='{name}';"

            self._db.do(query.format(name=name,
                                     value=value))

