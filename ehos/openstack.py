#!/usr/bin/python3
""" 
 Functions related to openstack, extends the vm-api
 
 
 
 Kim Brugger (19 Oct 2018), contact: kim@brugger.dk
"""

import sys
import re
import pprint
pp = pprint.PrettyPrinter(indent=4)

import openstack


import ehos.vm 




class Openstack( ehos.vm.Vm ):



    def __init__(self):
        """ The init function, currently just sets the name of the backend 

        Args:
          None

        Returns:
          None

        Raises:
           None

        """

        self._backend = "openstack"
    
    
    
    def check_connection(self):
        """ Checks that there is a connection to the openstack, otherwise will raise an exception

        Args:
        None
        
        Returns:
        None
        
        Raises:
        ConnectionError if not connected
        """

        if  self._connection is not None:
            verbose_print("No connection to openstack clouds", FATAL)
            raise ConnectionError


    def connect(self, cloud_name:str, auth_url:str, project_name:str, username:str, password:str, region_name:str, user_domain_name:str, project_domain_name:str, no_cache:str,   ):
        """ Connects to a openstack cloud

        Args:
          cloud_name: name of the cloud this information relates to
          auth_url: authentication url
          project_name: name of project to connect to
          username: name of the user
          password: password for the user
          region_name: global connection
        
        Returns:
          None
        
        Raises:
          None
        """
        
        self._connection = openstack.connect(
            auth_url=auth_url,
            project_name=project_name,
            username=username,
            password=password,
            region_name=region_name,
            user_domain_name=user_domain_name,
            project_domain_name=project_domain_name,
            no_cache=no_cache
            
        )
        self._name = cloud_name
        ehos.verbose_print("Connected to openstack server", ehos.INFO)
        

    def server_create(self, name:str, image:str, flavor:str, network:str, key:str, security_groups:str, userdata_file:str=None): 
        """ creates and spins up a server
    
        Args:
          name: the name of the server
          image: what image to use
          flavor: the type of vm to use
          network: type of network to use
          security_groups: External access, ensure the group can connect to other server in the same group
          userdata_file
        
        Returns:
          id (str) of the server
        
        Raises:
          None
        """

    
        self.check_connection()

        
        try:
            user_data_fh = None
            if ( userdata_file is not None):
                user_data_fh = open( userdata_file, 'r')
            server = self._connection.create_server(name,
                                              image=image,
                                              flavor=flavor,
                                              network=network,
                                              key_name=key,
                                              security_groups=security_groups,
                                              # Kind of breaks with the documentation, plus needs a filehandle, not commands or a filename.
                                              # though the code looks like it should work with just a string of command(s).
                                              # Cannot be bothered to get to the bottom of this right now.
                                              userdata=user_data_fh,
                                              wait=True,
                                              auto_ip=True)
        

            ehos.verbose_print("Created server id:{} ip:{}".format( server.id, server_ip(server.id)), ehos.DEBUG)
        
            return server.id

        except Exception as e:
            raise e


    def server_list(self):
        """ gets a list of servers on the openstack cluster
        
        Args:
        None
        
        Returns:
        server dict ( name -> id )
        
        Raises:
        None
        """

        servers = {}

        for server in self._connection.compute.servers():
            servers[ server.name ] = {'id':server.id, 'status':server.status}
            servers[ server.id ]  = {'name':server.id, 'status':server.status}
            
            # htcondor changes the name slightly, so make sure we can find them gtain
            server.name = server.name.lower()
            server.name = re.sub('_','-', server.name)
            servers[ server.name ] = {'id':server.id, 'status':server.status}
    
        return servers


    
    def server_delete(self, id:str):
        """ Deletes a server instance

        Args:
          id: name/id of a server

        Returns:
          None

        Raises:
          None
        """


        if ("." in id):
            id = re.sub(r'\..*', '', id)

        servers = server_list()
        #    pp.pprint( servers )

        if id not in servers.keys():
            ehos.verbose_print("Unknown server to delete id:{}".format( id ), ehos.DEBUG)
            raise RuntimeError( "Unknown server {}".format( id ))

        if ( 'id' in servers[ id ]):
            id = servers[ id ]['id']


        self._connection.delete_server( id )
        ehos.verbose_print("Deleted server id:{}".format( id ), ehos.INFO)


    def server_log(self, id:str):
        """ streams the dmesg? log from a server
        
        Args:
        id: id/name of server
        
        Returns:
        ?
        
        Raises:
        None
        """

        # needs a check to ensure that something was returned! Will crash!
        return( self._connection.compute.get_server_console_output( id )['output'])

    def server_log_search(self,  id:str, match:str='The EHOS vm is up after '):
        """ get a server log and searches for a match 
        
        Args:
          id: id/name of the server 
          match: regex/str of log entry to look for
        
        Returns:
          matches found in log, if none found returns an empty list
        
        Raises:
          None    
        """

        log = server_log( id )
        ehos.verbose_print("Spooling server log for id:{}".format( id ), ehos.DEBUG)
        
        results = []
        
        for line in log.split("\n"):
            if ( re.search( match, line)):
                results.append( line )

        return results

    def wait_for_log_entry(self, id:str, match:str, timeout:int=200):
        """ continually checks a server log until a string match is found

        Args:
        id: id/name of the server 
        match: regex/str of log entry to look for
        timeout: max time to check logs for in seconds
        
        Returns:
        matches found in log, if none found returns an empty list

        Raises:
        TimeoutError if entry not found before timeout is 
        """

        ehos.verbose_print("Waiting for log entry  id:{} --> entry:{}".format( id, match ), ehos.INFO)

        while( True ):
            matches = server_log_search( id, match)

            if matches is not None and matches != []:
                return matches
            
            timeout -= 1
            if ( not timeout):
                raise TimeoutError

            #        print(". {}".format( timeout))
            time.sleep( 1 )        
            ehos.verbose_print("sleeping in wait_for_log_entry TO:{}".format( timeout ), ehos.DEBUG)



    
    def server_ip(self, id:str, ipv:int=4):
        """ returns the ip address of a server
        
        Args:
        id: name/id of server
        ipv: return IP4 or IP6 address. IPV4 is default
        
        Returns:
        IP address (str), if not found (wrong IPV) returns None
        
        Raises:
        None
        """

        server = self._connection.compute.get_server( id )
        
        for nic in server.addresses['dualStack']:
            if ( nic['version'] == ipv):
                return nic['addr']

        return None



    def server_stop(self, id:str, timeout:int=200): 
        """ stops a server
        
        Args:
        id: the name of the server
        timeout: max time (s) to wait for the server to shotdown

        Returns:
        None
        
        Raises:
        TimeoutError: if the server is not in shutdown status within the timeout time
        """


        check_connection()
        ehos.verbose_print("Stopping server id{} ".format( id ), ehos.INFO)
        
        server = self._connection.compute.get_server( id )
        self._connection.compute.stop_server( server )
        while ( True ):
            server = self._connection.compute.get_server( id )
            if ( server.status.lower() == 'shutoff'):
                return

            timeout -= 1
            if ( not timeout ):
                raise TimeoutError

            ehos.verbose_print("sleeping in server stop TO:{} status:{}".format( timeout, server.status ), ehos.DEBUG)
            time.sleep(1)

        ehos.verbose_print("Server stopped id:{} ".format( id ), ehos.INFO)


        def _wait_for_image_creation( image_name:str, timeout:int=200):
            """ Wait for a single image with the given name exists and them return the id of it
            
            Args:
            image_name: name of the image
            timeout: how long to wait for the image to be created.
            
            Returns:
            image id (str)
            
            Raises:
            None
            """

            ehos.verbose_print("Waiting for image creationimage_name:{} ".format( image_name ), ehos.INFO)
            while ( True ):
                
                nr_images = 0
                image_id = None
                image_status = None
                for image in self._connection.image.images():
                    if image.name == image_name:
                        nr_images += 1
                        image_id = image.id
                        image_status = image.status.lower()

                # Only one image with our name exist, so return its id
                if nr_images == 1 and image_status == 'active':
                    ehos.verbose_print("Created image from server id{}, image_id:{} ".format( id, image_id ), ehos.INFO)
                    return image_id

                # decrease the timeout counter, if hits 0 raise an exception, otherwise sleep a bit
                timeout -= 1
                if ( not timeout ):
                    raise TimeoutError
                time.sleep(1)
                ehos.verbose_print("sleeping in wait_for_image_creation TO:{} NR:{} status:{}".format( timeout, nr_images, image_status ), ehos.DEBUG)
        
    def make_image_from_server(self,  id:str, image_name:str, timeout:int=200):
        """ creates an image from a server. Due to some bug in the openstack we spin it down before doing the backup

        The function has a timeout variable to ensure we dont end up in an infinite loop
        
        Args:
        id: server name/id
        image_name: the name of the backup to create
        timeout: how long to wait for the image to be created.
        
        Returns:
        None
        
        Raises:
        TimeoutError: if the image is not created within the timeout time
        
        """



        ehos.verbose_print("Creating an image from server id{}, image_name:{} ".format( id, image_name ), ehos.INFO)
        server_stop( id )
        # rotation == 1 will only keep one version of this name, not sure about backup type
        self._connection.compute.backup_server( id, image_name, backup_type='', rotation=1 )
        
        return _wait_for_image_creation( image_name )


    
    

