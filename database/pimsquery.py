#!/usr/bin/env python

import os
import sys
import math
from time import sleep
import datetime
import socket
from MySQLdb import *
from _mysql_exceptions import *
from pims.config.conf import get_db_params
from pims.utils.iterabletools import pairwise
import pandas as pd
from hashlib import md5

# FIXME add logging feature

# FIXME need hostname for testing (db @home vs. @work)
_HOSTNAME = socket.gethostname()
if _HOSTNAME == 'jimmy':
    _HANDBOOK_HOST = 'yoda'
else:
    _HANDBOOK_HOST = 'localhost'    

# TODO class this up (c'mon man)
_SCHEMA, _UNAME, _PASSWD = get_db_params('pimsquery')

# FIXME did this sqlalchemy quick test wrt obspy
def quick_test(host, schema):
    from sqlalchemy import create_engine
    # 'mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>'
    # 'mysql://username:password@serverlocation/mysqldb_databasename?charset=utf8&use_unicode=0'
    engine = create_engine('mysql://' + _UNAME + ':' + _PASSWD + '@' + host + '/' + schema + '?charset=utf8&use_unicode=0')
    connection = engine.connect()
    result = engine.execute("select time from 121f03 order by time desc limit 9")
    for row in result:
        print "time:", row['time']
    r2 = engine.execute('select from_unixtime(time) as gmt from 121f03 order by time desc limit 6')
    for r in r2:
        print "GMT:", r['gmt']
    result.close()
    r2.close()
    
#quick_test('manbearpig', 'pims')
#raise SystemExit

# round a float up at 4th decimal place (db has time to only 4 decimal places of precision)
def ceil4(input): # the database has time to only 4 decimal places of precision
    """round a float up at the 4th decimal place"""
    return math.ceil(input*10000.0)/10000.0

# fetch all entries from pad.coord_system_db table [on kyle] into dataframe
class CoordQueryAsDataFrame(object):
    """fetch all entries from pad.coord_system_db table [on kyle] into dataframe"""
    def __init__(self, host='kyle', uname=_UNAME, passwd=_PASSWD):
        self.host = host
        self.schema = 'pad'
        self.uname = uname
        self.passwd = passwd        
        self.query = 'SELECT * FROM %s.coord_system_db;' % self.schema
        self.dataframe = self.coord_db_to_dataframe()

    def __str__(self):
        #self.run_query()
        #return '%s,%s' % (self.gse_tiss_dtm, self.aos_los)
        return 'self.dataframe'

    # fetch all entries from pad.coord_system_db table [on kyle] into dataframe
    def coord_db_to_dataframe(self):
        """fetch all entries from pad.coord_system_db table [on kyle] into dataframe"""
        con = Connection(host=self.host, user=self.uname, passwd=self.passwd, db=self.schema)
        cursor = con.cursor()
        cursor.execute(self.query)
        results = cursor.fetchall()
        cursor.close()
        con.close()
        df = pd.DataFrame( list(results) )
        df.columns = [rec[0] for rec in cursor.description]
        df.rename(columns={'coord_name':    'sensor',
                           'r_orient':      'roll',
                           'p_orient':      'pitch',
                           'y_orient':      'yaw',
                           'x_location':    'x',
                           'y_location':    'y',
                           'z_location':    'z'}, inplace=True)
        # convert unixtime to datetime and get rid of old column
        gmt = pd.to_datetime(df['time'], unit='s')
        df['gmt'] = gmt
        
        ## make gmt the index
        #df.set_index(gmt, inplace=True)
        ## cleanup to get rid of original unixtime column
        #df = df.drop(['gmt'], axis=1)
        
        # return sorted by sensor, then by gmt
        return df.sort(['sensor', 'time'], ascending=[1, 1])

    def filter_dataframe_sensors(self, regex_pattern):
        """keep only certain sensors matching regex_pattern"""
        self.dataframe = self.dataframe[ self.dataframe.sensor.str.contains(regex_pattern) ]
    
    def filter_pre2001(self):
        """get rid of bogus entries (CIR, FIR) on kyle"""
        self.dataframe = self.dataframe[ self.dataframe.gmt > datetime.datetime(2001, 1, 1) ]
    
    def consolidate_rpy_xyz(self):
        """for convenience, merge all of the location/orientation info into single column"""
        #self.dataframe['location'] = self.dataframe.location_name + "; " + \
        #                            "rpy: [" + self.dataframe.roll.map(str) + ", " + \
        #                                  self.dataframe.pitch.map(str) + ", " + \
        #                                  self.dataframe.yaw.map(str) + "], " + \
        #                            "xyz: [" + self.dataframe.x.map(str) + ", " + \
        #                                  self.dataframe.y.map(str) + ", " + \
        #                                  self.dataframe.y.map(str) + "]"
        self.dataframe['location'] = self.dataframe.location_name
        self.dataframe = self.dataframe.drop(['location_name', 'roll', 'pitch', 'yaw', 'x', 'y', 'z', 'time'], axis=1)
    
    def format_date(self, d):
        return d.strftime('new Date(%Y, %m, %d, %H, %M, %S)')
        
    def print_row(self, sensor, location, start, stop):
        """          [ 'SE-F02',  'USL, Location One',        new Date(2001, 5, 3,12,15,55),  new Date(2003,12,31,14,22,44) ],"""
        return "          [ '%s',\t'%s', %s, %s ]," % (sensor, location, self.format_date(start), self.format_date(stop))
    
    def per_sensor_pairwise_start_stop(self, sensor):
        sensor_entries = []
        df = self.dataframe[ self.dataframe.sensor.str.contains(sensor) ]
        if len(df) > 1:
            for a,b in pairwise( df.iterrows() ):
                sensor_entries.append( self.print_row(sensor, a[1].location, a[1].gmt, b[1].gmt) )
            sensor_entries.append( self.print_row(sensor, b[1].location, b[1].gmt, pd.Timestamp.now()) ) #.strftime('%Y-%m-%d %H:%M:%S')) )
        else:
            for a in df.iterrows():
                sensor_entries.append( self.print_row(sensor, a[1].location, a[1].gmt, pd.Timestamp.now()) ) #.strftime('%Y-%m-%d %H:%M:%S')) )
        return '\n'.join(sensor_entries)
        
    def get_rows(self):
        sensor_rows = []
        for sensor in self.dataframe['sensor'].unique():
            sensor_rows.append( self.per_sensor_pairwise_start_stop(sensor) )
        return '\n'.join(sensor_rows)


