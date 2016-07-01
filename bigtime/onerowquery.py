#!/usr/bin/env python

from pims.database.pimsquery import mysql_con
from pims.database.samsquery import mysql_con_yoda
from pims.utils.pimsdateutil import samsops_timestamp_to_datetime
from pims.utils.pimsdateutil import dtm2unix
from pims.database.ee_packets import dbstat


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

# FIXME select timestamp, ee_id from ee_packet_rt;
# FIXME select timestamp, se_accel_se_id from se_accel_packet_rt;

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

# return unixtime query result from multi-row db table or None (if empty)
def query_hirap(table, host='towelie'):
    """return unixtime query result from multi-row db table or None (if empty)"""
    utime = None
    con = mysql_con(host=host)
    cursor = con.cursor()
    query = 'select time from %s order by time desc limit 1;' % table
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    con.close()
    if result:
        utime = result[0][0]
    return utime

# return unixtime query result from timestamp for given ee in ee_packet_rt db table or None (if empty)
def query_timestamp(ee_id, table='ee_packet_rt', schema='samsmon', host='yoda'):
    """return unixtime query result from timestamp for given ee in samsmon.ee_packet_rt db table or None (if empty)"""
    utime = None
    con = mysql_con_yoda(db=schema)
    cursor = con.cursor()
    query = 'select timestamp from %s.%s where ee_id = "%s" limit 1;' % (schema, table, ee_id)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    con.close()
    if result:
        utime = dtm2unix( result[0][0] )
    return utime    

# return unixtime query result from time for ee table (in like 122f07 db table) or None (if empty)
def query_timestamp_jimmy(table, host='jimmy'):
    """return unixtime query result from time for ee table (in like 122f07 db table) or None (if empty)"""
    count, tmin, tmax, age, rate, loc = dbstat(host, table)
    utime = dtm2unix( tmax )
    return utime    

# return unixtime query result from ku_timestamp gse_packet db table or None (if empty)
def query_ku_timestamp(table='gse_packet', schema='samsmon', host='yoda'):
    """return unixtime query result from ku_timestamp gse_packet db table or None (if empty)"""
    utime = None
    con = mysql_con_yoda(db=schema)
    cursor = con.cursor()
    query = 'select ku_timestamp from %s.%s order by ku_timestamp desc limit 1;' % (schema, table)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    con.close()
    if result:
        utime = dtm2unix( result[0][0] )
    return utime  

# insert fake unixtime into "onerow [rt]" db table
def debug_android_even_odd_minute_insert(table, host='chef'):
    """insert fake unixtime into "onerow [rt]" db table"""
    import datetime
    now = datetime.datetime.now()
    fake_dtm = now
    if now.hour % 2 != 0:
        if now.minute % 2 == 0:
            #print now.minute, " is even"
            fake_dtm -= datetime.timedelta(seconds=fake_dtm.second, microseconds=fake_dtm.microsecond)
            fake_dtm += datetime.timedelta(seconds=75)
            utime = dtm2unix(fake_dtm)
            con = mysql_con(host=host)
            cursor = con.cursor()
            query = 'replace into %s set time=%f;' % (table, utime)
            cursor.execute(query)
            cursor.close()
            con.close()

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
    for ee_id in ['122-f02', '122-f03', '122-f04', '122-f07']:
        utime = query_timestamp(ee_id)
        print ee_id,
        if utime:
            print unix2dtm(utime)
        else:
            print utime

if __name__ == "__main__":
    demo()
