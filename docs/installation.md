## Manual configuratino and running EHOS daemon




### Installing EHOS on the deployment computer.

EHOS does not need to be installed system wide on the computer used
for deploying EHOS. The deployment computer however needs to have
python 3.4 (or later) installed if you want to benefit from the
deployment scripts.

The example below creates a virtual environment with EHOS in it on the
deployment computer.

```bash
# create a python 3.X virtual environment, download EHOS and install the EHOS requirements.
virtualenv -p python3 ehos
#create and activate your ehos python virtualenv
cd ehos

# for bash
source path-of-virtual-environment/bin/activate

# for (t)csh
source path-of-virtual-environment/bin/activate.csh

#download ehos. (requires wget)
wget https://github.com/elixir-no-nels/ehos-python/archive/v1.0.0.tar.gz
tar zxvf v1.0.0.tar.gz --strip 1

# install requirements:
pip install -r requirements.txt

# To deactivate virtualenv once done:
deactivate
```

If you want to install EHOS on the deployment system, EHOS needs to be
installed in /usr/local. Note EHOS is installed with pip3.

```bash
# Install latest stable ehos version & dependencies in /usr/local:
pip3 install --prefix /usr/local/ git+https://github.com/elixir-no-nels/ehos-python.git
```

The documentation below referring to the EHOS configuration files and
scripts assumes you have downloaded ehos into the virtualenv. If you
have installed EHOS in /usr/local the location of the configuration
files are not in share/ and etc/ but /usr/local/share/ehos and
/usr/local/etc/ehos respectively. Furthermore, the scripts should be
available system wide so ./bin/ehos_build_images.py should be
ehos_build_images.py instead.


### Configuration files:

There are two types of configuration files, one is to control the
behaviour of the ehos deployment script and daemon and the others for
installing and configuring the compute nodes. The files can be found
in share/ ( or /usr/loca/share/ehos). Upon alteration it is
recommended to place the altered file in etc ( or /usr/local/etc/ehos) to
distinguish them from the original template ones.

Most configuration files contains mark-up tags (looks like this:
{host_ip}). These are place holders that the EHOS system will add
system specific information into. Do not alter these unless you fully
understand the system.

#### EHOS daemon connection and behaviour configuration file

There is an example etc/ehos.yaml.example file provided. This will
needed to be renamed to etc/ehos.yaml and credentials for openstack
connection filled in, eg: username, password, vm-image etc. The
remainder of the file regards the behaviour of the ehos daemon, like
the max number of nodes to create etc, and htcondor specific
customisation. The template-file, with its comments, should be self
explanatory. In the HTCondor section it is important to change the
password to something unique as this restricts what nodes are allowed
to connect to the EHOS instance.


#### VM creation files

The configuration files for VM creation are all cloud-init files in
yaml format. These configuration files can either be used as is or as
templates for tweaking the system. Notice that all the files have been
created for centos 7 systems, so alterations might be required if your
system differs from this.


### Configure OpenStack 

EHOS uses OpenStack to provide the virtual machines (VM) used for the
compute environment. Most of the initial configuration of the
OpenStack service can be done either by using the OpenStack dashboard
or the OpenStack command line interface (CLI). The CLI is installed as
part of EHOS.  All CLI tasks, with the exception of uploading of the
ssh key (see below), can be achieved using the openstack
dashboard. However the detail of using the dashboard will will not be
covered in this document.

Documentation of how to configure the CLI can be found at:
http://docs.uh-iaas.no/en/latest/api.html.

If you plan to use multiple OpenStack regions/projects these steps
must be done for each region/project. All command line examples shown
assumes that you have successfully installed and configured 
OpenStack CLI

**Important note:** CLI reads and reacts to shell variables, so if you
have sourced your keystone file this might break the EHOS scripts in
odd ways.




#### Firewall rules

Depending on your setup you will need to open some ports to your
master and potential execution nodes. It is strongly recommended to
open port **22/ssh** so the admin user can connect and
troubleshoot/fix issues.

One on the underlying technologies of EHOS is HTCondor that
communicates on port 9618 (both TCP and UDP). If you are running on a
single openstack region/project you will need to allow communication
between nodes in the security group, if the master or the nodes are in
multiple regions/projects you will need to open up for both incoming
and outgoing traffic on the 9618 port, again both TCP and UDP.


```bash

# Create the security group for EHOS, for these examples the
# security group name is set to ehos, please change for your setup
openstack security group create ehos

# Open for ssh from any computer 
openstack security group rule create --protocol tcp --ingress --description 'ssh' --dst-port 22:22 --remote-ip 0.0.0.0/0 ehos

# Open for HTCondor specific communication
# open for HTCondor within the security group
openstack security group rule create --protocol tcp --ingress --description 'htcondor' --dst-port 9618:9618  --remote-group ehos ehos
openstack security group rule create --protocol udp --ingress --description 'htcondor' --dst-port 9618:9618 --remote-group ehos  ehos

# globally:
openstack security group rule create --protocol tcp --ingress --description 'htcondor' --dst-port 9618:9618 --remote-ip 0.0.0.0/0 ehos
openstack security group rule create --protocol udp --ingress --description 'htcondor' --dst-port 9618:9618 --remote-ip 0.0.0.0/0 ehos

```

#### SSH key


If you want to be able to connect to the master and/or nodes through
SSH you will need to upload the public key to the openstack instance
using the CLI.

