#!/usr/bin/env python
version = '$Id$'

import os
import sys
import socket
import datetime
import pandas.io.sql as psql
import pandas as pd
import MySQLdb
from cStringIO import StringIO
from pims.utils.pimsdateutil import parser
from pims.database.pimsquery import db_connect, mysql_con
from pims.database.samsquery import mysql_con_yoda
from pims.realtime.dbgapdetect_headerfooter import HEADER, FOOTER
from pims.files.utils import tail
from pims.utils.pimsdateutil import floor_ten_minutes

# TODO
# - robustness for missing table (or go out and find hosts/tables automagically)
# - iterate over list of sensors
# - better way to get expected packets per second (SAMS/MAMS HiRAP, SampleRate, what else)
# - some form of pivot table to show results
# - allow more than 23 hours of history (the GROUP BY in MySQL call mucks this up otherwise)

#### input parameters
###defaults = {
###'sensor':           '121f03',       # sensor = table name
###'packets_per_sec':  '8',            # expected value for this sensor for this gap check period
###'host':             'tweek',        # like tweek for 121f03
###'min_pct':          '0',            # show hourly periods with pkt count < min_pct (USE ZERO TO SHOW ALL)
###'hours_ago':        '23',           # start checking this many hours ago
###}

# defaults
#defaults = {
#'sensorhosts': [
#    #('hirap',       'towelie',      'pims',     '5.21'),    
#    ('121f02',      'tweek',        'pims',     '8'),
#    ('121f03',      'tweek',        'pims',     '8'),
#    ('121f04',      'tweek',        'pims',     '8'),
#    ('121f05',      'chef',         'pims',     '8'),
#    ('121f08',      'kenny',        'pims',     '8'),
#    ('es03',        'kenny',        'pims',     '7.84'),
#    ('es05',        'kenny',        'pims',     '7.84'),  # 3.92 or 7.84
#    ('es06',        'chef',         'pims',     '7.84'),
#    ('es09',        'kenny',        'pims',     '7.84'),
#    ('es20',        'chef',         'pims',     '7.84'),
#    #('oss',         'stan',         'pims',     '0.0625'),
#    ('cu_packet',   'yoda',         'samsnew',  '1')
#    ],          
#'packets_per_sec':  '8',    # expected value for this sensor for this gap check period
#'min_pct':          '0',    # show hourly periods with pkt count < min_pct (USE ZERO TO SHOW ALL)
#'hours_ago':        '22',   # start checking this many hours ago
#}
defaults = {
'sensorhosts': [
    ('121f02',      'kenny',        'pims',     '8'),
    ('121f03',      'kenny',        'pims',     '8'),
    ('121f04',      'kenny',        'pims',     '8'),
    ('121f05',      'cartman',         'pims',     '8'),
    ('121f08',      'cartman',        'pims',     '8'),
    ('es03',        'cartman',        'pims',     '7.84'),
    ('es05',        'cartman',        'pims',     '7.84'),  # 3.92 or 7.84
    ('es06',        'cartman',         'pims',     '7.84'),
    ('es09',        'cartman',        'pims',     '7.84'),
    ('es20',        'cartman',         'pims',     '7.84'),
    #('oss',         'stan',         'pims',     '0.0625'),
    ('cu_packet',   'yoda',         'samsnew',  '1')
    ],          
'packets_per_sec':  '8',    # expected value for this sensor for this gap check period
'min_pct':          '0',    # show hourly periods with pkt count < min_pct (USE ZERO TO SHOW ALL)
'hours_ago':        '22',   # start checking this many hours ago
}
parameters = defaults.copy()

def FAKE_floor_ten_minutes(x):
    d = pd.to_datetime(x)
    r = floor_ten_minutes(d)        
    return '%s' % r

