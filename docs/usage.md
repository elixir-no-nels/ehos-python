## Usage:

Install ehos according to the [installation](installation.md) page.


### openstack configurations


Before EHOS can run on your openstack of choice you will need
configure some basic setting. If you plan to use multiple openstack
connections this must be done on each of the locations. Also all
command line examples shown here assumes that you have successfully
configured, and sourced, the openstack keystone file.


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



#### SSH key

If you want to be able to connect to the server through SSH you will
need to upload the public key to the openstack instance. 

If you just want to be able to connect to the master node, the key can
be added through the openstack dashboard. 

**Important note**

Openstack (at least the uh-cloud instance) has an issue where ssh key
pair added using the dashboard is not visible for the API/CLI. If you
want to be able to connect to the nodes the key using the CLI. See:
http://docs.uh-iaas.no/en/latest/known-issues.html#api-access


```bash
# Upload ssh the id-rsa publich key to openstack with the name mykey

openstack keypair create --public-key ~/.ssh/id_rsa.pub [KEYNAME]
```


### Configuration files:

There are two types of configuration files, one is to control the
behaviour of the ehos deployment script and daemon and the others for
installing and configuring the compute nodes.


#### EHOS behaviour configuration file

There is an example ehos.yaml.example file provided. You will need to
fill in is the cloud details, eg: username, password, image to use
for a cloud, etc. The remainder of the file regards the behaviour of
the ehos daemon, like the max number of nodes to create etc. The
template-file, with its comments, should be self explanatory.


#### VM creation configuration files


The configuration files are all cloud-init files in yaml format, with
some additional markup for parts handled by the deployment script. A
markup tag looks like this: {host_ip}, please do not alter these
unless you fully understand the system. These configuration files can
either be used as is or as templates for tweaking the system. Upon
alteration it is recommended to place the altered file in
/usr/local/etc/ehos to distinguish them from the template ones in
/usr/local/share/ehos.



## Creating the ehos image(s)


In order to speed up the creation of new nodes and also ensure a
uniform environment across all compute nodes EHOS is utilising vm
images, one in each region/project. The image can either be created in
two ways, Manual: Create a suitable vm instance and install and
configure the required software. Automatically: Create a VM and give
it a cloud-init file that installs and configure the system. Both
methods have their advantages: Manual is good for troubleshooting and
development, automatically using a cloud-init file. The latter ensures
that the image creation process is not only reproducible, but also
documented.

If creating the image using the cloud-init scripts a script is
provided that will create the images for you.

```bash
# Create base VM
ehos_build_images.py -B /usr/local/share/ehos/base.yaml /usr/local/etc/ehos/ehos.yaml

```


Ehos installs a base image sample configuration file in
/usr/local/share/ehos/base.yaml for a centos system that is a good
start for a system. Be aware that the initial run of the cloud-init
script takes a few minutes so be sure that the VM is fully up and
running before progressing to creating the backup/image. Please notice
that it is important to spin down the VM prior to making the image, as
the VM might otherwise get corrupted.



The CLI commands for achieving this are:

```bash
# Create base VM
openstack server create --flavor <FLAVOR> --image <IMAGE> --nic net-id=<NETID> --security-group <SECURITYGROUP> --key-name <KEYNAME> --user-data configs/base.yaml   <VM_NAME>

# This is the time and tweak and install additional software if required.

# Make sure the VM is fully up and running before this step:
openstack server stop <VM_ID>

# Make the VM into an image for us to use later:
openstack backup create --name <IMAGE_NAME> <VM_NAME>
```




## Create the master node

The master node is normally run within the openstack environment. If
this is the case the easiest way to deploy the master node is to use
the provided master.yaml file when creating the master. This can be
either done through the openstack dashboard, or on the command
line. If using the commandline execute the following


```bash
# This assumes that the keystone setting are already set.

# Create base VM
openstack server create --flavor <FLAVOR> --image <IMAGE> --nic net-id=<NETID> --security-group <SECURITYGROUP> --key-name <KEYNAME> --user-data configs/base.yaml   <VM_NAME>

# This is the time and tweak and install additional software if required.

# Make sure the VM is fully up and running before this step:
openstack server stop <VM_ID>

# Make the VM into an image for us to use later:
openstack backup create --name <IMAGE_NAME> <VM_NAME>
```






Setting up the master node

Firstly create a new VM instance from the base image you can use the
provided master.yaml file to ensure everything is setup and configured
correctly.


```bash
# Create master VM
openstack server create --flavor <FLAVOR> --image <IMAGE_NAME> --nic net-id=<NETID> --security-group <SECURITYGROUP> --key-name <KEYNAME> --user-data configs/base.yaml   <VM_NAME>

# Make sure the VM is fully up and running before this step:

# Connect to the server according to the documentation.
# Install ehos in /usr/local (recommended):
pip3 install --prefix /usr/local/ git+https://github.com/elixir-no-nels/ehos-python.git


#To install a specific branch of ehost this can be added at the end of the URL:
pip3 install --prefix /usr/local/ git+https://github.com/elixir-no-nels/ehos-python.git@v1.0.0


#make a copy of the config file and edit it with your openstack keystone credientials
cp /usr/loca/share/ehos/ehos.yaml.example /usr/loca/etc/ehos/ehos.yaml
vim /usr/loca/etc/ehos/ehos.yaml

# Start up the ehos sever, adding some -v will increase the logging amount:
/usr/local/bin/ehosd.py /usr/local/etc/ehos/ehos.yaml

# or run it as as systemd service
systemctl enable ehos.service
systemctl start ehos.service

```






### The deployment script

The whole building of a base image and deployment of a master node can
be achieved by using the provided deploy_ehos.py (should this be
changed to ehos_deployment.py?)


```bash
# clone or download ehos, there is no reason to install it as a pip package:

git clone https://github.com/elixir-no-nels/ehos-python.git
cd ehos-python

# install packages it relies on:
pip3 install openstacksdk python-openstackclient

#make a copy of the config file and edit it with your openstack keystone credientials
cp ehos.yaml.example ehos.yaml
vim /usr/loca/etc/ehos/ehos.yaml

# make the base image and start the master ehos server:

./bin/deploy_ehos.py ehos.yaml 

#there are additional flags if you want to use a manually made image etc.
```

