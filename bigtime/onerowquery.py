#!/usr/bin/env python

from pims.database.pimsquery import mysql_con
from pims.database.samsquery import mysql_con_yoda
from pims.utils.pimsdateutil import samsops_timestamp_to_datetime
from pims.utils.pimsdateutil import dtm2unix

# FIXME the if host == 'yoda' kludge was quick fix here
# return True if table exists on host; otherwise, return False
def table_exists(table, host='manbearpig'):
    """return True if table exists on host; otherwise, return False"""
    if host == 'yoda':
        con = mysql_con_yoda(db='samsmon')
    else:
        con = mysql_con(host=host)
    cursor = con.cursor()
    query = "show tables like '%s';" % table
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    con.close()
    if result:
        return True
    return False

# return unixtime query result from "onerow [rt]" db table or None (if empty)
def query_onerow_unixtime(table, host='manbearpig'):
    """return unixtime query result from "onerow [rt]" db table or None (if empty)"""
    utime = None
    con = mysql_con(host=host)
    cursor = con.cursor()
    query = 'select time from %s;' % table
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    con.close()
    if result:
        utime = result[0][0]
    return utime

# return unixtime query result from timestamp for given ee in ee_packet db table or None (if empty)
def query_timestamp_kludge(ee_id, table='ee_packet', schema='samsmon', host='yoda'):
    """return unixtime query result from timestamp for given ee in samsmon.ee_packet db table or None (if empty)"""
    utime = None
    con = mysql_con_yoda(db=schema)
    cursor = con.cursor()
    query = 'select timestamp from %s.%s where ee_id = "%s" order by timestamp desc limit 1;' % (schema, table, ee_id)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    con.close()
    if result:
        utime = dtm2unix( result[0][0] )
    return utime    

def demo():
    from pims.utils.pimsdateutil import unix2dtm
    for table in ['es03rt', 'es05rt', 'es06rt', '121f02rt', '121f03rt', '121f04rt', '121f05rt', '121f08rt']:
        if table_exists(table):
            utime = query_onerow_unixtime(table)
            print table,
            if utime:
                print unix2dtm(utime)
            else:
                print utime
        else:
            print table, 'does not exist'
    for ee_id in ['122-f02', '122-f03', '122-f04']:
        utime = query_timestamp_kludge(ee_id)
        print ee_id,
        if utime:
            print unix2dtm(utime)
        else:
            print utime

if __name__ == "__main__":
    demo()
