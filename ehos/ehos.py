#!/usr/bin/python
# 
# 
# 
# 
# Kim Brugger (14 Sep 2018), contact: kim@brugger.dk

import os
import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)
import traceback
import random
import string
import time
import time
import datetime
import re
import shutil
import shlex
from typing import List, Tuple
import subprocess

import openstack

connection = None
level = 1


FATAL = 1
ERROR = 2
WARN  = 3
INFO  = 4
DEBUG = 5


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
        verbose_print("No connection to openstack server", FATAL)
        raise ConnectionError

def connect_yaml( cloud_name:str ):
    """ connect to openstack server using the cloud.yaml config file, openstack default.

      Args: 
       cloud_name: name of cloud to connect to


      Returns:
        None

      Raises:
        None
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
    verbose_print("Connected to openstack server", INFO)



    


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
        

        verbose_print("Created server id:{} ip:{}".format( server.id, server_ip(server.id)), DEBUG)
        
        global _server_cache
        _server_cache[ server.id ] = server

        return server.id

    except Exception as e:
        raise e


def server_list():
    """ gets a list of servers on the openstack cluster

    Args:
      None

    Returns:
      server dict ( name -> id )

    Raises:
      None
    """

    servers = {}
    
    for server in connection.compute.servers():
        servers[ server.name ] = {'id':server.id, 'status':server.status}
        servers[ server.id ]  = {'name':server.id, 'status':server.status}
    
        # htcondor changes the name slightly, so make sure we can find them gtain
        server.name = server.name.lower()
        server.name = re.sub('_','-', server.name)
        servers[ server.name ] = {'id':server.id, 'status':server.status}
        
    return servers

    
def server_delete(id:str):
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
        verbose_print("Unknown server to delete id:{}".format( id ), ehos.DEBUG)
        raise RuntimeError( "Unknown server {}".format( id ))
    
    if ( 'id' in servers[ id ]):
        id = servers[ id ]['id']

    
    connection.delete_server( id )
    verbose_print("Deleted server id:{}".format( id ), INFO)
    
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
    verbose_print("Spooling server log for id:{}".format( id ), DEBUG)
    
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

    verbose_print("Waiting for log entry  id:{} --> entry:{}".format( id, match ), INFO)

    while( True ):
        matches = server_log_search( id, match)

        if matches is not None and matches != []:
            return matches

        timeout -= 1
        if ( not timeout):
            raise TimeoutError

#        print(". {}".format( timeout))
        time.sleep( 1 )        
        verbose_print("sleeping in wait_for_log_entry TO:{}".format( timeout ), DEBUG)

    
    
        
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



def server_stop(id:str, timeout:int=200): 
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
    verbose_print("Stopping server id{} ".format( id ), INFO)

    server = connection.compute.get_server( id )
    connection.compute.stop_server( server )
    while ( True ):
        server = connection.compute.get_server( id )
        if ( server.status.lower() == 'shutoff'):
            return

        timeout -= 1
        if ( not timeout ):
            raise TimeoutError

        verbose_print("sleeping in server stop TO:{} status:{}".format( timeout, server.status ), DEBUG)
        time.sleep(1)
    
    verbose_print("Server stopped id:{} ".format( id ), INFO)

    
def make_image_from_server( id:str, image_name:str, timeout:int=200):
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

        verbose_print("Waiting for image creationimage_name:{} ".format( image_name ), INFO)
        while ( True ):
        
            nr_images = 0
            image_id = None
            image_status = None
            for image in connection.image.images():
                if image.name == image_name:
                    nr_images += 1
                    image_id = image.id
                    image_status = image.status.lower()

            # Only one image with our name exist, so return its id
            if nr_images == 1 and image_status == 'active':
                verbose_print("Created image from server id{}, image_id:{} ".format( id, image_id ), INFO)
                return image_id

            # decrease the timeout counter, if hits 0 raise an exception, otherwise sleep a bit
            timeout -= 1
            if ( not timeout ):
                raise TimeoutError
            time.sleep(1)

            verbose_print("sleeping in wait_for_image_creation TO:{} NR:{} status:{}".format( timeout, nr_images, image_status ), DEBUG)


    verbose_print("Creating an image from server id{}, image_name:{} ".format( id, image_name ), INFO)
    server_stop( id )
    # rotation == 1 will only keep one version of this name, not sure about backup type
    connection.compute.backup_server( id, image_name, backup_type='', rotation=1 )

    return _wait_for_image_creation( image_name )
    
    
    

def make_uid_domain_name(length:int=3):
    """ Makes a uid domain name

    Args:
      length: domain length
    
    Returns:
      uid domain name (str)

    Raises:
      RuntimeError if length is longer than our word list

    """


    quote = "Piglet was so excited at the idea of being Useful that he forgot to be frightened any more, and when Rabbit went on to say that Kangas were only Fierce during the winter months, being at other times of an Affectionate Disposition, he could hardly sit still, he was so eager to begin being useful at once"

#    quote = "The more he looked inside the more Piglet wasnt there"
    quote = re.sub(",", "", quote);

    words = list(set( quote.lower().split(" ")))

    if (len(words) < length):
        raise RuntimeError( 'length required is longer than dictonary used')
        

    
    choices = []
    while( True ):
        word = random.choice(words)

        if word in choices:
            continue
            
        choices.append( word )

        if (len( choices ) == length):
            break
        
    return('.'.join(choices))
    

def timestamp():
    """ gets a sec since 1.1.1970

    "Args:
      None

    Returns:
      Secs since the epoc
    
    Raises:
      None
    """

    return int(time.time())


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

    return ts


def random_string(N:int=10) -> str:
    """ Makes a random string the length of N

    Args:
      length: length of random string, default is 10 chars

    Returns:
      random string (str)

    Raises:
      None
    """

    chars=string.ascii_lowercase + string.ascii_uppercase + string.digits

    res = ""
    
    for _ in range( N ):
        res += random.SystemRandom().choice(chars)

    return res
        

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


def readin_whole_file(filename:str):
    """ reads in a whole file as a single string

    Args:
      filename: name of file to read

    Returns
      file contents (str)

    Raises:
      None
    """

    with open( filename, 'r') as fh:
        lines = "".join(fh.readlines())
        fh.close()
    
    return lines

    
def find_config_file( filename:str, dirs:List[str]=None):
    """ Depending on the setup the location of config files might change. This helps with this, first hit wins!

    The following location are used by default: /etc/ehos/, /usr/local/etc/ehos, /usr/share/ehos/, configs/

    Args:
      filename: file to find
      dirs: additional list of directories to search through

    Return:
      Full path to the file (str)

    Raises:
      RuntimeError if file not found
    """

    script_dir = os.path.dirname(os.path.abspath( filename))

    default_dirs = ['/etc/ehos/',
                    '/usr/local/etc/ehos',
                    '/usr/share/ehos/',
                    '/usr/local/share/ehos/',
                    "{}/../configs".format( script_dir ),
                    'configs',
                    './']


    

    
    if dirs is not None:
        dirs += default_dirs
    else:
        dirs = default_dirs
        
    for dir in dirs:
        full_path = "{}/{}".format( dir, filename)
        if os.path.isfile(full_path):
            return full_path

    raise RuntimeError("File {} not found".format( filename ))

        


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
      RuntimeError if no pattern

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

    shutil.copy( filename, "{}.original".format( filename ))
    
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

    

        


def verbose_level(new_level:int):
    """ Set the verbosity level, value is forced with in the [1-5] range

    levels correspond to: DEBUG=5,  INFO=4 WARN=3, ERROR=2 and FATAL=1

    Args:
      level: when to report

    Returns:
      None

    Raises:
      None

    """
    if new_level < 1:
        new_level = 1
    elif new_level > 5:
        new_level = 5
        
    global level
    level = new_level
    

        
def verbose_print( message:str, report_level:int=1):
    """ If level is equal or above limit print message

    Args:
      message: what to print
      level: when to report

    Returns:
      None

    Raises:
      None

    """

    levels = {FATAL: 'FATAL',
              ERROR: 'ERROR',
              WARN:  'WARN',
              INFO:  'INFO',
              DEBUG: 'DEBUG' }

    
    if ( report_level <= level):
        print( "{}: {}".format(levels[report_level], message ))
        

def system_call(command:str):
    """ runs a system command

    Args:
      command to run

    Returns:
      None

    Raises:
      None
    
    """

    subprocess.call(shlex.split( command ), shell=False)
        
        
