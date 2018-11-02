## Installation:

EHOS can either be installed by cloning (or downloading and uncompressing) the package from github or install with pip (pip3 install git+https://github.com/elixir-no-nels/ehos-python.git)


If installing with pip it is recommended to install the package either
in /usr/local as the setup expect configuration files there by default
and especially if you want to run ehosd as a systemd entry this is
required.

Along with a library and scripts a set of example configuration files
will be installed in share/ehos/. When the programs run they look for
configuration files if not provided by the use (see [usage](usage.md)). If the
repository is downloaded the config files will be in the configs
directory instead. The order of directories to be searched by the
scripts are: /etc/ehos/, /usr/local/etc/ehos, /usr/share/ehos/,
/usr/local/share/ehos/ and configs/. As ehos can be run as a systemctl
service the scripts are installed in /usr/local/bin so they can be
referred to correctly


```bash
# 

# Connect to the server according to the documentation.
# Install ehos in /usr/local (recommended):
pip3 install --prefix /usr/local/ git+https://github.com/elixir-no-nels/ehos-python.git


#To install a specific branch of ehost this can be added at the end of the URL, eg version 1.0.0:
pip3 install --prefix /usr/local/ git+https://github.com/elixir-no-nels/ehos-python.git@v1.0.0


```

