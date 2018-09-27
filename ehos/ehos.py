#!/usr/bin/python
# 
# 
# 
# 
# Kim Brugger (14 Sep 2018), contact: kim@brugger.dk

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)
import traceback
import time
import re
import shutil
import shlex
from typing import List, Tuple
import subprocess

import openstack

connection = None

_server_cache = {}


def check_connection():
    """ Checks that there is a connection to the openstack, otherwise will raise an exception

    Args:
      None
    
    Returns:
      None

    Raises:
      ConnectionError if not connected
    """

    if connection is None:
        raise ConnectionError

def connect_yaml( cloud_name:str ):
    """
      Args: 
       cloud_name: name of cloud to connect to


      Returns:
        None

      Raises:
        reraise any openstack exception
    """

    try:
        global connection
        connection = openstack.connect( cloud=cloud_name )
    except Exception as e:
        print( "Unexpected error:", sys.exc_info()[0])
        print( e )
        raise e


def connect(auth_url:str, project_name:str, username:str, password:str, region_name:str, user_domain_name:str, project_domain_name:str, no_cache:str,   ):
    """ Connects to a openstack cloud

    Args:
      auth_url: authentication url
      project_name: name of project to connect to
      username: name of the user
      password: password for the user
      region_name:
    
    global connection

    Returns:
      None
    
    Raises:
      None
    """

    global connection
    connection = openstack.connect(
        auth_url=auth_url,
        project_name=project_name,
        username=username,
        password=password,
        region_name=region_name,
        user_domain_name=user_domain_name,
        project_domain_name=project_domain_name,
        no_cache=no_cache
        
    )





def server_create(name:str, image:str, flavor:str, network:str, key:str, security_groups:str, userdata_file:str=None): 
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

    
    check_connection()

    
    try:
        user_data_fh = None
        if ( userdata_file is not None):
            user_data_fh = open( userdata_file, 'r')
        server = connection.create_server(name,
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
        
        for nic in server.addresses.dualStack:
            if ( nic.version == 4):
                print( "Server IP: {}".format( nic.addr))
                
        print("Server ({}) is up and running ...".format( server.id ))

        global _server_cache
        _server_cache[ server.id ] = server

        return server.id

    except Exception as e:
        print( "Unexpected error:", sys.exc_info()[0] )
        print( e )
        raise e



def server_delete(id:str):
    """ Deletes a server instance

    Args:
      id: name/id of a server

    Returns:
      None

    Raises:
      None
    """

    connection.delete_server(id )
    
def servers():
    print("List Servers:")

    for server in connection.compute.servers():
        print("\t".join(map(str, [server.id, server.name, server.status])))


def server_log(id:str):
    """ streams the dmesg? log from a server
    
    Args:
      id: id/name of server
    
    Returns:
      ?

    Raises:
      None
    """

    return( connection.compute.get_server_console_output( id )['output'])

def server_log_search( id:str, match:str):
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

    
    results = []
    
    for line in log.split("\n"):
        if ( re.search( match, line)):
            results.append( line )

    return results

def wait_for_log_entry(id:str, match:str, timeout:int=200):
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

    while( True ):
        matches = server_log_search( id, match)

        if matches is not None and matches != []:
            return matches

        timeout -= 1
        if ( not timeout):
            raise TimeoutError

#        print(". {}".format( timeout))
        time.sleep( 1 )        
    
    
    
        
def server_ip(id:str, ipv:int=4):
    """ returns the ip address of a server
    
    Args:
      id: name/id of server
      ipv: return IP4 or IP6 address. IPV4 is default

    Returns:
      IP address (str), if not found (wrong IPV) returns None

    Raises:
      None
    """

    server = connection.compute.get_server( id )

    for nic in server.addresses['dualStack']:
        if ( nic['version'] == ipv):
            return nic['addr']
    return None



def server_stop(id:str): 
    """ stops a server
    
    Args:
      id: the name of the server

    Returns:
      None

    Raises:
      pass any openstack exceptions along.
    """

    
    check_connection()

    server = connection.compute.get_server( id )
    connection.compute.stop_server( server )
    

    
def make_image_from_server( id:str, image_name:str, timeout:int=20):
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
      pass the openstack exceptions along

    """

    server_stop( id )
    # rotation == 1 will only keep one version of this name, not sure about backup type
    connection.compute.backup_server( id, image_name, backup_type='', rotation=1 )

    def _wait_for_image_creation( image_name:str, timeout:int=timeout):
        """ Wait for a single image with the given name exists and them return the id of it

        This loop

        Args:
          image_name: name of the image
          timeout: how long to wait for the image to be created.

        Returns:
          image id (str)
        
        Raises:
          None
        """

        timeout = timeout
        
        while ( True ):
        
            nr_images = 0
            image_id = None
            for image in connection.image.images():
                if image.name == image_name:
                    print( image.name )
                    nr_images += 1
                    image_id = image.id

            # Only one image with our name exist, so return its id
            if nr_images == 1:
                return image_id

            # decrease the timeout counter, if hits 0 raise an exception, otherwise sleep a bit
            timeout -= 1
            if ( not timeout ):
                raise TimeoutError
            print( "Sleep" )
            time.sleep(1)

        image = connection.get_image( image_name )

    return _wait_for_image_creation( image_name )
    
    
    

def datetimestamp():
    """ Creates a timestamp so we can make unique server names

    Args:
      none
    
    Returns:
      timestamp (string)

    Raises:
      none
    """
    ts = time.time()
    ts = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%dT%H%M%S')




def get_node_id():
    """ Cloud init stores the node id on disk so it possible to use this for us to get host information that way

    Ideally this would have been done using the cloud_init library, but that is python2 only, so this is a bit of a hack

    Args:
      None

    Returns:
      node id (string)
    
    Raises:
      None
    """


    fh = open('/var/lib/cloud/data/instance-id', 'r')
    id  = fh.readline().rstrip("\n")
    fh.close()

    return id

    
    


def alter_file(filename:str, pattern:str=None, replace:str=None, patterns:List[ Tuple[ str, str]]=None):
    """ Alter a file by searching for a pattern (str or regex) and replace it

    The function further more make a backup copy of the original file

    Args:
      filename: The file to change
      pattern: the pattern (str/regex) to search for in the file
      replace: what to replace the pattern with
      patterns: a list of replacements to be done
    Returns:
      None

    Raises:
      RuntimeError if no patter

    """

    # this is foobared but I cannot find the strength to do this right now
    if ( pattern is None and
         replace is None and
         patterns is None):


        #  or

        #  ( patterns is not None and
        #    (pattern is not None or
        #     replace is not None))

        # or
        
        #  ( pattern is None or
        #    replace is None )):
        

        raise RuntimeError('Wrong use of alter_file function parameters, provide either a pattern and a replace or a list of patterns')



    
    
    
    # first make a copy of the file

    shutil.copy( filename, "{}.orginal".format( filename ))
    
    # open and read in the while file as a single string
    with open( filename, 'r') as fh:
        lines = "".join(fh.readlines())
        fh.close()

    if patterns is None:
        patterns = [ (pattern, replace) ]

    for pattern, replace in patterns:
        print( pattern, " ---> ", replace )
        # replace the pattern with the replacement string
        lines = re.sub(pattern, replace, lines)

    with  open(filename, 'w') as fh:
        fh.write( lines )
        fh.close()

    

    

def system_call(command:str):
    """ runs a system command

    Args:
      command to run

    Returns:
      None

    Raises:
      None
    
    """

    subprocess.run(shlex.split( command ), shell=False, check=True)
        
        