class DatabaseHourlyGapsHoursAgo(object):
    """
    Info on database gaps given sensor (i.e. table), host, expected packets per second, min%, and hours ago (to now).
    """
    def __init__(self, sensor='121f03', host='tweek', packets_per_sec=8, hours_ago=23, min_pct=0):
        """Initialize."""
        self.sensor = sensor
        self.host = host
        self.packets_per_sec = packets_per_sec
        ## FIXME next "if" ignores "defaults" tuple object [which itself gets overcome by packets_per_sec just below it]
        ##       Plus, it overrides input param...not good, but quick and useful for now.
        #if self.sensor.startswith('es'):
        #    self.packets_per_sec = 7.84
        self.hours_ago = hours_ago
        self.expect_packet_count = self.packets_per_sec * 3600.0 # count for one hour's worth          
        self.min_pct = min_pct
        self.start, self.stop = self._get_times()
        self.dataframe = None
        # dataframe formatters (for db query to dataframe)
        self.formatters = dict([
        ('%s pct'  % self.sensor,   lambda x: ' %3d%%' % x),
        ('%s pkts' % self.sensor,   lambda x: ' %d' % x)
        ])

    def __str__(self):
        s = ''
        s += 'sensor = %s\n' % self.sensor
        s += 'packets/sec = %s\n' % self.packets_per_sec
        s += 'hours_ago = %s\n' % self.hours_ago
        s += 'expect_packet_count = %s\n' % self.expect_packet_count
        s += 'host = %s\n' % self.host
        s += 'min_pct = %s\n' % self.min_pct
        s += 'start = %s\n' % self.start
        s += 'stop  = %s\n' % self.stop
        if self.dataframe:
            s += 'dataframe...\n'
            s += self.dataframe.to_string(formatters=self.formatters, index=False)
        else:
            s += 'no dataframe (yet)'
        return s

    def _get_times(self):
        """Get start/stop times."""
        now = datetime.datetime.now()
        rnd = datetime.timedelta(minutes=now.minute % 60, seconds=now.second, microseconds=now.microsecond)
        stop = now - rnd + datetime.timedelta(hours=1)
        start = now - rnd - datetime.timedelta(hours=self.hours_ago)
        return  start, stop

    def _dataframe_query(self, every_sec=600):
        """count number of packets expected for hourly chunks""" 
        #query =  'SELECT FROM_UNIXTIME(time) as "hour", ' # <<< WORKED BEFORE mariadb
        #query =  'SELECT DATE_FORMAT(FROM_UNIXTIME(time), "%Y-%m-%d %T") as "hour", '
        query =  'SELECT DATE_FORMAT(FROM_UNIXTIME(time), "%Y-%m-%d %T") as "GMT", '
        #query += 'ROUND(100*COUNT(*)/8.0/3600.0) as "pct", '
        #query += 'COUNT(*) as "pkts" from %s ' % self.sensor
        #query += 'ROUND(100*COUNT(*)/8.0/3600.0) as "%s<br>%%", ' % self.sensor
        query += 'ROUND(100*COUNT(*)/%f/%d) as "%s<br>%%", ' % (self.packets_per_sec, every_sec, self.sensor)
        query += 'COUNT(*) as "%s<br>pkts" from %s ' % (self.sensor, self.sensor)
        query += 'WHERE FROM_UNIXTIME(time) BETWEEN "%s" ' % self.start.strftime('%Y-%m-%d %H:%M:%S')
        query += 'AND "%s" ' % self.stop.strftime('%Y-%m-%d %H:%M:%S')
        #query += "GROUP BY DATE_FORMAT(FROM_UNIXTIME(time), '%H') ORDER BY time;"
        query += "GROUP BY time DIV %d ORDER BY time;" % every_sec
        # SELECT DATE_FORMAT(FROM_UNIXTIME(time), "%Y-%m-%d %T") as "GMT", ROUND(100*COUNT(*)/8.000000/600.0) as "121f03<br>%", COUNT(*) as "121f03<br>pkts" from 121f03
        # WHERE FROM_UNIXTIME(time) BETWEEN "2017-08-29 14:00:00" AND "2017-08-30 13:00:00" GROUP BY time DIV 600 ORDER BY time;
        #print query
        con = mysql_con(host=self.host, db='pims')
        #self.dataframe = psql.frame_query(query, con=con) # <<< before pandas update
        self.dataframe = psql.read_sql(query, con=con)
        #if self.host in ['chef', 'tweek']: print self.dataframe # <<< debug
        
    def filt_min_pct(self):
        """if min_pct is non-zero, then return filtered dataframe"""
        if self.min_pct == 0:
            df_gaps = self.dataframe
        else:
            df_gaps = self.dataframe[self.dataframe['pct'] < self.min_pct]
        return df_gaps
    
    def filter(self, predicate):
        """return filtered dataframe"""
        pass

