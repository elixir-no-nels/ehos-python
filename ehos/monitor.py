""" 
 
 
 
 Kim Brugger (09 Nov 2018), contact: kim@brugger.dk
"""

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)
import time
import datetime


import records


db = None

def connect(url:str) -> None:
    """ connects to a database instance 

    Args:
      url: as specified by sqlalchemy ( {driver}://{user}:{password}@{host}:{port}/{dbase}

    Returns:
      none

    Raises:
      RuntimeError on failure.


    """
    global db
    
    db = records.Database( url )
        


def _add_value(table:str, value:int):
    """ low level function for adding a value to a table

    Args:
      table: table to add to
      value: the value to get/add

    returns:
      None

    Raises:
      None
    """

    db.query("insert into {table} (value) VALUES ('{value}');".format(table=table, value=value))
    return ( _get_value_id( table, value ))



    
def _get_value_id(table:str, value:int):
    """ low level function for getting a value if present in database, otherwise add the entry.

    Args:
      table: table to add to
      value: the value to get/add

    returns:
      None

    Raises:
      None
    """

    rows = db.query("select * from {table} where value = '{value}';".format(table=table, value=value)).as_dict()

    
    if len( rows) > 0:
        return rows[ 0 ]['id']

    else:
        return _add_value( table, value )
        
    

    
def _get_context_id(table:str, value:str):
    """ adds a standard stat/event entry to a table function, that will be wrapped by simpler functions below


    Args:
      table: table to add to
      context: the context the entry relates to, eg create, total_nodes etc

    returns:
      None

    Raises:
      None
    """

    return _get_value_id("{}_context".format( table ), value )


def _get_target_id(table:str, value:str):
    """ adds a standard stat/event entry to a table function, that will be wrapped by simpler functions below


    Args:
      table: table to add to
      context: the context the entry relates to, eg create, total_nodes etc

    returns:
      None

    Raises:
      None
    """

    return _get_value_id("{}_target".format( table ), value )

    

    
def _add_entry(table:str, context:int, target:int, value:str):
    """ adds a standard stat/event entry to a table function, that will be wrapped by simpler functions below


    Args:
      table: table to add to
      context: the context the entry relates to, eg create, total_nodes etc
      target: ip, name, region
      value: what happened, nr or something else

    returns:
      None

    Raises:
      None
    """

    context_id = _get_context_id( table, context);
    target_id  = _get_target_id( table, target);


    q = "insert into {table} (context_id, target_id, value) VALUES ('{context_id}','{target_id}', '{value}');"
    

    db.query(q.format( table=table, context_id=context_id, target_id=target_id, value=value))
    

    
def add_stat(context:int, target:int, value:str):
    """ adds a standard stat/event entry to a table function, that will be wrapped by simpler functions below


    Args:
      table: table to add to
      context:  
      target:
      value: what happened, nr or something else

    returns:
      None

    Raises:
      None
    """

    _add_entry('stat', context, target, value)


def add_event(context:int, target:int, value:str):
    """ adds a standard stat/event entry to a table function, that will be wrapped by simpler functions below


    Args:
      table: table to add to
      context_id:  
      target_id:
      value: what happened, nr or something else

    returns:
      None

    Raises:
      None
    """

    _add_entry('event', context, target, value)
    

    
def _get_timeserie_range(start:str, end:str, keys:list=[], res:int=60, method:str='mean') -> {}:
    """Extract a timeserie from the database. The values are filtered by
       keys if provided. The timerange is divided into bins of res
       size. If multiple values occur for a key the mean value is
       returned.

    Args:
    start: datatime format start time
    end: datatime format start time
    keys: if provided keys to filter on
    method: how to handle multipl occurences in a bin. Possibilites are: mean, median, sum

    Returns
      dict of times and observations seen in each one

    Raises:
      None

    """


    Q =  "select s.ts, st.value as target, sc.value as context, s.value as count "
    Q += "from stat s, stat_context sc, stat_target st where s.context_id = sc.id and s.target_id=st.id "
    Q += " and ts >= '{}' and ts <= '{}' order by ts;"


    Q = Q.format( start, end )

    db_data =  db.query( Q ).as_dict()

    
    data = {}
    for entry in db_data:
        key = "{}-{}".format( entry['target'], entry['context'])
        if ( keys != [] and key not in keys):
            continue

        ts   = entry[ 'ts' ].timestamp()
        ts = int( ts/res)*res

        ts = datetime.datetime.fromtimestamp( ts )

        if ( ts not in data ):
            data[ ts ] = {}
            
        if key not in data[ ts ]:
            data[ ts ][ key ] = []

        data[ ts ][ key ].append( int(entry['count']))
        
    for timestamp in data:
        for key in data[ timestamp]:
            if method == 'sum':
                data[ timestamp][ key ] = sum(data[ timestamp][ key ])
            if method == 'mean':
                data[ timestamp][ key ] = sum(data[ timestamp][ key ])/len(data[ timestamp][ key ])
            elif method == 'median':
                data[ timestamp][ key ] = sorted( data[ timestamp][ key ])
                data[ timestamp][ key ] = data[ timestamp][ key ][ int(len ( data[ timestamp][ key ])/2)]
                

        
    return data


def transform_timeserie_to_dict( timeserie:dict):

    trans = {'x': []}

    for timestamp in sorted(timeserie):
        trans[ 'x' ].append( str( timestamp))
        
        for key in timeserie[ timestamp ]:
            if key not in trans:
                trans[ key ] = []
            trans[ key ].append( timeserie[ timestamp ][key] )

    

    return trans

def _get_timeserie_offset(seconds:int, keys:list=[], method:str='mean'):


    now = time.time()

    
    start = datetime.datetime.fromtimestamp( now - seconds)
    end   = datetime.datetime.fromtimestamp( now )

    return _get_timeserie_range(start = start, end=end, keys=keys, method=method)


def timeserie_5min(keys:list=[], method:str='mean'):

    return _get_timeserie_offset(5*60, keys=keys, method=method)

def timeserie_10min(keys:list=[], method:str='mean'):

    return _get_timeserie_offset(10*60, keys=keys, method=method)

def timeserie_30min(keys:list=[], method:str='mean'):

    return _get_timeserie_offset(30*60, keys=keys, method=method)

def timeserie_1hour(keys:list=[], method:str='mean'):

    return _get_timeserie_offset(1*60*60, keys=keys, method=method)

def timeserie_2hour(keys:list=[], method:str='mean'):

    return _get_timeserie_offset(2*60*60, keys=keys, method=method)

def timeserie_5hour(keys:list=[], method:str='mean'):

    return _get_timeserie_offset(5*60*60, keys=keys, method=method)

def timeserie_10hour(keys:list=[], method:str='mean'):

    return _get_timeserie_offset(10*60*60, keys=keys, method=method)

def timeserie_1day(keys:list=[], method:str='mean'):

    return _get_timeserie_offset(1*24*60*60, keys=keys, method=method)
