## Installation:

It is recommended to install EHOS using pip3 to ensure installing the
most recent and stable version. If wanting to test the development
versions downloading/clone EHOS directly from the github repo
(https://github.com/elixir-no-nels/ehos-python.git)


When installing with pip the package either must be installed in in
/usr/local as ehos expects configuration files in ehos-specific sub
directories default. Together with the ehos specific libraries and
scripts a set of example configuration files will be installed in
share/ehos/. When the program run it looks for the configuration files
if not provided by the user (see [usage](usage.md)).  Installing in
/usr/local is imperative if you want to run ehosd as a systemd
service.



```bash
# 

# Connect to the server according to the documentation.
# Install latest stable ehos version in /usr/local (recommended):
pip3 install --prefix /usr/local/ git+https://github.com/elixir-no-nels/ehos-python.git

#To install a specific branch of ehost this can be added at the end of the URL, eg version 1.0.0:
pip3 install --prefix /usr/local/ git+https://github.com/elixir-no-nels/ehos-python.git@v1.0.0


```

