#!/usr/bin/env python3

''' REST API for EHOS'''

import argparse
import pprint as pp

import ehos.tornado as tornado
import ehos.instances_db as instances_db
import ehos
import ehos.log_utils as logger

db = None

class RootHandler (tornado.BaseHandler):

    def get(self):
        self.render('index.html', title='My title', message='Hello world')


class Clouds (tornado.BaseHandler):

    def set_default_headers(self):
        print( "setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    
    def get(self, id:str=None):

        if id is None:
            data = db.clouds()
        else:
            data = db.cloud( id=id)

        print( 'In clouds @@@@ ')
        self.set_json_header()
        self.send_response( data )


class Nodes (tornado.BaseHandler):

    def set_default_headers(self):
        print( "setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self, id:str=None):

        if id is None:
            data = db.nodes()
        else:
            data = db.node( id=id)

        print( 'In clouds @@@@ ')
        self.set_json_header()
        self.send_response( data )



def main():
    parser = argparse.ArgumentParser(description='ehos_rest: the ehos rest service daemon')

    parser.add_argument('-l', '--logfile', default=None, help="Logfile to write to, default is stdout")
    parser.add_argument('-v', '--verbose', default=4, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('config_file', metavar='config-file', nargs='?',    help="yaml formatted config file", default=ehos.find_config_file('ehos.yaml'))

    args = parser.parse_args()
    logger.init(name='ehosd', log_file=args.logfile )
    logger.set_log_level( args.verbose )

    logger.info("Using config file: {}".format( args.config_file))


    config = ehos.readin_config_file( args.config_file )
    pp.pprint( config )
    #ehos.init( condor_init=False)
    global db
    db = instances_db.InstancesDB(config.ehos_daemon.database)




    urls = [(r'/', RootHandler),
             (r'/nodes/?$', Nodes ),
             (r'/nodes/(.+?)/?$', Nodes ),
             (r'/clouds/?$', Clouds ),
             (r'/clouds/(.+?)/?$', Clouds ),

        ]


    tornado.run_app( urls, debug=True, template_path="/home/brugger/projects/BloodFlow/templates/" )


if __name__ == "__main__":
    main()
