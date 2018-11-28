groupadd docker
groupadd ehos

useradd -g ehos -M -r ehos

## for Extra Packages for Enterprise Linux packages (stupid centos)
yum install -y epel-release 

yum -y groupinstall "development tools"
## some editors and tools we need
yum install -y vim  nano wget lvm2 squashfs-tools python34 python34-pip python-pip autofs
yum install -y  python-devel libarchive-devel yum-utils device-mapper-persistent-data 

# docker install 

# yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
# yum install -y docker-ce

## Enable condor to run docker
# usermod -aG docker condor

## Enable rootless use of docker
# usermod -aG docker centos

## htcondor install

wget -P /etc/yum.repos.d https://research.cs.wisc.edu/htcondor/yum/repo.d/htcondor-stable-rhel7.repo

wget -P /tmp/ http://research.cs.wisc.edu/htcondor/yum/RPM-GPG-KEY-HTCondor
rpm --import /tmp/RPM-GPG-KEY-HTCondor
yum -y install condor.x86_64

pip install openstacksdk
pip install python-openstackclient
pip3 install --prefix /usr/local/ git+https://github.com/elixir-no-nels/ehos-python.git


/bin/cat << EOM > /etc/condor/00personal_condor.config
CONDOR_HOST = {master_ip}

##  This macro determines what daemons the condor_master will start and keep its watchful eyes on.
##  The list is a comma or space separated list of subsystem names

DAEMON_LIST = COLLECTOR, MASTER, NEGOTIATOR, SCHEDD

FLOCK_TO = $(CONDOR_HOST)
ALLOW_NEGOTIATOR = $(FLOCK_TO)
# ALLOW_WRITE = {ip_range}
ALLOW_WRITE  = *
ALLOW_READ = $(ALLOW_WRITE)
UID_DOMAIN = {uid_domain}
STARTER_ALLOW_RUNAS_OWNER = TRUE
TRUST_UID_DOMAIN=TRUE
SOFT_UID_DOMAIN = TRUE



SEC_PASSWORD_FILE = $(LOCK)/pool_password
SEC_DEFAULT_AUTHENTICATION = REQUIRED
SEC_DEFAULT_AUTHENTICATION_METHODS = PASSWORD
#SEC_DAEMON_AUTHENTICATION = REQUIRED
#SEC_DAEMON_INTEGRITY = REQUIRED
#SEC_DAEMON_AUTHENTICATION_METHODS = PASSWORD

#SEC_NEGOTIATOR_AUTHENTICATION = REQUIRED
#SEC_NEGOTIATOR_INTEGRITY = REQUIRED
#SEC_NEGOTIATOR_AUTHENTICATION_METHODS = PASSWORD
#SEC_CLIENT_AUTHENTICATION = REQUIRED
SEC_CLIENT_AUTHENTICATION_METHODS = FS, PASSWORD, KERBEROS, GSI
# ALLOW_DAEMON = condor_pool@$(UID_DOMAIN),   condor@$(UID_DOMAIN)/$(IP_ADDRESS)

NEGOTIATOR_INTERVAL = 5

EOM

chown root.root /etc/condor/00personal_condor.config
chmod 644       /etc/condor/00personal_condor.config

# startup services

## Start autofs and enable automatic start at boot
#  - service autofs start
#  - systemctl enable autofs

  ## Start docker and enable automatic start at boot
#  - service docker start
#  - systemctl enable docker

# Start condor and enable it on start
service condor start
systemctl enable condor
  


