#!/usr/bin/env python

from pims.database.pimsquery import mysql_con

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
    for table in ['121f05rt', 'es05rt', 'es06rt']:
        utime = query_onerow_unixtime(table)
        print table,
        if utime:
            print unix2dtm(utime)
        else:
            print utime

if __name__ == "__main__":
    demo()