class DatabaseHourlyGapsStartStop(DatabaseHourlyGapsHoursAgo):
    """
    Info on database gaps given sensor (i.e. table), host, expected packets per second, min%, and start/stop.
    """
    def __init__(self, start, stop, sensor='121f03', host='tweek', packets_per_sec=8, min_pct=0):
        """Initialize."""
        self.start = parser.parse(start)
        self.stop = parser.parse(stop)
        self.sensor = sensor
        self.host = host
        self.packets_per_sec = packets_per_sec
        self.expect_packet_count = self.packets_per_sec * 3600.0 # count for one hour's worth          
        self.min_pct = min_pct
        self.dataframe = None
        # dataframe formatters (for db query to dataframe)
        self.formatters = dict([
        ('%s pct'  % self.sensor,   lambda x: ' %3d%%' % x),
        ('%s pkts' % self.sensor,   lambda x: ' %d' % x)
        ])

    def __str__(self):
        s = ''
        s += 'sensor = %s\n' % self.sensor
        s += 'packets/sec = %s\n' % self.packets_per_sec
        s += 'expect_packet_count = %s\n' % self.expect_packet_count
        s += 'host = %s\n' % self.host
        s += 'min_pct = %s\n' % self.min_pct
        s += 'start = %s\n' % self.start
        s += 'stop  = %s\n' % self.stop
        if self.dataframe:
            s += 'dataframe...\n'
            s += self.dataframe.to_string(formatters=self.formatters, index=False)
        else:
            s += 'no dataframe (yet)'
        return s

class CuDatabaseHourlyGapsStartStop(DatabaseHourlyGapsStartStop):
    """
    Info on cu_packet database gaps.
    """
    def __init__(self, start, stop, host='yoda', min_pct=0):
        """Initialize."""
        self.start, self.stop = self._get_times(start, stop)
        self.table = 'cu_packet'
        self.host = host
        self.packets_per_sec = 1
        self.expect_packet_count = self.packets_per_sec * 3600.0 # count for one hour's worth          
        self.min_pct = min_pct
        self.dataframe = None
        # dataframe formatters (for db query to dataframe)
        self.formatters = dict([
        ('%s pct'  % self.table,   lambda x: ' %3d%%' % x),
        ('%s pkts' % self.table,   lambda x: ' %d' % x)
        ])
    
    def _get_times(self, start, stop):
        return parser.parse(start), parser.parse(stop)
    
    def __str__(self):
        s = ''
        s += 'table = %s\n' % self.table
        s += 'packets/sec = %s\n' % self.packets_per_sec
        s += 'expect_packet_count = %s\n' % self.expect_packet_count
        s += 'host = %s\n' % self.host
        s += 'min_pct = %s\n' % self.min_pct
        s += 'start = %s\n' % self.start
        s += 'stop  = %s\n' % self.stop
        if self.dataframe:
            s += 'dataframe...\n'
            s += self.dataframe.to_string(formatters=self.formatters, index=False)
        else:
            s += 'no dataframe (yet)'
        return s        
        
    def _dataframe_query(self):
        """count number of packets expected for hourly chunks"""
        #query =  'SELECT timestamp as "hour", '
        query =  'SELECT timestamp as "GMT", '
        query += 'ROUND(100*COUNT(*)/1.0/3600.0) as "%s<br>%%", ' % self.table
        query += 'COUNT(*) as "%s<br>pkts" from %s ' % (self.table, self.table)       
        query += 'WHERE timestamp >= "%s" ' % self.start.strftime('%Y-%m-%d %H:%M:%S')
        query += 'AND timestamp < "%s" ' % self.stop.strftime('%Y-%m-%d %H:%M:%S')
        query += "GROUP BY DATE_FORMAT(timestamp, '%H') ORDER BY timestamp;"
        con = mysql_con_yoda(host=self.host, db='samsnew')
        #self.dataframe = psql.frame_query(query, con=con)
        self.dataframe = psql.read_sql(query, con=con)        

# function to format percentages
def percentage_fmt(x):
    """function to format percentages"""
    if x < 80:               s = '<span style="color: red">%g</span>' % x
    elif x >= 80 and x < 99: s = '<span style="color: blue">%g</span>' % x
    else:                    s = '%g' % x
    return s

# FIXME this time conversion does not work (see example in samsquery.py)
# function to format hourlies
def hourly_fmt(x):
    """function to format hourlies"""
    d = pd.to_datetime(x)
    #all_balls = d.minute == 0 and d.second == 0 and d.microsecond == 0
    #if all_balls: s = '%s' % x
    #else:         s = '<span style="color: red;">%s</span>' % x
    #return s
    r = floor_ten_minutes(d)
    return '%s' % r

