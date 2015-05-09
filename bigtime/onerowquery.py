#!/usr/bin/env python

from pims.database.pimsquery import mysql_con

# return True if table exists on host; otherwise, return False
def table_exists(table, host='manbearpig'):
    """return True if table exists on host; otherwise, return False"""
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

def demo():
    from pims.utils.pimsdateutil import unix2dtm
    for table in ['121f02rt', '121f03rt', '121f05rt', 'es05rt', 'es06rt']:
        if table_exists(table):
            utime = query_onerow_unixtime(table)
            print table,
            if utime:
                print unix2dtm(utime)
            else:
                print utime
        else:
            print table, 'does not exist'

if __name__ == "__main__":
    demo()