#####################################################################################
# SQL helper routines ---------------------------------------------------------------
# create a connection (with possible defaults), submit command, return all results
# try to do all connecting through this function to handle exceptions
# plugable 0-argument function to be called when idling. It can return true to stop idling. 
add_idle_function = None
def mysql_con(host='localhost', user=_UNAME, passwd=_PASSWD, db=_SCHEMA):
    return Connection(host=host, user=user, passwd=passwd, db=db)
def add_idle(idle_function):
    global add_idle_function
    add_idle_function = idle_function
def idle_wait(seconds = 0):
    for i in range(seconds):
        if add_idle_function:
            if add_idle_function():
                return 1
        sleep(1)
    else: # always execute at least once
        if add_idle_function:
            return add_idle_function()
    return 0
def db_connect(command, host='localhost', user=_UNAME, passwd=_PASSWD, db=_SCHEMA):
    sql_retry_time = 30
    repeat = 1
    while repeat:
        try:
            con = Connection(host=host, user=user, passwd=passwd, db=db)
            cursor = con.cursor()
            cursor.execute(command)
            results = cursor.fetchall()
            repeat = 0
            cursor.close()
            con.close()
        except MySQLError, msg:
            print 'MySQL call failed, will try again in %s seconds' % sql_retry_time
            if idle_wait(sql_retry_time):
                return []
    return results
#####################################################################################

