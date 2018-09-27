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
        'openstacksdk',
        ],
      classifiers=[
        'Development Status :: 1.0.0',
        'License :: MIT License',
        'Programming Language :: Python :: 3.4'
        ],      
      scripts=['bin/deploy_ehos.py',
               'bin/ehosd.py',
           ],
      data_files=[('/etc/ehos/', ['configs/base.yaml',
                                  'configs/master.yaml',
                                  'configs/submit.yaml',
                                  'configs/execute.yaml'])]
#      package_data={'': ['modules/Vcf.pm']},
      include_package_data=True,
      zip_safe=False)
