#!/usr/bin/env python
version = '$Id$'

import os
import sys
import socket
import datetime
from pims.database.pimsquery import db_connect, mysql_con
import pandas.io.sql as psql
import pandas as pd
import MySQLdb
from cStringIO import StringIO

# TODO
# - robustness for missing table (or go out and find hosts/tables automagically)
# - iterate over list of sensors
# - better way to get expected packets per second (SAMS/MAMS HiRAP, SampleRate, what else)
# - some form of pivot table to show results
# - allow more than 23 hours of history (the GROUP BY in MySQL call mucks this up othewise)

#### input parameters
###defaults = {
###'sensor':           '121f03',       # sensor = table name
###'packets_per_sec':  '8',            # expected value for this sensor for this gap check period
###'host':             'tweek',        # like tweek for 121f03
###'min_pct':          '0',            # show hourly periods with pkt count < min_pct (USE ZERO TO SHOW ALL)
###'hours_ago':        '23',           # start checking this many hours ago
###}

# defaults
defaults = {
'sensorhosts': [
    ('121f02',  'kenny'),
    ('121f03',  'tweek'),
    ('121f04',  'mr-hankey'),
    ('121f05',  'chef'),
    ('121f08',  'timmeh'),
    ('es03',    'manbearpig'),
    ('es05',    'ike'),
    ('es06',    'butters')
    ],          
'packets_per_sec':  '8',    # expected value for this sensor for this gap check period
'min_pct':          '0',    # show hourly periods with pkt count < min_pct (USE ZERO TO SHOW ALL)
'hours_ago':        '18',   # start checking this many hours ago
}
parameters = defaults.copy()

class DatabaseGaps(object):
    """
    Info on database gaps given sensor (i.e. table), host, and expected packets per second.
    """
    def __init__(self, sensor='121f03', host='tweek', packets_per_sec=8, hours_ago=23, min_pct=0):
        """Initialize."""
        self.sensor = sensor
        self.host = host
        self.packets_per_sec = packets_per_sec
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
        s += 'stop  = %s' % self.stop
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

    def _dataframe_query(self):
        """count number of packets expected for hourly chunks""" 
        query =  'SELECT FROM_UNIXTIME(time) as "hour", '
        #query += 'ROUND(100*COUNT(*)/8.0/3600.0) as "pct", '
        #query += 'COUNT(*) as "pkts" from %s ' % self.sensor
        query += 'ROUND(100*COUNT(*)/8.0/3600.0) as "%s<br>%%", ' % self.sensor
        query += 'COUNT(*) as "%s<br>pkts" from %s ' % (self.sensor, self.sensor)
        query += 'WHERE FROM_UNIXTIME(time) >= "%s" ' % self.start.strftime('%Y-%m-%d %H:%M:%S')
        query += 'AND FROM_UNIXTIME(time) < "%s" ' % self.stop.strftime('%Y-%m-%d %H:%M:%S')
        query += "GROUP BY DATE_FORMAT(FROM_UNIXTIME(time), '%H') ORDER BY time;"
        #print query
        con = mysql_con(host=self.host, db='pims')
        self.dataframe = psql.frame_query(query, con=con)
        
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

# function to format percentages
def percentage_fmt(x):
    """function to format percentages"""
    if x < 50:               s = '<span style="color: red">%.1f</span>' % x
    elif x >= 50 and x < 95: s = '<span style="color: blue;">%.1f</span>' % x
    else:                    s = '%.1f' % x
    return s

# FIXME this time conversion does not work (see example in samsquery.py)
# function to format hourlies
def hourly_fmt(x):
    """function to format hourlies"""
    d = pd.to_datetime(x)
    all_balls = d.minute == 0 and d.second == 0 and d.microsecond == 0
    if all_balls: s = '%s' % x
    else:         s = '<span style="color: red;">%s</span>' % x
    return s