# FIXME did this one kinda quick, so scrub it
class HandbookQueryFilename(object):
    """Query yoda for handbook filename (should be none or one)."""
    def __init__ (self, filename, host=_HANDBOOK_HOST, user=_UNAME, passwd=_PASSWD, db='pimsdoc', table='Document'):
        self.filename = filename
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.table = table
        self.file_exists = self._file_exists()
        
    def _file_exists(self):
        """Establish db connection."""
        _db_conn = connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db)
        files = self._query_file(_db_conn)
        _db_conn.close()
        if len(files) > 0:
            return True
        else:
            return False

    def _query_file(self, db_conn):
        """query for filename"""
        c = db_conn.cursor() 
        self._query_string = 'SELECT * FROM %s.%s where FileName = "%s";' % (self.db, self.table, self.filename)
        c.execute(self._query_string)
        s = c.fetchall()
        L = [a[0] for a in list(s)]
        return L

# FIXME this needs scrubbing on jimmy for yoda (and maybe new stored procedure/Routine)
def db_insert_handbook(fname, title, regime, category, host=_HANDBOOK_HOST, user=_UNAME, passwd=_PASSWD, db='pimsdoc'):
    """Attempt db_insert_handbook MySQL routine and output flag_ok boolean and a message."""
    err_msg = None

    # FIXME I do not know how to get MySQLdb callproc to work, so go with execute on this query string:
    query_str = """
    use pimsdoc;
    set @filename = '%s';   # filename
    set @title = '%s';      # title (same as source in stored procedure)
    set @regime = '%s';     # vibratory or quasi-steady
    set @category = '%s';   # crew, vehicle, or equipment
    call auto_insert_handbook(@filename, @title, @regime, @category);
    """ % (fname, title, regime, category)

    # check for pre-existing filename    
    hbcf = HandbookQueryFilename(fname)
    if hbcf.file_exists:
        return "Database problem %s already exists in one of the records" % fname
    
    try:
        con = Connection(host=host, user=user, passwd=passwd, db=db)
        cursor = con.cursor()

        # FIXME preferred, but not working: cursor.callproc('auto_insert_handbook', (fname, title, regime, category) )
        cursor.execute(query_str)
        
        cursor.close()
        con.close()
        
    except Exception, e:
        
        err_msg = "Error db_insert_handbook %s" % e.message

    return err_msg

class PadExpect(object):
    """Class for dictionary of results from pad db query on kyle for expected config values.

    Keyword arguments:
    database: string name of db to query (default 'pad' schema on kyle)
    table: string for table name (default 'expected_config')
    sensor: string for sensor designator (like '121f03')
    values: dictionary of {'fields':values}

    """

    def __init__ (self, database='pad', table='expected_config', sensor=None):
        """PadExpect constructor"""
        self.database = database
        self.table = table
        self.sensor = sensor
        self._excludeFields = ['time','sensor']
        self._db = connect(host="kyle", user=_UNAME, passwd=_PASSWD, db=database)
        self._fields = self._query_fields()
        self._values = self._query_expected_values()
        self._db.close()
        self.values = dict(zip(self._fields,self._values))

    def __repr__(self):
        s  = 'database (%s) shows sensor (%s) should have:' % (self.database, self.sensor)
        for f,v in self.values.iteritems():
            s += '\n %s = %s' % (f, v)
        return s
    
    def _query_fields(self):
        """return expected values as result of db query"""
        c = self._db.cursor()
        queryString = "DESCRIBE %s" % self.table
        c.execute(queryString)
        fields = []
        for f in c.fetchall():
            if f[0] not in self._excludeFields:
                fields.append(f[0])
        return fields
        
    def _query_expected_values(self):
        """return expected values as result of db query"""
        c = self._db.cursor()
        fieldString = string.join(self._fields,sep=',')
        queryString = "SELECT %s FROM %s WHERE sensor = '%s' ORDER BY time DESC LIMIT 1" % (fieldString, self.table, self.sensor)
        c.execute(queryString)
        expected_values = c.fetchone()
        return expected_values

