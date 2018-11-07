# EHOS
**E**lastic **H**TCondor **O**penStack **S**caling - Pronounced EOS

## Goal:

EHOS is in a nutshell an HPC where the number of compute nodes scales
according to a workload.  This ensures that resources are not wasted when during computational lulls.


EHOS is implemented in python 3, uses HTCondor for job scheduling, and
using openstack for the virtual compute generation. It is possible to
spread the workload across multiple openstack
project/regions/solutions to ensure full scalability. The long time goal is
it to support additional virtulisation backends including AWS and
VmWare.


This system was implemented on CentOS 7, using the openstack
implementation at: uh-iaas.no, it is recommended to look at their
documentation regarding basic openstack operations and usage as it
will not be covered by this document (http://docs.uh-iaas.no/en/latest/).

## Sections:

* [Installation](installation.md)
* [Requirements](requirements.md)
* [Usage](usage.md)
* [Design notes](design.md)