"""NOTE THIS GREEN COMMENT PART IS SNIPPET OF POSSIBLY IMPROVED TABLE HEADER ROW
<SNIP>
}
.df tbody tr:nth-child(even) {background: #CCC} tr:nth-child(odd) {background: #FFF}
</style>
</head>
<body>
<titletag>PIMS Database Tables</titletag><br>
<updatetag>updated at GMT 2014-09-06 10:11:03</updatetag><br>
<hosttag>host: jimmy</hosttag><br>
<br>
<table class="dataframe df" border="1">
<thead> <tr>
<th><toprow>LAB/RACK</toprow></th>
<th colspan="2"><toprow>COL/ER3</toprow></th>
<th colspan="2"><toprow>USL/ER2</toprow></th>
<th colspan="2"><toprow>USL/ER1</toprow></th>
<th colspan="2"><toprow>JEM/ER4</toprow></th>
<th colspan="2"><toprow>COL/ER3</toprow></th>
<th colspan="2"><toprow>USL/FIR</toprow></th>
</tr>
<tr>
<th>hour</th>
<th><dbhosttag>kenny</dbhosttag><br>121f02<br>
~data%</th>
<th><dbhosttag>kenny</dbhosttag><br>121f02<br>
#pkts</th>
<th><dbhosttag>tweek</dbhosttag><br>121f03<br>
~data%</th>
<th><dbhosttag>tweek</dbhosttag><br>121f03<br>
#pkts</th>
<th><dbhosttag>mr-hankey</dbhosttag><br>121f04<br>
~data%</th>
<th><dbhosttag>mr-hankey</dbhosttag><br>121f04<br>
#pkts</th>
<th><dbhosttag>chef</dbhosttag><br>121f05<br>
~data%</th>
<th><dbhosttag>chef</dbhosttag><br>121f05<br>
#pkts</th>
<th><dbhosttag>timmeh</dbhosttag><br>121f08<br>
~data%</th>
<th><dbhosttag>timmeh</dbhosttag><br>121f08<br>
#pkts</th>
<th><dbhosttag>manbearpig</dbhosttag><br>es06<br>
~data%</th>
<th><dbhosttag>manbearpig</dbhosttag><br>es06<br>
#pkts</th>
</tr>
</thead> <tbody>
<SNIP>
"""

HEADER = '''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="600">
<title>PIMS db</title>
<style>
updatetag {
text-align: left;
color: black;
font-size: 0.83em;
font-family: Verdana,Geneva,sans-serif;
}
dbhosttag {
font-size: 0.55em;
text-align: right;
font-family: Verdana,Geneva,sans-serif;
color: gray;
}
hosttag {
font-size: 0.75em;
text-align: left;
font-family: Verdana,Geneva,sans-serif;
color: gray;
}
titletag {
font-size: 1.25em;
font-weight: bold;
font-family: Verdana,Geneva,sans-serif;
color: black;
text-align: left;
text-decoration: underline;
}
captiontag {
font-size: 1.1em;
font-weight: bold;
font-family: Verdana,Geneva,sans-serif;
color: black;
text-align: left;
}
toprow {
background-color: black;
font-size: 0.729em;
color: orange;
}
.df {
width: 100%;
font-family: Verdana,Geneva,sans-serif;
border-collapse: collapse;
}
.df td, .df th {
border: 1px solid #123456;
padding: 3px 7px 2px;
font-size: 0.99em;
}
.df th {
border: 1px solid #ffffff;
background-color: black;
font-size: 1.1em;
vertical-align: bottom;
padding-bottom: 5px;
padding-top: 5px;
color: #ffffff;
}
.df tbody tr:nth-child(even) {background: #CCC} tr:nth-child(odd) {background: #FFF}
</style>
</head>
<body>
<titletag>PIMS Database Tables</titletag><br>
        '''
FOOTER = '<updatetag>updated at GMT %s</updatetag><br>' % str(datetime.datetime.now())[0:-7]
FOOTER += '<hosttag>host: %s</hosttag><br><br>' % socket.gethostname()
FOOTER += '''
    </body>
</html>
'''

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
    
def main(argv):
    """script to simply check/show gaps in db"""
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if params_okay():

            buf = StringIO()
            df_merged = pd.DataFrame({'hour':[]})
            df_formatters = dict()
            for sensor, host in parameters['sensorhosts']:
                msg_preamble = '{:<20s}:'.format('%s, %s' % (sensor, host))
                df_formatters['%s<br>%%' % sensor] = percentage_fmt
                try:
                    # first, get all info on gaps
                    dbgaps = DatabaseGaps(
                        sensor=sensor,
                        host=host,
                        packets_per_sec=parameters['packets_per_sec'],
                        min_pct=parameters['min_pct'],
                        hours_ago=parameters['hours_ago'],
                        )
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
            
            df_merged.sort(columns=['hour'], inplace=True)
            df_merged.to_html(buf, formatters=df_formatters, escape=False, index=False, na_rep='nan')
            s = buf.getvalue()
            s = s.replace('<tr>', '<tr style="text-align: right;">')
            with open("/misc/yoda/www/plots/user/sams/dbpims.html", "w") as html_file:
                html_file.write( HEADER + s.replace('nan', '') + FOOTER )            
            #print df_merged
            
            return 0

    print_usage()  

if __name__ == '__main__':
    sys.exit(main(sys.argv))