**Important note**

OpenStack (at least the uh-cloud instance) has an issue where ssh key
pair added using the dashboard is not visible for the PI/CLI. If you
want to be able to connect to the nodes the key using the CLI. See:
http://docs.uh-iaas.no/en/latest/known-issues.html#api-access

```bash
# Upload your default ssh id-rsa public key to openstack
openstack keypair create --public-key ~/.ssh/id_rsa.pub [KEYNAME]
```

## Creating the ehos image(s)

In order to speed up the creation of new nodes and also ensure a
uniform environment across all compute nodes EHOS is utilising VM
images, one in each region/project. The EHOS installation contains a
image cloud-init sample configuration file: share/base.yaml for a
centos 7 system. This is a good start for creating the EHOS
image. Please note that this script installs some crucial pieces of
software that is required for EHOS to work, so don't delete entries
from it, but feel free to add aditional software if needed.

The creation of image(s) can either be done manually using either the
OpenStack CLI or dashboard, or through an EHOS script that is provided
with the EHOS installation. This script will create the images in each
region/project specified in your ehos.yaml for you, and update the
ehos.yaml file with the id for the created image(s).


### Automatic creation of the images

This automates the process of creating the image(s) on all
region(s)/project(s) specified in your ehos.yaml file, this script
will also create a EHOS wide password if not already set.

```bash
# Create base VMs and update the ehos.yaml file with the ids
# The more -v you add the more loggin will you get.
# -B base.yaml specify what base.yaml file to use, otherwise it find one.
ehos_build_images.py -v -v -v etc/ehos.yaml
```

### Manual creation of the image(s)

One thing to be aware of iis that the initial run of the cloud-init
script takes a few minutes to complete, so be sure that the VM is
fully up and running before progressing to creating the
backup/image. Please notice that it is important to spin down the VM
prior to making the image, as the VM might otherwise get corrupted.


The CLI commands for creating an image  are:

```bash
# Create base VM
openstack server create --flavor <FLAVOR> --image <IMAGE> --nic net-id=<NETID> --security-group <SECURITYGROUP> --key-name <KEYNAME> --user-data /usr/local/share/ehos/base.yaml   <VM_NAME>

# Notice the vm ID as this is needed later ( it is uuid string)

#Check the status of the booting of the VM, will normally take 1-2 minuttes: 
openstack console log show <VM_ID>

# Make sure the VM is fully up and running before this step (you should see a login prompt on the step above) :
openstack server stop <VM_ID>

# Make the VM into an image for us to use later:
openstack backup create --name <IMAGE_NAME> <VM_NAME>
```

The id of the image created need to be added to the corresponding cloud
entry in the ehos.yaml file.



## Create the master node & run the EHOS daemon

**Important:** note that these install instructions differ from the
ones for the deployment computer!


### Automatic master creation, installation and configuration

If you are using an OpenStack VM to act as the EHOS master it is
recommended that you use the provided bin/ehosd_deployment.py script to
create and configure the master node. 

It is important that you have moved any modified config files into the
etc directory as these will then automatically be copied across to the
master node, along with the ehos.yaml file.

This script will install EHOS on the masternode and run the ehos-daemon
(ehosd) as a service under systemd, and all ehosd logs can be seen with
the journalctl command.


```bash
# create VM, install software, start EHOS
./bin/ehosd_deploy.py -v -v -v ehos.yaml

```

### Manual instructions

#### Semi-automatic installation:

The master node is normally run within the openstack environment. If
this is the case the easiest way to deploy the master node is to use
the image created above and use the provided master.yaml file when
creating the master. This can be either be done through the openstack
dashboard, or on the command line. If using the command line execute
the following


```bash
# Create master VM (assumes virtualenv installations of EHOS)
openstack server create --flavor <FLAVOR> --image <IMAGE_ID> --nic net-id=<NETID> --security-group <SECURITYGROUP> --key-name <KEYNAME> --user-data share/ehos/master.yaml <VM_MASTER_NAME>

```

### Starting the daemon

A few steps is remaining before the system is up and running, you will
need to edit the ehos.yaml file with your openstack credentials and
tweak the expected behaviour of the system. Eg: the max number of
nodes running etc.


```bash
#make a copy of the ehos config file and edit it with your
# openstack keystone credentials and ehosd setting

cp /usr/loca/share/ehos/ehos.yaml.example /usr/loca/etc/ehos/ehos.yaml
vim /usr/local/etc/ehos/ehos.yaml

# to run the server manually
# Start up the ehos sever, adding some -v will increase the logging amount:
/usr/local/bin/ehosd.py -v -v -v /usr/local/etc/ehos/ehos.yaml

To run is as a systemd service:

# or run it as as systemd service
systemctl enable ehos.service
systemctl start ehos.service

```
## Testing the installation

The EHOS package installs a script that is suitable for testing the
EHOS installation. The script submits a set of jobs to the HTCondor
queue that executes a sleep command on the execution nodes. Running
the command without any parameters and you will get the full list of
possible modifications as number of jobs, sleep intervals etc.

Note that this should be run on the master node

```bash
# Submit 10 jobs, sleeping randomly between 30 and 50 seconds 
ehos_sleep_jobs.py -n 10 -r 30,50

# Submit 10 jobs, each sleeping for 20 seconds
ehos_sleep_jobs.py -n 10 -s 20
```
