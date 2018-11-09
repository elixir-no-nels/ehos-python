""" 
 
 
 
 Kim Brugger (09 Nov 2018), contact: kim@brugger.dk
"""

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)


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
    

    
def add_stat(context_id:int, target_id:int, value:str):
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

    _add_entry('stat', context_id, target_id, value)


def add_event(context_id:int, target_id:int, value:str):
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

    _add_entry('event', context_id, target_id, value)
    
