import pprint as pp
import sys
import os 
import re
import subprocess
import tempfile

import db as db

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import or_, and_


# Globlal variables to be used through out the script
Session = None
Base    = None

dbase     = 'genetics_ark_dev'
db_host   = 'localhost'
db_user   = 'easih_admin'
db_passwd = 'easih'
db_model  = 'mysql'

def init_database( dbase = dbase, db_host = db_host, db_user = db_user, db_passwd = db_passwd, db_model = db_model) :

    """initiate the connection to the database.

    Args:
        dbase (str): database name
        db_host (str): the server name of the database 
        db_user (str): who to connect as
        db_passwd (str): the password for the user, if applicable 
        db_model (str): model, eg: mysql
            
    Returns:
        Bool
        
    Raises:
        All sqlalchemy exceptions are re-raised

    """
    global Session, Base

    try:
        Session, Base = db.init_database(dbase, db_host, db_user, db_passwd, db_model)
    except:
        raise
        return False

    return True


def commit( ):
    """Commits any changes to the database

    Args:
        None
    Returns:
        Boolean

    Raises:
        All sqlalchemy exceptions are re-raised

    """

    global Session
    try:
        Session.commit()
    except:
        raise

    return True



def delete( entry ):
    """delete object from database

    Args:
        entry (obj): sqlalchemy object to delete
    Returns:
        None

    Raises:
        All sqlalchemy exceptions are re-raised

    """

    global Session
    try:
        Session.delete( entry )
        commit()
    except:
        raise

    return True



def check_db_init():
    """ Checks if the database connection have been initiated, otherwise raises a RuntimeWarning


    """

    if Base == None or Session == None:
        raise RuntimeWarning('Database connection not initialised yet')


#================== Sample functions =========================


def node( name ):
    """Get, or add, a node from the database. 

    If newly created the object added value is set to true

    Args:
        uuid (str)      : The node uuid
        name (str)      : The node name
            
    Returns:
        Single sample database object
        
    Raises:
        All sqlalchemy exceptions are re-raised

    """

    check_db_init()
    try:
        node, added = db.get_or_create(Session,
                                         Base.classes.node,
                                         name = name,
                                         uuid = uuid)

        commit()
        
    except:
        raise

    node.added = added
    return node




def nodes( id = None, name = None, uuid=None, status=None ):
    """Get all samples from the database filtered by any of the args

    If newly created the object added value is set to true

    Args:
        id(int)          : database id
        name (str)       : The node name
        uuid (str)       : The node uuid 
        status (str)     : The node uuid 

    Returns:
        database Query object
        
    Raises:
        All sqlalchemy exceptions are re-raised

    """
    constraints = []

    if ( id is not None):
        constraints.append( Base.classes.node.id == id )

    if ( name is not None):
        constraints.append( Base.classes.node.name == name )

    if ( uuid is not None):
        constraints.append( Base.classes.node.uuid == uuid )

    if ( status is not None):
        constraints.append( Base.classes.node.status == status )


    check_db_init()
    try:
        samples = Session.query( Base.classes.node ).filter( and_(*constraints ))

    except:
        raise

    return node
