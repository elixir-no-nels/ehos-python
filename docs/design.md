## Design notes

The ehos package consists of two main programs: ehos_deployment.pu
that helps with the deployment of ehos and ehosd the master daemon
responsible for running the main ehos. Please the [usage](usage.md)
page on how to use these programs. The package otherwise contains a
library that is described below. For the full detail please look at
the full documentation.

### The ehos library

The overall structure of the ehos code is outlined in figure XX with
the two scripts at the top, mainly interacting with the higher level
ehos librays. This library provide a set of simple functions (eg
timestamp) and add some logic onto functions found in the lower level
sub-modules.

When passing config information onto the vm/openstack functions this
is done by using kwargs. This limits the readability of the code, but
ensure that going forward it is possible to use different information
to connect to different VM backends.


### ehos.instances

This library provides the tracking of execution nodes and their state
(os/vm level) and status (condor level). Eg a node can be state active
and have status idle, meaning that is running but not executing any
htcondor jobs. The library gives the option to add clouds and nodes
associated with clouds and provide some basic logic to ensure nodes
are not added multiple times or nodes are added to unknown clouds.

*future plans*: to act as a cache for the same data stored in a
database. This would give the option for calculating statistics later
on and ensuring no nodes are left hanging if restarting the ehos daemon.


### ehos.htcondor

A few simple wrapper functions making it possible to interact with the
htcondor master for the project. The main responsibility of this
module is to provide the status of current jobs and the state of
nodes.



### ehos.vm

This is a template class describing the interfaces required for the VM backends. 

*future plans*: add support of VmWare and AWS.

### ehos.openstack

The openstack interface class. Each instance of the class contains the
connector to the instance of the openstack cloud as ehos can now be
connected and use multiple openstack instances at the same time. 


### config and files


If the repository is downloaded the config files
will be in the configs directory instead. The order of directories to
be searched by the scripts are: /etc/ehos/, /usr/local/etc/ehos,
/usr/share/ehos/, /usr/local/share/ehos/ and configs/. As ehos can be
run as a systemctl service the scripts are installed in /usr/local/bin
so they can be referred to correctly