def params_okay():
    """Not really checking for reasonableness of parameters entered on command line."""
    # check if sensorhosts not an input argument (list)
    if not isinstance(parameters['sensorhosts'], list):
        # first, split sensorhosts, each pairing separated by commas
        tmp = parameters['sensorhosts'].split(',')
        # next, split each pairing into tuple of (sensor, host)
        parameters['sensorhosts'] = [ tuple(i.split('_')) for i in tmp ]
    parameters['packets_per_sec'] = float(parameters['packets_per_sec'])
    parameters['min_pct'] = float(parameters['min_pct'])
    parameters['hours_ago'] = int(parameters['hours_ago'])
    if parameters['hours_ago'] > 23:
        parameters['hours_ago'] = 23
        print 'FIXME: currently MySQL GROUP BY mucks up queries longer than 23 hours ago'
        print 'CHANGED hours_ago PARAMETER TO MAX VALUE OF 23'
    return True

def print_usage():
    """Print short description of how to run the program."""
    print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def weekly_get_cu_packet_gaps():
    #df_merged = pd.DataFrame({'hour':[]})
    df_merged = pd.DataFrame({'GMT':[]})
    with open('/misc/yoda/www/plots/user/sams/dbsams.csv', 'r') as f:
        last_line = tail(f, 1)
    last_gmt = last_line[0].split(',')[0]
    dstart = parser.parse(last_gmt)
    #dstop = datetime.datetime.now().date()
    dstop = parser.parse('2015-03-01')
    d = dstart
    while d < dstop:
        d2 = d + datetime.timedelta(hours=1)
        # first, get all info on gaps
        dbgaps = CuDatabaseHourlyGapsStartStop(d.strftime('%Y-%m-%d %H:%M:%S'), d2.strftime('%Y-%m-%d %H:%M:%S'))
        dbgaps._dataframe_query()
        df_gaps = dbgaps.filt_min_pct()
        df_merged = pd.merge(df_merged, df_gaps, how='outer')
        d = d2
        print d
    with open('/misc/yoda/www/plots/user/sams/dbsams.csv', 'a') as f:
        df_merged.to_csv(f, index=False, header=False)


def pims_dbgaps():
    buf = StringIO()
    #df_merged = pd.DataFrame({'hour':[]})
    df_merged = pd.DataFrame({'GMT':[]})
    df_formatters = dict()
    the_list = [ tup for tup in parameters['sensorhosts'] if (tup[2] == 'pims') ]
    for sensor, host, db, pps in the_list:
        msg_preamble = '{:<20s}:'.format('%s, %s' % (sensor, host))
        #df_formatters['GMT'] = hourly_fmt
        df_formatters['%s<br>%%' % sensor] = percentage_fmt
        try:
            # first, get all info on gaps
            dbgaps = DatabaseHourlyGapsHoursAgo(
                sensor=sensor,
                host=host,
                packets_per_sec = float(pps), #parameters['packets_per_sec'],
                min_pct=parameters['min_pct'],
                hours_ago=parameters['hours_ago'],
                )
            dbgaps._dataframe_query()
            
            # FIXME to round down GMT to nearest ten-minute mark (GMT column appears to be a string at this point!?)
            # apply ten-minute round down to GMT column
            #dbgaps.dataframe['GMT'] = dbgaps.dataframe['GMT'].apply(FAKE_floor_ten_minutes)
            
            # filter using min_pct
            df_gaps = dbgaps.filt_min_pct()
            # get result into string
            #msg = df_gaps.to_string(formatters=dbgaps.formatters, index=False)
            df_merged = pd.merge(df_merged, df_gaps, how='outer')
            msg = '%s %02d hourly recs' % (msg_preamble, len(df_merged))
        except Exception as e:
            #msg = '%s Exception %s' % (msg_preamble, e[1])
            msg = '%s Exception %s' % (msg_preamble, e[0])

        #print msg or 'done'
        print msg
    
    #df_merged.sort_values(by=['hour'], inplace=True)
    #df_merged.sort_values(by=['hour'], inplace=True, ascending=False)
    df_merged.sort_values(by=['GMT'], inplace=True, ascending=False)
    df_merged.to_html(buf, formatters=df_formatters, escape=False, index=False, na_rep='nan')
    s = buf.getvalue()
    # s = s.replace('<tr>', '<tr style="text-align: right;">')
    # s = s.replace('<table border="1" class="dataframe">', '<table class="dataframe" id="fixed_hdr3">')
    with open("/misc/yoda/www/plots/user/sams/dbpims.html", "w") as html_file:
        html_file.write(HEADER + s.replace('nan', '') + FOOTER)
    #print df_merged
    return dbgaps.start, dbgaps.stop


