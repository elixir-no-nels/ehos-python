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


Ehos installs a base image cloud-init sample configuration file in
/usr/local/share/ehos/base.yaml for a centos system that is a good
start for creating a ehos base image. Be aware that the initial run of
the cloud-init script takes a few minutes to run, so be sure that the VM is
fully up and running before progressing to creating the
backup/image. Please notice that it is important to spin down the VM
prior to making the image, as the VM might otherwise get corrupted.



The CLI commands for achieving this are:

```bash
# Create base VM
openstack server create --flavor <FLAVOR> --image <IMAGE> --nic net-id=<NETID> --security-group <SECURITYGROUP> --key-name <KEYNAME> --user-data /usr/local/share/ehos/base.yaml   <VM_NAME>

# This is the time to tweak and install additional software if required.

# Make sure the VM is fully up and running before this step:
openstack server stop <VM_ID>

# Make the VM into an image for us to use later:
openstack backup create --name <IMAGE_NAME> <VM_NAME>
```




## Create the master computer & run EHOS

The master node is normally run within the openstack environment. If
this is the case the easiest way to deploy the master node is to use
the image created above and use the provided master.yaml file when
creating the master. This can be either done through the openstack
dashboard, or on the command line. If using the commandline execute
the following


```bash
# Create base VM
openstack server create --flavor <FLAVOR> --image <IMAGE_NAME> --nic net-id=<NETID> --security-group <SECURITYGROUP> --key-name <KEYNAME> --user-data /usr/local/share/ehos/master.yaml <VM_MASTER_NAME>

```

As the master can be run of any computer. If wanting to install the
master node yourself, you can use the /usr/local/share/ehos/master.sh to install the basic
systems. Please notice this file is created for a centos system.

A few steps is remaining before the system is up and running, you will
need to edit the ehos.yaml file with your openstack information and
tweak the expected behaviour of the system. Eg: the max number of
nodes running etc.

And then you can either run it on the command line or through systemd


```bash
# Create master VM
#make a copy of the config file and edit it with your openstack keystone credientials
cp /usr/loca/share/ehos/ehos.yaml.example /usr/loca/etc/ehos/ehos.yaml
vim /usr/loca/etc/ehos/ehos.yaml

# to run the server manually
# Start up the ehos sever, adding some -v will increase the logging amount:
/usr/local/bin/ehosd.py /usr/local/etc/ehos/ehos.yaml

To run is as a systemd service:

# or run it as as systemd service
systemctl enable ehos.service
systemctl start ehos.service

```


