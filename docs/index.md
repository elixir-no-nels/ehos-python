EHOS design and usage document.

EHOS: Elastic HTCondor OpenStack Scaling
Introduction:

EHOS addresses the problem of dynamically scaling the number of openStack compute nodes based on workload.  This ensures that we don’t waste compute resources, and thus money when compute is not needed.

EHOS is implemented in python 3 and are running on a openstack platform. The ehos daemon script interacts with the HTcondor master and scales the compute resources available based on the requirements. 


This system is build on the openstack implementation at: uh-iaas.no, it is recommended to look at their documentation regarding basic openstack operations and usage as it will not be covered by this document ( http://docs.uh-iaas.no/en/latest/).

Requirements:
Python3 (preferrable >= 3.6)
Python libraries:
hpenstacksdk (v.0.17.2)
htcondor (v.8.7.9)
typing (v.3.6.6)
munch (v.2.3.2)
python-openstackclient (v3.16.1), not used directly but nice to have


Usage:

Important notes

Some openstack installations have an issue where ssh key pair added using the dashboard is not visible for the API/CLI. If this is the case add the key using the CLI. See: http://docs.uh-iaas.no/en/latest/known-issues.html#api-access

When setting up the openstack network it is important to allow communication between nodes within a region. This is done by make a firewall rule with an Ingress of all TCP traffic allowed with the remote “host” being the security group.

Installation:

EHOS can either be installed by cloning (or downloading and uncompressing) the package from github or install with pip (pip3 install git+https://github.com/elixir-no-nels/ehos-python.git)


If installing with pip it is recommended to install the package either in / or /usr/local as the system expect configuration files there by default. Along with a library and scripts a set of example configuration files will be installed in share/ehos/. When the programs run they look for configuration files if not provided by the use (see below). If the repository is downloaded the config files will be in the configs directory instead. The order of directories to be searched by the scripts are: /etc/ehos/, /usr/local/etc/ehos, /usr/share/ehos/, /usr/local/share/ehos/ and configs/. As ehos can be run as a systemctl service the scripts are installed in /usr/local/bin so they can be referred to correctly


Configuration files:

The configuration files are all cloud-init files in yaml format, with some additional markup for parts handled by the deployment script. A markup tag looks like this: {host_ip}, please do not alter these unless you fully understand the system. These configuration files can either be used as is or as templates for tweaking the system. Upon alteration is recommended to place the altered file in etc/ehos to distinguish them from the template ones. 
Deploying ehos:

Before getting EHOS up and running some prerequisites needs be be sorted (see figure XX). This can either be done manually (good for development) or by using the provided ehos_deployment.py script, as described below.
Manuel deployment of EHOS:
Creating the base image

In order to speed up the creation of new nodes and also ensure a uniform environment across all compute nodes EHOS is utilising a vm image. The image can either be created in two ways,  Manual: Creating a suitable vm instance and install and configure the required software. Automatically: Create a VM and give it a cloud-init file that installs and configure the system. Both methods have their advantages: Manual is good for troubleshooting and development and then implement this as a cloud-init instance once you have the setup dialed. Furthermore the cloud-init ensures both that the image creation process is easy replicated but also documented.
Ehos provide a base image sample configuration file in configs/base.yaml. Be aware that the initial run of the cloud-init script takes a few minutes so be sure that the VM is fully up and running before progressing to the next step.


Once the VM has been created, an image/snapshot needs to made of it. It is important to spin down the VM prior to making the image, as the VM might otherwise get corrupted. 

The CLI commands for achieving this are:

# Create base VM
openstack server create --flavor <FLAVOR> --image <IMAGE> --nic net-id=<NETID> --security-group <SECURITYGROUP> --key-name <KEYNAME> --user-data configs/base.yaml   <VM_NAME>

# This is the time and tweak and install additional software if required.

# Make sure the VM is fully up and running before this step:
openstack server stop <VM_ID>

# Make the VM into an image for us to use later:
openstack backup create --name <IMAGE_NAME> <VM_NAME>


Setting up the master node

Firstly create a new VM instance from the base image you can use the provided master.yaml file to ensure everything is setup and configured correctly. 



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







The deployment script

The whole building of a base image and deployment of a master node can be achieved by using the provided deploy_ehos.py (should this be changed to ehos_deployment.py?)


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





Frontend
A simple frontend have been implemented using the flask framework, this runs as default on port 5000, remember to open the port on openstack if you want to use this.


# set the python lib paths:
export PYTHONPATH=/usr/local/lib64/python3.4/site-packages/:/usr/local/lib/python3.4/site-package

# download ehos as described above, as the frontend is not installed when using pip

cd ehos-python/front_end

#Name of the app:
export setenv FLASK_APP=ehos_frontend.py

flask run --host=158.37.63.101





Design notes:



