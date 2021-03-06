# EHOS
**E**lastic **H**TCondor **O**penStack **S**caling - Pronounced EOS

EHOS is a cloud based HPC where the number of compute nodes that
scales according to a workload.  This ensures that resources are not
wasted when during computational lulls.

EHOS is implemented in python 3, uses HTCondor for job scheduling, and
openstack for the virtual compute generation. The long time goal is to
support additional virtulisation backends including AWS and VmWare.

This implementation used CentOS 7 for the virtual computes, using the
openstack implementation at: uh-iaas.no, it is recommended to look at
their documentation regarding basic openstack operations and usage as
it will not be covered by this document (http://docs.uh-iaas.no/en/latest/).

Read the [quick start ](docs/quick_start.md) to try ehos, or dive into
the [full documentation](docs/index.md) for more details regarding
architecture, installation, and running the system in a production
environment. There is now an ansible-playbook available as well: 
[ansible-role-ehos](https://github.com/elixir-no-nels/ansible-role-ehos.git)
