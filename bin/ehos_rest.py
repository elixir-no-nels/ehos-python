#!/usr/bin/env python3

''' REST API for EHOS'''

import argparse
import pprint as pp

import ehos.tornado as tornado
import ehos.db as ehos_db
import ehos
import ehos.log_utils as logger
import ehos.utils

db = None

class RootHandler (tornado.BaseHandler):

    def get(self):
        self.render('index.html', title='My title', message='Hello world')


class Clouds (tornado.BaseHandler):

    def set_default_headers(self):
        #print( "setting headers!!!")
        #self.set_header("Access-Control-Allow-Origin", "*")
        #self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        #self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Content-Type", 'application/json; charset="utf-8"')


    def get(self, id:str=None):

        arguments = self._arguments()

        arguments = self._valid_arguments(arguments, ['name'])
        if id is not None:
            arguments[ 'id' ] = id

        #pp.pprint( arguments )

        data = db.clouds(**arguments)

        #print( 'In clouds @@@@ ')
        self.set_json_header()
        self.send_response( data )


class Nodes (tornado.BaseHandler):

    def set_default_headers(self):
        #print( "setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self, id:int=None):

        arguments = self._arguments()

        arguments = self._valid_arguments(arguments, ['cloud_id', 'node_state_id', 'vm_state_id'])
        if id is not None:
            arguments[ 'id' ] = id

        #pp.pprint( arguments )
        data = db.nodes(**arguments)

        #print( 'In clouds @@@@ ')
        self.set_json_header()
        self.send_response( data )

class NodeStatus(tornado.BaseHandler):

    def set_default_headers(self):
        #print( "setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):

        data = db.vm_states()
        self.set_json_header()
        self.send_response( data )

class NodeStates(tornado.BaseHandler):

    def set_default_headers(self):
        #print( "setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):

        data = db.node_states()

        self.set_json_header()
        self.send_response( data )


class Settings(tornado.BaseHandler):

    def set_default_headers(self):
        #print( "setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        #self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET, PATCH, OPTIONS')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Allow-Headers',
                    'Content-Type, Access-Control-Allow-Origin, Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods')


    def get(self, id:int=None):
        print( 'get...')

        arguments = self._arguments()

        #arguments = self._valid_arguments(arguments, ['cloud_id', 'node_state_id', 'vm_state_id'])
        #if id is not None:
        #    arguments[ 'id' ] = id

        #pp.pprint( arguments )
        data = db.settings_flat(**arguments)
        data = list( filter( lambda x:'clouds' not in x['name'], data  ))
        data = sorted( data, key=lambda k: k['name'] )
        pp.pprint( data )
        #print( 'In clouds @@@@ ')
        self.set_json_header()
        self.send_response( data )


    def options(self, id:str=None):
        print( 'checking options...')
        pass

    def patch(self, id:int=None):
        print( 'patch... ID:', id)
        setting = self.json_decode(self.request.body)
        pp.pprint( setting )
        db.set_setting(name=setting['name'], value=setting['value'], setting_id=id)

        self.send_response_204( )

def main():
    parser = argparse.ArgumentParser(description='ehos_rest: the ehos rest service daemon')

    parser.add_argument('-l', '--logfile', default=None, help="Logfile to write to, default is stdout")
    parser.add_argument('-v', '--verbose', default=4, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('config_file', metavar='config-file', nargs='?', help="yaml formatted config file", default=ehos.utils.find_config_file('ehos.yaml'))

    args = parser.parse_args()
    logger.init(name='ehosd', log_file=args.logfile )
    logger.set_log_level( args.verbose )

    logger.info("Using config file: {}".format( args.config_file))


    config = ehos.utils.get_configuration(args.config_file)
    #pp.pprint( config )
    #ehos.init( condor_init=False)
    global db
    db = ehos_db.DB()
    db.connect(config.daemon.database)

    urls = [(r'/', RootHandler),
             (r'/nodes/?$', Nodes ),
             (r'/nodes/(\d+?)/?$', Nodes ),
             (r'/nodes/states/?$', NodeStates ),
             (r'/nodes/status/?$', NodeStatus ),
             (r'/clouds/?$', Clouds ),
             (r'/clouds/(\d+?)/?$', Clouds ),
             (r'/settings/(\d+)/?$', Settings ),
             (r'/settings/?$', Settings ),
        ]


    tornado.run_app( urls, debug=True, template_path="/home/brugger/projects/BloodFlow/templates/" )


if __name__ == "__main__":
    main()
