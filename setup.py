from setuptools import setup
import json

def readme():
    with open('README.rst') as f:
        return f.read()

def get_version():
    with open('version.json') as json_file:
        data = json.load(json_file)

    return "{}.{}.{}".format( data['major'], data['minor'], data['patch'])



setup(name='ehos',
      version= get_version(),
      description='Elastic HTCondor OpenStack Scaling',
      url='https://github.com/elixir-no-nels/ehos-python/',
      author='Kim Brugger',
      author_email='kim.brugger@uib.no',
      license='MIT',
      packages=['ehos'],
      install_requires=[
          'htcondor',
          'typing',
          'munch',
          'openstacksdk',
          'records',
      ],
      classifiers=[
        'License :: MIT License',
        'Programming Language :: Python :: +3.6'
        ],      
      scripts=['bin/ehosd.py',
               'bin/ehos_deployment.py',
               'bin/ehos_create_config.py',
               'bin/ehos_cloud_setup.py',
               'bin/condor_run_jobs.py',
               'bin/ehosd_config.py'
#               'bin/ehos_status.py'
           ],
      # install our config files into an ehos share.
      data_files=[('share/ehos/', ['share/base.yaml',
                                   'share/master.yaml',
                                   'share/execute.yaml',]),
                  ('etc/ehos/', ['etc/ehos.yaml.example',
                                 'etc/ehos.yaml.template']),
 #                 ('/etc/systemd/system/',['ehos.service'])
                 ],
      include_package_data=True,
      zip_safe=False)
