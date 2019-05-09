import datetime
import os
import random
import re
import shlex
import shutil
import socket
import string
import subprocess
import time
from typing import List, Tuple

from munch import Munch

from ehos import log_utils as logger


def get_host_ip() -> str:
    """ gets the host ip address

    Args:
      None

    returns:
      Host Ip 4 address

    Raises:
      None
    """


    return socket.gethostbyname(socket.getfqdn())


def get_host_name() -> str:
    """ gets the host name

    Args:
      None

    Returns:
      full host name

    Raises:
      None
    """
    return socket.getfqdn()


def timestamp() -> int:
    """ gets a sec since 1.1.1970

    "Args:
      None

    Returns:
      Secs since the epoc

    Raises:
      None
    """

    return int(time.time())


def datetimestamp() -> str:
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


def make_node_name(prefix="ehos", name='node') -> str:
    """ makes a nodename with a timestamp in it, eg: prefix-name-datetime

    Furthermore, ensures the name will correspond to a hostname, eg making _ to -, and lowercase letters

    Args:
      prefix: prefix for name
      name: type of node, eg executer

    Returns:
      name generated

    Raises:
      None
    """

    node_name = "{}-{}-{}".format(prefix, name, datetimestamp())
    node_name = re.sub("_","-",node_name)
    node_name = node_name.lower()

    return node_name


def system_call(command:str) -> int:
    """ runs a system command

    Args:
      command to run

    Returns:
      None

    Raises:
      None

    """

    return(subprocess.call(shlex.split( command ), shell=False))


def get_node_id(filename:str='/var/lib/cloud/data/instance-id') -> str:
    """ Cloud init stores the node id on disk so it possible to use this for us to get host information that way

    Ideally this would have been done using the cloud_init library, but that is python2 only, so this is a bit of a hack

    Args:
      filename: should only be changed when testing the function

    Returns:
      node id (string)

    Raises:
      if the instance not found raise a RuntimeError
    """


    if ( not os.path.isfile( filename )):
      raise RuntimeError("instance file ({}) does not exists".format( filename))


    fh = open(filename, 'r')
    id  = fh.readline().rstrip("\n")
    fh.close()

    return id


def readin_config_file(config_file:str) -> Munch:
    """ reads in and checks the config file

    Args:
      config_file: yaml formatted config files

    Returns:
      config ( munch )

    Raises:
      None
    """

    with open(config_file, 'r') as stream:
        config = Munch.fromYAML(stream)
        stream.close()

    #print( config_file )

    if 'daemon' not in config:
        config[ 'daemon' ] = {}
    if 'hostname' not in config.daemon:
        config.daemon['hostname'] = get_host_name()

    return config



def readin_whole_file(filename:str) -> str:
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


def find_config_file( filename:str, dirs:list=None) -> str:
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
                    "{}/../etc".format( script_dir ),
                    'etc/',
                    'etc/ehos',
                    '/usr/share/ehos/',
                    '/usr/local/share/ehos/',
                    "{}/../share".format( script_dir ),
                    'share/',
                    'share/ehos',
                    './']


    if dirs is not None:
        dirs += default_dirs
    else:
#        print( "No additional dirs!")
        dirs = default_dirs

    for dir in dirs:
        full_path = "{}/{}".format( dir, filename)
        if os.path.isfile(full_path):
            return os.path.normpath(full_path)

    raise RuntimeError("File {} not found".format( filename ))


def patch_file(filename:str, pattern:str=None, replace:str=None, patterns:List[ Tuple[str, str]]=None, outfile:str=None):
    """ Alter a file by searching for a pattern (str or regex) and replace it

    The function further more make a backup copy of the original file

    Args:
      filename: The file to change
      pattern: the pattern (str/regex) to search for in the file
      replace: what to replace the pattern with
      patterns: a list of replacements to be done
      outfile: alternative file to write to, will not create a backup of the original file

    Returns:
      None

    Raises:
      RuntimeError if no pattern

    """

    # this is foobared but I cannot find the strength to do this right
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

    if ( outfile is None ):
        shutil.copy( filename, "{}.original".format( filename ))

    # open and read in the while file as a single string
    with open( filename, 'r') as fh:
        lines = "".join(fh.readlines())
        fh.close()

    if patterns is None:
        patterns = [ (pattern, replace) ]

    for pattern, replace in patterns:
#        print( pattern, " ---> ", replace )
        # replace the pattern with the replacement string
        lines = re.sub(pattern, replace, lines)

    if ( outfile is None ):
        with  open(filename, 'w') as fh:
            fh.write( lines )
            fh.close()
    else:
        with  open(outfile, 'w') as fh:
            fh.write( lines )
            fh.close()


def make_uid_domain_name(length:int=3):
    """ Makes a 'random' uid domain name

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
