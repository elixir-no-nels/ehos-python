#!/usr/bin/python3
""" 
 
Checks that a yaml file is correctly formatted.
 
 
 Kim Brugger (16 Oct 2018), contact: kim@brugger.dk
"""

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)
import yaml
import argparse


def check_yaml(infile:str) -> None:
    """ Checks that a yaml file is correctly formatted

    Args:
      infile: file to check

    Returns:
      None

    Raises:
      passes through any yaml module exceptions
    """

    
    with open(infile, 'r') as stream:
        try:
            config = yaml.load(stream)

            print("{} file is in correct yaml format".format( infile ))
            
        except yaml.YAMLError as exc:
            print("{} file is not in correct yaml format".format( infile ))
            print(exc)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='yaml_checker: check the correctness of a yaml file')
    parser.add_argument('yaml_file', metavar='yaml_file', nargs="+",   help="yaml formatted config file")

    args = parser.parse_args()

    for yaml_file in args.yaml_file:
        check_yaml( yaml_file )
        
