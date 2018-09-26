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
        'pysam',
        ],
      classifiers=[
        'Development Status :: 1.0.0',
        'License :: MIT License',
        'Programming Language :: Python :: 3.4'
        ],      
      scripts=['bin/deploy_system.py',
               'bin/ehosd.py',
           ],
#      package_data={'': ['modules/Vcf.pm']},
      include_package_data=True,
      zip_safe=False)
