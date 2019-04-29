import datetime
import random
import re
import shlex
import socket
import string
import subprocess
import time


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
