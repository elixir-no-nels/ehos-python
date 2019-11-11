import os
import json

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application

from tornado.web import RequestHandler
import tornado.gen as gen
import tornado

import pprint as pp




class BaseHandler( RequestHandler ):

    def remote_ip(self):
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip

        return remote_ip


    
    def prepare(self):
        ''' change the strings from bytestring to utf8 '''
        
        self.form_data = {
            key: [val.decode('utf8') for val in val_list]
            for key, val_list in self.request.arguments.items()
        }


    def _arguments(self):

        values = {}
        for argument in self.request.arguments:
            values[ argument ] = self.get_argument( argument )

        return values

    def _check_arguments(self, values:dict, valid:list) -> bool:

        for key in values.keys():
            if key not in valid:
                return False

        return True

    def json_decode(self, value):

        return tornado.escape.json_decode( value )


    def _valid_arguments(self, values:dict, valid:list) -> bool:

        valid_values = {}

        for key in values:
            if key in valid:
                valid_values[ key ] = values[ key ]

        return valid_values

    def set_ACAO_header(self, sites="*"):
#        print( "setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", sites)
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


    def set_json_header(self):
         """Set the default response header to be JSON."""
         self.set_header("Content-Type", 'application/json; charset="utf-8"')

    # Success
    def send_response(self, data=None, status=200):
        """Construct and send a JSON response with appropriate status code."""

        self.set_status(status)
        # check if the data is already in valid json format, otherwise make it
        try:
            json_object = json.loads( data )
        except:
            data = json.dumps(data)


        return self.write( data )


    def send_status_code(self, status=200):
        """Construct and send an empty response with appropriate status code."""

        self.set_status(status)
        return self.finish( )

    
    # Created
    def send_response_201(self):
        return self.send_response( data=None, status=201)

    # Accecpted
    def send_response_202(self, data):
        return self.send_status_code( status=202)

    # No content
    def send_response_204(self):
        return self.send_status_code( status=204)

    # bad request
    def send_response_400(self, data):
        pp.pprint( data )
        return self.send_response( data, 400)

    # Unauthorized
    def send_response_401(self, data):
        return self.send_response( data, status=401)

    # Forbidden
    def send_response_403(self, data):
        return self.send_response( data, status=403)

    # Not fund
    def send_response_404(self, data):
        return self.send_response( data, status=404)

    # Internal Server Error
    def send_response_500(self, data):
        return self.send_response( data, status=500)

    # Not Implemented
    def send_response_501(self, data):
        return self.send_response( data, status=501)

    # Service Unavailable
    def send_response_503(self, data):
        return self.send_response( data, status=503)

        

def run_app(urls, port=8888, **kwargs):

    app = Application(urls, **kwargs)
    app.listen(port)
    IOLoop.current().start()
    
        
