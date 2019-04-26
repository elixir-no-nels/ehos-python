#!/usr/bin/python3
""" 

Abstract class for the VM interface 
 
 
 Kim Brugger (22 Oct 2018), contact: kim@brugger.dk
"""

import sys
import pprint

pp = pprint.PrettyPrinter(indent=4)

import ehos

from enum import IntEnum


class State(IntEnum):
    vm_booting = 1
    vm_active = 2
    vm_suspended = 3
    vm_restarting = 4
    vm_stopping = 5
    vm_deleted = 6
    vm_unknown = 7


class Vm(object):
    _connection = None
    _name = None
    _servers = {}
    _backend = "Vm"

    def __init__(self):
        """ default init function, set class variables to ensure they are not shared betwewen class objects
        
        Args:
          None

        Returns: 
          None
        
        Raises:
          None
        """

        self._connection = None
        self._name = None
        self._servers = {}
        self._backend = "Vm"

    def check_connection(self) -> bool:
        """ Checks that there is a connection to the vm
        
        Args:
          None
        
        Returns:
          bool
        
        Raises:
          ConnectionError if not connected
        """

        return False

    def connect(self, cloud_name: str, **kwargs) -> None:
        """ Connects to a vm service

        Args:
          cloud_name: name of the cloud this information relates to
    
        Returns:
          None
    
        Raises:
          None
        """

        return None

    def server_create(self, name: str, *kwargs) -> str:
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

        return ""

    def server_stop(self, id: str, timeout: int = 200) -> None:
        """ stops a server

        Args:
          id: the name of the server
          timeout: max time (s) to wait for the server to shotdown

        Returns:
          None

        Raises:
          TimeoutError: if the server is not in shutdown status within the timeout time
        """

        return None

    def server_delete(self, id: str) -> None:
        """ Deletes a server instance

        Args:
          id: name/id of a server

        Returns:
          None

        Raises:
          None

        """

        return None

    def server_list(self) -> {}:
        """ gets a list of servers on the vm

        Args:
          None

        Returns:
          server dict ( name -> id )

        Raises:
          None
        """

        return {}

    def server_log(self, id: str) -> str:
        """ streams the dmesg? log from a server

        Args:
          id: id/name of server

        Returns:
          the log (str)

        Raises:
          None
        """

        return ""

    def server_log_search(self, id: str, match: str) -> str:
        """ get a server log and searches for a match

        Args:
          id: id/name of the server
          match: regex/str of log entry to look for

        Returns:
          matches found in log, if none found returns an empty list

        Raises:
          None

        """

        return ""

    def wait_for_log_entry(self, id: str, match: str, timeout: int = 200) -> str:
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

        return ""

    def server_ip(self, id: str, ipv: int = 4) -> str:
        """ returns the ip address of a server

        Args:
        id: name/id of server
        ipv: return IP4 or IP6 address. IPV4 is default

        Returns:
          IP address (str), if not found (wrong IPV) returns None

        Raises:
          None
        """

        return ""

    def make_image(self, id: str, image_name: str, timeout: int = 200):
        """ creates an image from a vm server.

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

        return None

    def _wait_for_image_creation(self, image_name: str, timeout: int = 200) -> str:
        """ Wait for a single image with the given name exists and them return the id of it

        Args:
          image_name: name of the image
          timeout: how long to wait for the image to be created.

        Returns:
          image id (str)
        
        Raises:
          None
        """

        return ""
