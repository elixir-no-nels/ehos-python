#!/usr/bin/env python3
""" 
 
 
 
 Kim Brugger (05 Apr 2019), contact: kim.brugger@uib.no
"""

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)

import typing
import requests

JSON_TEMPLATE = {"measurement": 'str',
                "tags": {},
                "fields": {}}


class Tick(object):

    def __init__(self, url:str, database:str, user:str=None, passwd:str=None ) -> None:
        self.url    = url
        self.db     = database
        self.user   = user
        self.passwd = passwd


    def _make_to_list(self, data ):
        if not isinstance( data, list):
            data = [data]
        return data


    @typing.overload
    def _generate_line(self, points:list) -> str:
        ...

    @typing.overload
    def _generate_line(self, points:dict) -> str:
        ...

    def _generate_line(self, points ) -> str:
        
        points = self._make_to_list(points)
        data = []
        
        for point in points:
            tags = []
            for key, value in point[ 'tags' ].items():
                tags.append("{}={}".format( key, value))

            fields = []            
            for key, value in point[ 'fields' ].items():
                fields.append("{}={}".format( key, value))

            if ( 'time' in point):
                data.append( "{measurement},{tags} {fields} {time}".format(measurement=point['measurement'],
                                                                                tags=",".join(tags),
                                                                                fields=",".join(fields),
                                                                                time=point.get('time', '')))
            else:
                data.append( "{measurement},{tags} {fields}".format(measurement=point['measurement'],
                                                                         tags=",".join(tags),
                                                                         fields=",".join(fields)))

        data = "\n".join( data )
        #print( data )
        return data
        
    
    @typing.overload
    def write_points(self, points:list) -> bool:
        ...

    @typing.overload
    def write_points(self, points:dict) -> bool:
        ...
        
    def write_points(self, points) -> bool:

        #json_utils.validate_json(points, JSON_TEMPLATE )
        
        data = self._generate_line(points )

        url = "{url}/write?db={db}".format( url=self.url, db=self.db)
        print( url )
        
        if self.user is not None and self.passwd is not None:
            res = requests.post(url, auth=(self.user, self.passwd), data=data)

            print(res)
            if res.status_code != 204:
                return False

        else:
            res = requests.post(url, auth=(self.user, self.passwd), data=data)

            print(res)
            if res.status_code != 204:
                return False
        return True


