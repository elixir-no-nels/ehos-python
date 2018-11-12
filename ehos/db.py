# -*- coding: utf-8 -*-

import records



from os import path

import records

import file_utils
import string_utils

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

    return db



def execute_file(sql_file):
    global DB
    for command in file_utils.read_file_content(sql_file).replace("\n", " ").split(';'):
        if command.strip() == "":
            continue
        DB.query(command)


def execute_query(sql):
    global DB
    return DB.query(sql).as_dict()


def execute_nonquery(sql):
    global DB
    return DB.query(sql)


def execute_count(sql):
    global DB
    return DB.query(sql).all()[0].count


def get_all(tbl, flds="*", order_by=None):
    sql = 'SELECT %s FROM %s' % (flds, tbl)
    if order_by:
        sql = '%s ORDER BY %s' % (sql, order_by)
    return execute_query(sql)


def get_by_id(tbl, id_val, flds="*"):
    sql = "SELECT %s FROM %s WHERE id ='%s'" % (flds, tbl, id_val)
    res = execute_query(sql)
    return res[0] if len(res) == 1 else None


def record_exists(tbl, id_val):
    return get_by_id(tbl, id_val) is not None


def delete_by_id(tbl, id_val):
    execute_nonquery("DELETE FROM %s WHERE id ='%s'" % (tbl,id_val))


def key_val_where(keyVals):
    where = ''
    for col_name in keyVals.keys():
        col_val = keyVals[col_name]
        if not string_utils.is_number(col_val):  # assume it's text
            col_val = "'%s'" % col_val
        where = string_utils.append_and_filter(where, "%s = %s" % (col_name, col_val))
    return where


def delete_by_column(tbl, col_name, col_val):
    delete_by_columns(tbl, {col_name: col_val})


def delete_by_columns(tbl, keyVals):
    execute_nonquery('DELETE FROM %s WHERE %s ' % (tbl, key_val_where(keyVals)))


def get_by_column(tbl, col_name, col_val, flds="*", order_by=None):
    return get_by_columns(tbl, {col_name: col_val}, flds, order_by)


def get_by_columns(tbl, keyVals, flds="*", order_by=None):
    sql = 'SELECT %s FROM %s WHERE %s ' % (flds, tbl, key_val_where(keyVals))
    if order_by:
        sql = "%s ORDER BY %s" % (sql, order_by)
    return execute_query(sql)


def get_add_sql(tbl, fields):
    flds = ""
    values = ""
    for fld in fields:
        flds = string_utils.append_with_delimiter(flds, fld, ",")
        values = string_utils.append_with_delimiter(values, ":%s" % fld, ",")
    return ("insert into %s(%s) values(%s) RETURNING id" % (tbl, flds, values))


def get_update_sql(tbl, fields, filters=["id"]):
    flds = ""
    for fld in fields:
        flds = string_utils.append_with_delimiter(flds, fld + "=:%s" % fld, ",")
    fltrs = ""
    for fltr in filters:
        fltrs = string_utils.append_with_delimiter(fltrs, fltr + "=:%s" % fltr, " AND ", "(", ")")
    return ("update %s set %s where %s" % (tbl, flds, fltrs))


def get_search_where(flds):
    filters = ""
    for fld in flds:
        filters = string_utils.append_with_delimiter(filters, "lower(%s) Like lower (:%s)" % (fld, fld), " OR ")
    return filters


def get_search_sql(tbl, search_fields, summary_fields="*"):
    return ("select %s from %s where %s" % (summary_fields, tbl, get_search_where(search_fields)))


def get_count(tbl):
    return execute_count("Select count(*) from %s " % tbl)


def get_count_by_column(tbl, col_name, col_val):
    return get_count_by_columns(tbl, {col_name: col_val})


def get_count_by_columns(tbl, keyVals):
    return execute_count("SELECT count(*) FROM %s WHERE %s" % (tbl, key_val_where(keyVals)))


def group_count(tbl, col_name):
    return execute_query("select %s, count(*) from %s group by %s" % (col_name, tbl, col_name))

