# EHOS
**E**lastic **H**TCondor **O**penStack **S**caling - Pronounced EOS

EHOS addresses the problem of dynamically scaling the number of
openStack compute nodes based on a scheduler workload.  This ensures
that we don’t waste compute resources, and thus money when compute is
not needed.

EHOS is implemented in python 3, uses HTCondor for job scheduling, and
are running on the openstack platform. The long time goal is it to
support additional virtulisation backends.


This system was implemented on CentOS 7, using the openstack implementation at: uh-iaas.no, it is recommended to look at their documentation regarding basic openstack operations and usage as it will not be covered by this document ( http://docs.uh-iaas.no/en/latest/).

**Requirements:**
* Python3 (preferrable >= 3.4)
* Python libraries:
* openstacksdk (v.0.17.2)
* htcondor (v.8.7.9)
* typing (v.3.6.6)
* munch (v.2.3.2)
* python-openstackclient (v3.16.1), not used directly but nice to have

Please read the [full documentation](docs/index.md) for more details