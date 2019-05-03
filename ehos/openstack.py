#!/usr/bin/python3
""" 
 Functions related to openstack, extends the vm-api
 
 
 
 Kim Brugger (19 Oct 2018), contact: kim@brugger.dk
"""

import sys
import os
import re
import pprint
pp = pprint.PrettyPrinter(indent=4)
import time

import ehos.log_utils as logger

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
        self._connection = None
    
    def check_connection(self):
        """ Checks that there is a connection to the openstack, otherwise will raise an exception

        Args:
        None
        
        Returns:
        None
        
        Raises:
        ConnectionError if not connected
        """

        if  self._connection is None:
            logger.critical("No connection to openstack cloud")
            raise ConnectionError


    def connect(self, cloud_name:str, auth_url:str, project_name:str, username:str, password:str, region_name:str, user_domain_name:str, project_domain_name:str, **kwargs  ):
        """ Connects to a openstack cloud

        Args:
          cloud_name: name of the cloud this information relates to
          auth_url: authentication url
          project_name: name of project to connect to
          username: name of the user
          password: password for the user
          region_name: global connection
          **kwargs catches extra cloud information from the config file
        
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
            project_domain_name=project_domain_name
        )

        self._name = cloud_name
        logger.debug("Connected to openstack server {}".format( cloud_name ))
        

    def server_create(self, name:str, image:str, flavor:str, network:str, key:str, security_groups:str, userdata_file:str=None, **kwargs): 
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

        if ( self.get_images(name=image) == []):
            logger.critical("Image {} does not exist in the openstack instance".format(image))
            raise( RuntimeError("Image {} does not exist in the openstack instance".format(image)))




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
        

            logger.debug("Created server id:{} ip:{}".format( server.id, self.server_ip(server.id)))
        
            return server.id

        except Exception as e:
            print( e )
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
            server.name = re.sub("_","-", server.name)
            servers[ server.id ] = {'id':server.id, 'name':server.name.lower(), 'vm_state':"vm_"+server.status.lower()}
            servers[ server.name.lower() ] = servers[ server.id ]

        logger.debug("Servers: \n{}".format( pp.pformat( servers )))

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

        servers = self.server_list()
        #    pp.pprint( servers )

        if id not in servers.keys():
            logger.debug("Unknown server to delete id:{}".format( id ))
            raise RuntimeError( "Unknown server {}".format( id ))


        self._connection.delete_server( id )
        logger.debug("Deleted server id:{}".format( id ))


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

        log = self.server_log( id )
        logger.debug("Spooling server log for id:{}".format( id ))
        
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

        logger.debug("Waiting for log entry  id:{} --> entry:{}".format( id, match ))

        while( True ):
            matches = self.server_log_search( id, match)

            if matches is not None and matches != []:
                return matches
            
            timeout -= 1
            if ( not timeout):
                raise TimeoutError

            #        print(". {}".format( timeout))
            time.sleep( 1 )        
            logger.debug("sleeping in wait_for_log_entry TO:{}".format( timeout ))



    
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


        self.check_connection()
        logger.debug("Stopping server id{} ".format( id ))
        
        server = self._connection.compute.get_server( id )
        self._connection.compute.stop_server( server )
        while ( True ):
            server = self._connection.compute.get_server( id )
            if ( server.status.lower() == 'vm_shutoff'):
                return

            timeout -= 1
            if ( not timeout ):
                raise TimeoutError

            logger.debug("sleeping in server stop TO:{} status:{}".format( timeout, server.status ))
            time.sleep(1)

        logger.info("Server stopped id:{} ".format( id ))


    def _wait_for_image_creation(self, image_name:str, timeout:int=200):
        """ Wait for a single image with the given name exists and them return the id of it

        Args:
        image_name: name of the image
        timeout: how long to wait for the image to be created.
        Returns:
        image id (str)

        Raises:
        None
        """

        logger.info("Waiting for image creation image_name:{} ".format( image_name ))
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
            if nr_images == 1 and image_status == 'vm_active':
                logger.info("Created image from server id{}, image_id:{} ".format( id, image_id ))
                return image_id

            # decrease the timeout counter, if hits 0 raise an exception, otherwise sleep a bit
            timeout -= 1
            if ( not timeout ):
                raise TimeoutError
            time.sleep(1)
            logger.debug("sleeping in wait_for_image_creation TO:{} NR:{} status:{}".format( timeout, nr_images, image_status ))
        
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



        logger.info("Creating an image from server id{}, image_name:{} ".format( id, image_name ))
        self.server_stop( id )
        # rotation == 1 will only keep one version of this name, not sure about backup type
        self._connection.compute.backup_server( id, image_name, backup_type='', rotation=1 )
        
        return self._wait_for_image_creation( image_name )


    
    
    def get_resources(self):
        """ get the resources available for the cloud

        Args:
          None
        
        Returns:
          dict of useful values

        Raises:
          None
        """
        
        limits = self._connection.compute.get_limits()
#        pp.pprint( self._connection.block_storage.get_limits())

        total_cores      = limits.absolute.total_cores
        total_cores_used = limits.absolute.total_cores_used
        instances        = limits.absolute.instances
        instances_used   = limits.absolute.instances_used
        total_ram        = limits.absolute.total_ram
        total_ram_used   = limits.absolute.total_ram_used


#        pp.pprint ( limits.absolute )
        
        res = {'total_cores'      : total_cores,
               'total_cores_used' : total_cores_used,
               'instances'        : instances,
               'instances_used'   : instances_used,
               'total_ram'        : total_ram,
               'total_ram_used'   : total_ram_used }



        
        return res

    def get_resources_available(self):
        """ get the resources available for the cloud

        Args:
          None
        
        Returns:
          dict of valuess ( cores, instances, ram)

        Raises:
          None
        """
        raw_res = self.get_resources()
#        pp.pprint( raw_res)

        return {'cores'     : raw_res['total_cores'] - raw_res['total_cores_used'],
                'instances' : raw_res['instances'] - raw_res['instances_used'],
                'ram'       : raw_res['total_ram'] - raw_res['total_ram_used']}
        


    def get_images( self, active:bool=True, name=None ):
        """ get the images currently available on the cloud

        Args:        
          active, returns only active images
          name to filter on. Match is case in-sensitive
        
        Return
          list of dict of image info ( includes id, name, min-requirements, etc)

        Raises:
          None
        """

        images = []
        for image in self._connection.image.images():
            if active and image.status!="active":
                continue

            if (name is not None and
                    (name.lower() not in image.name.lower() and
                     name.lower() not in image.id.lower())):
                continue
                
            
            image_info = { 'id': image.id,
                           'min_disk': image.min_disk,
                           'name': image.name,
			   'tags': image.tags,
			   'min_ram': image.min_ram,
			   'status': image.status}
                           
            
            images.append( image_info )

        return images


    def get_flavours( self ):
        """ get the flavours currently available on the cloud

        Only returns flavours that are active and public

        Args:
          None
        
        Return
          dict list of flavours (including, id, cpus, ram and name)

        Raises:
          None
        """

        flavours = []
        for flavour in self._connection.compute.flavors():

            if flavour.is_public != True:
                continue

            
            if flavour.is_disabled != False:
                continue

            flavour_info = { 'id': flavour.id,
                             'name': flavour.name,
                             'ram': flavour.ram,
                             'cpus': flavour.vcpus,
                             'disk': flavour.disk }
            

            
            
            flavours.append( flavour_info )

        return flavours
    



    def volume_create(self, size:int, name:str=None, **kwargs) -> str:
        """ Create a volume

        Args:
          size in GB
          name of the volume (set to none for UID name)

        Returns:
          id of volume (str)

        Raises:
          RuntimeError if 

        """

        volume = self._connection.create_volume( size=size, name=name )

        logger.info( "Created volume id {} with the size of {}GB".format( volume.id, size ))
        
        return volume.id

    def volume_delete(self, id:str=None, wait:bool=True) -> None:
        """ deletes a volume

        Args:
          id: volume id
          wait: wait for the volume to be deleted before returning.
          

        Returns:
          None

        Raises:
          RuntimeError if no id or name provided

        """

        logger.debug("Trying to delete volume {}".format( id ))

        if ( self._volume_exists( id ) == False ):
            logger.debug("Volume {} does not exist, cannot delete it".format( id ))
            return
        
        
        if ( id is not None):
            self._connection.delete_volume( id )
            logger.debug("Deleted volume id:{}".format( id ))
            if ( wait ):
                self._wait_for_volume_deletion( id )

        else:
            raise RuntimeError("No id or name provided")


    def _volume_exists(self, volume_id:str) -> bool:
        """ Checks if a volume exists or not in the volume list

        Args:
          volume_id to look for

        Returns:
          True/False if present/not-present

        Raises:
          None
        """

        for volume in self.volumes():
#            print("{} ===== {}".format( volume['id'], volume_id))
            if ( volume['id'] == volume_id ):
                    return True
        return False

        
        
    def _wait_for_volume_deletion(self, id:str, sleep_time:float=0.05, timeout:float=20.0):
        """ hangs till the volume has been deleted.

        Args:
          id volume to watch
          sleep_time: amount of time to sleep between checks
          timeout: max time to check before raising a RuntimeError

        Returns:
          None
        
        Raises:
          RuntimeError if volume not deleted within the timeout time
        """

        logger.debug("Waiting for volume {} being deleted".format( id ))

        
        while( True ):
            if ( self._volume_exists( id ) == False ):
                logger.debug("Volume {} has been successfully deleted".format( id ))
                return

            time.sleep( sleep_time )

            timeout -= sleep_time

            if ( timeout < 0.0 ):
                raise RuntimeError("Volume {} has not been deleted".format( id ))
            
            
        
    def volumes(self):
        """ get volumes information, currently one volume can only be attached to one node.

        Args:
          None

        Returns:
          dict of volumes w/ keys (size, attachment, name, id )

        Raises:
          none
        """

        volumes = []
        for volume in self._connection.block_storage.volumes( details=True ):
#            pp.pprint( volume )

            volume_data = { 'id': volume.id,
                            'name' : volume.name,
                            'size': volume.size,
                            'description': volume.description,
                            'server_id': None,
                            'device': None,
                            'attachment_id': None,
                            }

            if volume.attachments != []:
                attachment = volume.attachments[ 0 ]
                volume_data[ 'server_id']     = attachment[ 'server_id' ]
                volume_data[ 'device']        = attachment[ 'device' ]
                volume_data[ 'attachment_id'] = attachment[ 'id' ]
                
            volumes.append( volume_data )

        return volumes

            
    def attach_volume( self, server_id:str, volume_id:str):
        """ Attaches a volume to a server

        Args:
          server_id, id of the server
          volume_id, id of the volume

        Returns:
          None

        Raises:
          None

        """

        attachment = self._connection.compute.create_volume_attachment(server=server_id, volumeId=volume_id)
#        pp.pprint( attachment )
        return attachment.device
        

    def _get_attachment_id(server_id:str, volume_id:str) -> str:
        """ get an attachment id for the connections between server_id and volume_id

        Args:
          server_id 
          volume_id

        Returns:
          attachment_id, else None

        Raises:
          None
        """


        for volume in self.volumes():
            if ( volume['server_id'] == server_id and
                 volume['volume_id'] == volume_id):
                
                volume['attachment_id']

        return None

    def _get_attachment_server_id(attachment_id:str) -> str:
        """ get a server-id for an  attachment

        Args:
          attachment_id 

        Returns:
          server_id, else None

        Raises:
          None
        """


        for volume in self.volumes():
            if ( volume['attachment_id'] == attachment_id):
                
                volume['server_id']

        return None
    
    
    
    def server_attached_to_volume( self, volume_id:str) -> str:
        """ Find the server attached to a volume, if none returns None

        Args:
          volume id

        returns 
          server id (str or none)

        raises:
          None
        """

        for volume in self.volumes():
            if ( volume['id'] == volume_id ):
                return volume['server_id']

        return None


    def volumes_attached_to_server( self, server_id:str) -> []:
        """ Find the server attached to a volume, if none returns None

        Args:
          server id

        returns 
          server id (str or none)

        raises:
          None
        """

        volumes = []
        
        for volume in self.volumes():
            if ( volume['server_id'] == server_id ):
                volumes.append(volume['id'])

        return volumes

    def server_attachments(self, server_id):
        """ returns all the attachment id's related to a server

        Args:
          server_id

        returns 
          attachment id(s) (str or none)

        raises:
          None
        """


        attachments = []
        
        for volume in self.volumes():
            if ( volume['server_id'] == server_id ):
                attachments.append(volume['attachment_id'])

        return attachments
    
    
    def detach_volume( self, attachment_id:str, server_id:str=None, volume_id:str=None) -> None:
        """ Detaches a volume to a server

        Args:
          attachment_id id of the server
          server_id, id of the server
          volume_id, id of the server

        Returns:
          None

        Raises:
          None

        """

        
        if ( attachment_id is None ):
            if ( server_id is not None and volume_id is not None):
                attachment_id = self._get_attachment_id( server_id, volume_id)
                if ( attachment_id is None ):
                    raise RuntimeError( "Could not find attachment if for server:{}, volume:{}".format(server_id, volume_id))
            else:
                raise RuntimeError( "Need to provide either a attachment-id or server & volume id")
                

        # Function needs a server-id to detach volume, as the user didnt provide one, get it
        if ( server_id is None ):
            server_id = self._get_attachment_server_id( attachment_id )
            if ( server_id is None ):
                raise RuntimeError( "Could not find server for attachment:{}".format(attachment_id))
        
        attachment = self._connection.compute.delete_volume_attachment(attachment_id, server=server_id)
        
    

    def detach_volumes_from_server(self, id ) -> int:
        """ detaches all volumes attached to a node

        args:
          id: id/name of server

        returns:
          nr of volumes detached

        raises:
          passes on from other functions
        """

        volumes_detached = 0
        
        for attachment_id in self.server_attachments( id ):
            self.detach_volume( attachment_id, server_id=id)
            time.sleep( 1 )
            volumes_detached +=1

        return volumes_detached;
        


    def security_groups(self):
        """ fetches the security groups from a openstack 

        Args:
          None

        Returns 
          id:name dict

        Raises:
          None
        """


        security_groups = self._connection.network.security_groups()

        res = {}
        
        for security_group in security_groups:
#            res[ security_group.id ] = {'name' : security_group.name,
#                                        'rules': []}

            res[ security_group.name ] = {'id' : security_group.id,
                                          'rules': []}



            
            for rule in security_group.security_group_rules:

                details = {}
                

                
                details[ 'direction'        ] =  rule[ 'direction' ]
                details[ 'protocol'         ] =  rule[ 'protocol' ]
                details[ 'ports'            ] = (rule[ 'port_range_min' ], rule[ 'port_range_max' ])
                details[ 'remote_group_id'  ] =  rule[ 'remote_group_id' ]
                details[ 'remote_ip_range'  ] =  rule[ 'remote_ip_prefix' ]
                details[ 'ethernet_version' ] =  rule[ 'ethertype' ]

                res[ security_group.name ]['rules'].append( details )

                
        return res


    
    def security_group_create(self, name:str):
        """ creates a security group for a given connectiona
    
        Args:
          name: the name of the security groupd
        
        Returns:
          id (str) of the security group
        
        Raises:
          RuntimeError if a groupd with this name already exists.
        """


        groups = self.security_groups()

        if name in groups:
            raise RuntimeError("Openstack security group {} already exist".format( name ))
        
        
        security_group_id = self._connection.network.create_security_group( name=name)

        return security_group_id

    def security_group_add_rule(self, id:str, direction:str, port:int, protocol:str, remote_group_id:str=None, remote_ip_range:str=None ):
        """ adds a firewall rule for a security group 
    
        Args:
          id of the security_group
          direction either ingress or egress
          port to open for
          protocol, we like tcp and udp so far
          remote_group: if intranet communication between nodes in this security group
          remote_ip_range: ip range filtering.
        
        Returns:
          None
        
        Raises:
          None
          RuntimeError if a groupd with this name already exists.
        """

        print("\nRule  details",
              id,
              direction,
              port,
              port,
              protocol,
              remote_group_id,
              remote_ip_range,"\n")

        
        self._connection.network.create_security_group_rule(security_group_id=id,
                                                            direction=direction,
                                                            port_range_min=port,
                                                            port_range_max=port,
                                                            protocol=protocol,
                                                            remote_group_id=remote_group_id,
                                                            remote_ip_prefix=remote_ip_range)





    def firewall_add_incoming_rule(self, name:str, port:int, protocol:str, remote_group:str=None, remote_ip_range:str=None ):
        """ adds an incoming firewall rule for a security group 
    
        Args:
          name of the security_group
          port to open for
          protocol, we like tcp and udp so far
          remote_group: if intranet communication between nodes in this security group
          remote_ip_range: ip range filtering.
        
        Returns:
          None
        
        Raises:
          None
          RuntimeError if a groupd with this name already exists.
        """

        groups = self.security_groups()

        if name not in groups:
            raise RuntimeError("Unknown security group {} tp update".format( name ))

        remote_group_id = None
        if remote_group is not None:
            if remote_group not in groups:
                raise RuntimeError("Unknown remote security group '{}'".format( name ))
            else:
                remote_group_id = groups[remote_group]['id']

        if 'rules' in groups[ name ]:
            for rule in groups[ name ][ 'rules' ]:
                
                if ( rule['ports']      == (port,port) and
                     rule['protocol']  == protocol and
                     rule['direction']  == 'ingress' and 
                     rule['remote_group_id']  == remote_group_id and
                     rule['remote_ip_range']  == remote_ip_range):
                    
                    logger.debug('firewall rule already exists, skipping it')
                    return
                 
            
                
        self.security_group_add_rule(id=groups[name]['id'],
                                     direction='ingress',
                                     port=port,
                                     protocol=protocol,
                                     remote_group_id=remote_group_id,
                                     remote_ip_range=remote_ip_range)


    def firewall_add_incoming_rules(self, name:str, rules:list ):
        """ adds an incoming firewall rule for a security group 
    
        Args:
          name of the security_group
          rules is a list of dicts all containing:
            port to open for
            protocol, we like tcp and udp so far
            remote_group: if intranet communication between nodes in this security group
            remote_ip_range: ip range filtering.
        
        Returns:
          None
        
        Raises:
          None
          RuntimeError if a groupd with this name already exists.
        """

        for rule in rules:
            self.firewall_add_incoming_rule( name=name, **rule )



    def upload_key(self, public_key:str, name:str='ehos'):
        """ Uploads a public key to the openstack server

        Args:
          public_key key to upload
          name of key, default ehos
        Returns
          None

        Raises:
          None

        """



        for keypair in self.get_keys():
            if ( keypair['name' ] == name ):
                logger.debug( "Key already exist in cloud, skipping it")
                return

        pub_key = open(os.path.expanduser(public_key)).read()
            
        self._connection.compute.create_keypair(name=name, public_key=pub_key)

                
    def get_keys(self):
        """ Get list of keys, mainly used to ensure a key name is not already used.


        Args:
          None

        Returns:
          dict of keys
        
        Raises:
          None
 
        """


        keys = []

        for entry in self._connection.compute.keypairs():
            key = {}
            key['name']        =  entry.name
            key['public_key']  =  entry.public_key
            key['fingerprint'] =  entry.fingerprint

            
            keys.append( key )

        return keys

        