def samsnew_dbgaps(d, d2):
    buf = StringIO()
    #df_merged = pd.DataFrame({'hour':[]})
    df_merged = pd.DataFrame({'GMT':[]})
    df_formatters = dict()
    the_list = [ tup for tup in parameters['sensorhosts'] if (tup[2] == 'samsnew') ]
    for sensor, host, db, pps in the_list:
        msg_preamble = '{:<20s}:'.format('%s, %s' % (sensor, host))
        df_formatters['%s<br>%%' % sensor] = percentage_fmt
        try:
            # first, get all info on gaps
            dbgaps = CuDatabaseHourlyGapsStartStop(d.strftime('%Y-%m-%d %H:%M:%S'), d2.strftime('%Y-%m-%d %H:%M:%S'))            
            dbgaps._dataframe_query()
            # filter using min_pct
            df_gaps = dbgaps.filt_min_pct()
            # get result into string
            #msg = df_gaps.to_string(formatters=dbgaps.formatters, index=False)
            df_merged = pd.merge(df_merged, df_gaps, how='outer')
            msg = '%s %02d hourly recs' % (msg_preamble, len(df_merged))
        except Exception as e:
            msg = '%s Exception %s' % (msg_preamble, e[1])

        #print msg or 'done'
        print msg
    
    #df_merged.sort(columns=['hour'], inplace=True, ascending=False)
    df_merged.sort_values(by=['GMT'], inplace=True, ascending=False)    
    df_merged.to_html(buf, formatters=df_formatters, escape=False, index=False, na_rep='nan')
    s = buf.getvalue()
    # s = s.replace('<tr>', '<tr style="text-align: right;">')
    # s = s.replace('dataframe', 'fixed_headers')
    with open("/misc/yoda/www/plots/user/sams/dbsams.html", "w") as html_file:
        hdr = HEADER.replace('PIMS Database Tables','SAMS Database Table')
        hdr = hdr.replace('dbsams', 'dbpims')
        html_file.write( hdr + s.replace('nan', '') + FOOTER )            
    #print df_merged    


def manbearpig_dbgaps(start, stop):
    buf = StringIO()
    #df_merged = pd.DataFrame({'hour':[]})
    df_merged = pd.DataFrame({'GMT':[]})
    df_formatters = dict()
    the_list = [ tup for tup in parameters['sensorhosts'] if (tup[2] == 'pims') ]
    for sensor, host, db, pps in the_list:
        host = 'manbearpig'
        msg_preamble = '{:<20s}:'.format('%s, %s' % (sensor, host))
        df_formatters['%s<br>%%' % sensor] = percentage_fmt
        try:
            # first, get all info on gaps
            dbgaps = DatabaseHourlyGapsStartStop(
                start, stop,
                sensor=sensor,
                host=host,
                packets_per_sec=parameters['packets_per_sec'],
                min_pct=parameters['min_pct'],
                )
            dbgaps._dataframe_query()
            # filter using min_pct
            df_gaps = dbgaps.filt_min_pct()
            # get result into string
            #msg = df_gaps.to_string(formatters=dbgaps.formatters, index=False)
            df_merged = pd.merge(df_merged, df_gaps, how='outer')
            msg = '%s %02d hourly recs' % (msg_preamble, len(df_merged))
        except Exception as e:
            msg = '%s Exception %s' % (msg_preamble, e[0])

        #print msg or 'done'
        print msg
    
    #df_merged.sort(columns=['hour'], inplace=True)
    df_merged.sort(columns=['GMT'], inplace=True)
    df_merged.to_html(buf, formatters=df_formatters, escape=False, index=False, na_rep='nan')
    s = buf.getvalue()
    s = s.replace('<tr>', '<tr style="text-align: right;">')
    with open("/misc/yoda/www/plots/user/sams/dbmanbearpig.html", "w") as html_file:
        html_file.write( HEADER + s.replace('nan', '') + FOOTER )            
    #print df_merged
    return dbgaps.start, dbgaps.stop


def main(argv):
    """script to simply check/show gaps in db"""
    if (len(argv) == 2) and (argv[1] == 'weekly'):
        weekly_get_cu_packet_gaps()
        return 0
    
    # parse command line
    for p in argv[1:]:
        pair = p.split('=')
        if 2 != len(pair):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if params_okay():
            start, stop = pims_dbgaps()
            samsnew_dbgaps(start, stop)
            return 0

    print_usage()  


if __name__ == '__main__':
    sys.exit(main(sys.argv))