# Query yoda for jaxa post file.
class JaxaPostPlotFile(object):
    """Query yoda for jaxa post file."""
    def __init__ (self, host='yoda', user=_UNAME, passwd=_PASSWD, db='jaxapost', table='plotfile'):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.table = table

    def insert(self, f):
        """insert entry for file found, presumably by ike along /misc/jaxa/mmadata/plot"""
        fname = os.path.basename(f)
        dtm, status = self.file_status(fname)
        if status in ['found', 'pending']:
            print 'NO INSERT BECAUSE %s EXISTS IN "%s" STATE ALREADY.' % (fname, status)
            return False
        
        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        md5sum = md5(f).hexdigest()
        querystr = "REPLACE INTO %s.%s ( time, file, status, host, md5sum ) VALUES ( '%s', '%s', 'found', '%s', '%s');" % (
            self.db, self.table, t, fname, _HOSTNAME, md5sum)
        try:
            db_conn = connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db)
            c = db_conn.cursor() 
            c.execute(querystr)
            db_conn.commit()
            b = True
        except Exception, e:
            db_conn.rollback()
            print e.message
            b = False
        db_conn.close()
        return b

    def update(self, fname, status):
        """update entry for file found, presumably by manbearpig WHAT JAXA-ISH PATH ON YODA?"""
        if not self.file_exists(fname):
            print 'NO UPDATE BECAUSE %s DOES NOT EXIST.' % fname
            return
        #UPDATE jaxapost.plotfile SET status="pending", time="2014-02-01 09:30:00" WHERE file = "121f05_intrms.csv";
        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        querystr = "UPDATE %s.%s SET status='%s', time='%s' WHERE file='%s';" % (
            self.db, self.table, status, t, fname)
        try:
            db_conn = connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db)
            c = db_conn.cursor() 
            c.execute(querystr)
            db_conn.commit()
        except Exception, e:
            db_conn.rollback()
            print e.message
        db_conn.close()

    def file_exists(self, fname):
        """Establish db connection and query if file exists."""
        querystr = 'SELECT * FROM %s.%s where file = "%s";' % (self.db, self.table, fname)
        files = self._run_query( querystr )
        # FIXME robustness: file is PK in db, so we should only get zero or one for len!?
        if len(files) > 0:
            return True
        else:
            return False

    def file_status(self, fname):
        """Establish db connection and query file state (found, pending, deployed, problem)"""
        if self.file_exists(fname):
            querystr = 'SELECT * FROM %s.%s where file = "%s";' % (self.db, self.table, fname)
            s = self._run_query( querystr )
            dtm, fname, status, host, md5sum = s[0]
        else:
            dtm, status = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'non-existent'
        return dtm, status

    def _run_query(self, querystr):
        """run query"""
        db_conn = connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db)
        c = db_conn.cursor() 
        c.execute(querystr)
        db_conn.close()
        s = c.fetchall()
        return s

def demo():
    err_msg = db_insert_handbook('hb_qs_crew_A_Nice_Enough_Title.pdf', 'A Nice Enough Title', 'quasi-steady', 'crew')
    
    if err_msg:
        print 'oh dear'
    else:
        print 'okay fine'
    
    #hbcf = HandbookQueryFilename('hb_vib_equipment_testing3.pdf')
    #print hbcf.file_exists
    
def demo_jaxapost():
    
    # create object to keep track of jaxa posting plotfile
    jppf = JaxaPostPlotFile() # host='localhost')
    
    # IKE: this is how we insert (as "found" file)
    jppf.insert('121f05_intrms.csv')
    
    # check if these files exist
    fnames = ['121f05_intrms.csv', 'holy_cow.csv', 'holy_cow2.csv']
    for fname in fnames:
        dtm, status = jppf.file_status(fname)
        print "at GMT", dtm, fname, "was", status
        
    ## MANBEARPIG: this is how we update from "found" to "pending" (or "deployed" or "problem")
    #jppf.update('holy_cow.csv', 'problem')
    #dtm, status = jppf.file_status('holy_cow.csv')
    #print "at GMT", dtm, 'holy_cow.csv', "was", status

# for Linux command-line usage, return zero when "insert as found"; otherwise non-zero
def ike_insert(f):
    """for Linux command-line usage, return zero when "insert as found"; otherwise non-zero"""
    # create object to keep track of jaxa posting plotfile
    jppf = JaxaPostPlotFile() # host='localhost')
    
    # IKE: this is how we insert, actually REPLACE, as "found" file
    if jppf.insert(f):
        sys.exit(0)
    else:
        sys.exit(-1)
        
if __name__ == "__main__":
    #demo()
    #demo_jaxapost()
    ike_insert('/misc/yoda/www/plots/sams/params/121f05_intrms.csv')