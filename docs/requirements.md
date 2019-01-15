## Requirements:


EHOS is implemented in python and is reliant on HTcondor as the
scheduler. CentosOS 7 is the OS used on all virtual servers for this
implementation and testing, but it should work as well if HTCondor is
supported. The provided config files are all specific to CentOS 7 but
should be easy to tweak for an alternative Linux OS.


HTCondor version 8.6.13 was used for the development of the system.




These python libraries will be installed automatically if the ehos package is installed using pip.


** Python libraries:**
* openstacksdk (v.0.17.2)
* htcondor (v.8.7.9)
* typing (v.3.6.6)
* munch (v.2.3.2)
* python-openstackclient (v3.16.1), not used directly but nice to have

