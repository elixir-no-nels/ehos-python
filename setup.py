from setuptools import setup
def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='ehos',
      version='1.0.0',
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
      ],
      classifiers=[
        'Development Status :: 1.0.0',
        'License :: MIT License',
        'Programming Language :: Python :: 3.4'
        ],      
      scripts=['/usr/local/bin/deploy_ehos.py',
               '/usr/local/bin/ehosd.py',
           ],
      # install our config files into an ehos share.
      data_files=[('share/ehos/', ['ehos.yaml.example',
                                   'configs/base.yaml',
                                   'configs/master.yaml',
                                   'configs/submit.yaml',
                                   'configs/execute.yaml'])
                  ('/etc/systemd/system/',['ehos.service'])],
      include_package_data=True,
      zip_safe=False)
