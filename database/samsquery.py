#!/usr/bin/env python

import re
import subprocess
import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser
import pandas as pd
from cStringIO import StringIO
import socket
from pims.config.conf import get_config
from pims.utils.datetime_ranger import DateRange

def get_samsops_db_params(app_name):
    cfg = get_config()
    config_dict = cfg['apps'][app_name]
    host = config_dict['host']
    schema = config_dict['schema']
    uname = config_dict['uname']
    pword = config_dict['pword']
    return host, schema, uname, pword    
    
# Get sensitive authentication credentials for internal MySQL db query
_HOST, _SCHEMA, _UNAME, _PASSWD = get_samsops_db_params('samsquery')

#print _HOST, _SCHEMA; raise SystemExit

def get_cronjob():
    cmd = 'crontab -l | grep samsquery.py'
    p = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    results, err = p.communicate()
    return results.split('#')[1] # just return the comment

class EeStatusQuery(object):
    """workaround query for updating web page with EE status"""

    def __init__(self, host, schema, uname, pword):
        self.host = host
        self.schema = schema
        self.uname = uname
        self.pword = pword
        self.query = self._get_query()

    def __str__(self):
        results = self.run_query()
        return results

    def _get_query(self):
        query = 'SELECT * FROM samsnew.ee_packet ORDER BY timestamp DESC LIMIT 55;'
        return query

    def run_query(self):
        cmdQuery = 'mysql -h %s -D %s -u %s -p%s --execute="%s"' % (self.host, self.schema, self.uname, self.pword, self.query)
        p = subprocess.Popen([cmdQuery], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        results, err = p.communicate()
        return results

# FIXME this was abandoned for quicker, manual build of queries shown in comments below
class SamsopsBak(object):
    """workaround query for updating web page with EE status"""

    def __init__(self, table, tfield, pword, fmt='%Y-%m-%d'):
        self.host = 'yoda'
        self.uname = 'root'
        self.pword = pword
        self.table = table
        self.tfield = tfield
        self.format = fmt

    def _get_query(self, schema, start, stop):
        query = "SELECT count(*) FROM %s.%s WHERE %s >= '%s' AND %s < '%s';" % (schema, self.table, self.tfield, start, self.tfield, stop)
        return query

    def run_query(self, schema, start, stop):
        query = self._get_query(schema, start, stop)
        cmdQuery = 'mysql -h %s -u %s -p%s --skip-column-names --execute="%s"' % (self.host, self.uname, self.pword, query)
        #print cmdQuery
        p = subprocess.Popen([cmdQuery], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        results, err = p.communicate()
        return results

    def my_method(self):
        d1 = datetime.date(2000, 1, 1)
        d2 = datetime.date(2013, 8, 6)
        date_range = DateRange(d1, d2)
        d = d1
        while d <= date_range.stop:
            next_year = d + relativedelta(years=1)
            print d, "<= d <", next_year
            d += relativedelta(years=1)

SAMSOPS_BAK = {
    'EE_Packet'                        :'timestamp',
    'GSE_EMBEDDED_EE_Health_Status'    :'TISS_time_value',
    'GSE_ER_Health_Status'             :'TISS_time',
    'GSE_MSG_Health_Status'            :'TISS_time',
    'GSE_SAMS_ICU_Health_Status'       :'TISS_time',
    'GSE_SAMS_RTS_Health_Status'       :'TISS_time',
    'ICU_Packet'                       :'timestamp',
    'ICU_messages'                     :'date',
    'tshes_house_packet'               :'timestamp',
    'command_receipt_log'              :'Timestamp',
    'tshes_command_receipt_log'        :'Timestamp'
}

def show_query(tname, field, date_range):
    fmt = '%Y-%m-%d'
    d = date_range.start
    while d <= date_range.stop:
        next_year = d + relativedelta(years=1)
        t1 = d.strftime(fmt)
        t2 = next_year.strftime(fmt)
        y1 = d.strftime('%Y')
        #print "INSERT INTO table_subdiv_recs (tname, start, stop, count) SELECT '%s' as tname, '%s' as start, '%s' as stop, (SELECT count(*) FROM %s WHERE %s >= '%s' AND %s < '%s') as count;" % (tname, t1, t2, tname, field, t1, field, t2)
        print "INSERT INTO samsops_bak_%s.%s SELECT * FROM samsops_bak.%s WHERE %s >= '%s' AND %s < '%s';" % (y1, tname, tname, field, t1, field, t2)
        d += relativedelta(years=1)

def compare_samsops_bak(pword, d1, d2):
    fmt = '%Y-%m-%d'
    date_range = DateRange(d1, d2)
    for tname, field in SAMSOPS_BAK.iteritems():
        d = date_range.start
        while d <= date_range.stop:
            next_year = d + relativedelta(years=1)
            t1 = d.strftime(fmt)
            t2 = next_year.strftime(fmt)
            y1 = d.strftime('%Y')
            sob = SamsopsBak(tname, field, pword)
            schema = 'samsops_bak_' + y1
            #print sob._get_query(schema, d, next_year)
            num1 = int( sob.run_query('samsops_bak', d, next_year).rstrip() )
            num2 = int( sob.run_query(schema, d, next_year).rstrip() )
            print '%s, year %s, diff = %d, count1 = %d, count2 = %d' % (tname, y1, num1-num2, num1, num2)
            d += relativedelta(years=1)

#pword = raw_input("Enter yoda db passwd: ")
#d1 = datetime.date(2000, 1, 1)
#d2 = datetime.date(2000, 12, 31)
#d3 = datetime.date(2009, 1, 1)
#d4 = datetime.date(2013, 8, 6)
#compare_samsops_bak(pword, d1, d2)
#compare_samsops_bak(pword, d3, d4)
#raise SystemExit

class CuStatusQuery(EeStatusQuery):
    """workaround query for updating web page with CU status"""

    def _get_query(self):
        #query = 'SELECT * FROM samsnew.cu_packet_rt;' # does not work, but why?
        query = 'SELECT * FROM samsnew.cu_packet ORDER BY timestamp DESC LIMIT 11;'
        return query

class CuMonthlyQuery(EeStatusQuery):
    """monthly query for updating kpi wth CU status"""

    def __init__(self, host, schema, uname, pword, d1, d2):
        self.host = host
        self.schema = schema
        self.uname = uname
        self.pword = pword
        self.query = self._get_query(d1, d2)

    def _get_query(self, d1, d2):
        fmt = '%Y-%m-%d'
        query = "SELECT DATE(timestamp) as Date, count(*)/3600.0 as sams_cu_hours FROM cu_packet"
        query += " WHERE timestamp >= '%s' AND timestamp <= '%s' GROUP BY Date;"  % (
                                                                        d1.strftime(fmt),
                                                                        d2.strftime(fmt))
        return query

class OldGseStatusQuery(EeStatusQuery):
    """workaround query for updating web page with GSE status"""

    def _get_query(self):
        query = 'SELECT * FROM samsnew.gse_packet_rt;' # ORDER BY ku_timestamp DESC LIMIT 11;'
        return query

class GseStatusQuery(EeStatusQuery):
    """workaround query for updating web page with GSE status"""

    def _get_query(self):
        fivemin_agostr = (datetime.datetime.now() - relativedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        query = "SELECT ku_timestamp, sams_cu_hs_counter FROM samsnew.gse_packet WHERE ku_timestamp >= '%s' ORDER BY ku_timestamp DESC LIMIT 5;" % fivemin_agostr
        return query

class SimpleQueryAOS(object):
    """simple query for AOS/LOS"""
    def __init__(self, host, schema, uname, pword):
        self.host = host
        self.schema = schema
        self.uname = uname
        self.pword = pword
        self.query = self._get_query()
        self.run_query()

    def _get_query(self):
        #query = 'select GSE_tiss_time , IF(GSE_aos_los =0, \\"LOS\\",\\"AOS\\") as aos_los from RT_ICU_gse_data;'
        query = 'select ku_timestamp , IF(ku_aos_los_status=0, \\"LOS\\",\\"AOS\\") as aos_los from gse_packet_rt;'
        return query

    def __str__(self):
        self.run_query()
        return '%s,%s' % (self.gse_tiss_dtm, self.aos_los)

    def get_aos_tisstime(self):
        self.run_query()
        return self.aos_los, self.gse_tiss_dtm

    def run_query(self):
        cmdQuery = 'mysql --skip-column-names -h %s -D %s -u %s -p%s --execute="%s"' % (self.host, self.schema, self.uname, self.pword, self.query)
        p = subprocess.Popen([cmdQuery], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        results, err = p.communicate()
        search_pat = re.compile('(.*)\t([AL]OS)').search
        m = search_pat(results)
        gse_tiss_time, aos_los = m.group(1,2)
        self.header = 'class, gse_tiss_dtm, aos_los'
        self.gse_tiss_dtm = parser.parse(gse_tiss_time)
        self.aos_los = aos_los

def get_raw_dataframe(results):
    s = StringIO()
    header = results[0]
    s.write(header)
    for result in results[1:]:
        s.write(result)
    s.seek(0) # "rewind" to the beginning of the StringIO object
    df = pd.read_csv( s, sep='\t' )
    return df

def get_processed_dataframe(params):
    # get db query results
    db_results = params['query_class'](_HOST, _SCHEMA, _UNAME, _PASSWD).run_query()
    
    # use db results to get raw dataframe
    df = get_raw_dataframe(db_results)
    
    # drop unwanted columns from dataframe
    for uc in params['unwanted_columns']:
        df = df.drop(uc, 1)
    
    # do some sorting (usually time desc)
    df_sorted = df.sort(params['sort_columns'], ascending=params['sort_flags'])
    df = df_sorted.groupby(params['group_column']).first().reset_index()
    
    # if needed, then do "trailing drop" too
    if params['trailing_drop_columns']:
        df = df.drop(params['trailing_drop_columns'], 1)
    #print df
    return df

# Define dictionary to hold info for getting, processing, and formatting web page output
GSE = {
    'query_class'           : GseStatusQuery,
    'unwanted_columns'      : [ 'sband_timestamp', 's_aos_los_status', 'sams_cu_cpu_temp',
                                'sams_cu_case_max_temp', 'sams_cu_case_min_temp', 'sams_cu_gpu_temp',
                                'sams_cu_hs_counter', 'msg_outlet2_current', 'msg_outlet2_status',
                                'msg_plus28V_outlet1', 'msg_plus28V_outlet1_status', 'msg_plus28V_outlet2',
                                'msg_plus28V_outlet2_status', 'msg_wv_air_temp'],
    'sort_columns'          : ['ku_timestamp'],
    'sort_flags'            : [False],
    'group_column'          : 'sams_cu_identity',
    'trailing_drop_columns' : ['sams_cu_identity'],
    'caption'               : 'GSE',
    'formatters'            : {'sams_cu_ecw':lambda x: "%d" % x}
}

CU = {
    'query_class'           : CuStatusQuery,
    'unwanted_columns'      : [ 'ram_total', 'swap_total', 'hdd_total', 'fan_speed',
                                'ram_used', 'swap_used', 'hdd_used',
                                'case_temp0', 'case_temp1', 'case_temp2',
                                'case_temp3', 'case_temp4', 'case_temp5',
                                'case_temp6', 'case_temp7', 'case_temp8'],
    'sort_columns'          : ['cu_id', 'timestamp'],
    'sort_flags'            : [True,    False],
    'group_column'          : 'cu_id',
    'trailing_drop_columns' : None,
    'caption'               : 'Control Unit (CU)',
    'formatters'            : {'cu_id':lambda x: "%9s" % x[-3:].replace('-', ' ')}
}

EE = {
    'query_class'           : EeStatusQuery,
    'unwanted_columns'      : [ 'se_id_head0', 'se_id_head1', 'time_in_sec',
                                'head0_tempX', 'head0_tempY', 'head0_tempZ',
                                'head1_tempX', 'head1_tempY', 'head1_tempZ'],
    'sort_columns'          : ['ee_id', 'timestamp'],
    'sort_flags'            : [True,    False],
    'group_column'          : 'ee_id',
    'trailing_drop_columns' : None,
    'caption'               : 'Electronics Enclosures (EEs)',
    'formatters'            : {'ee_id':lambda x: "%9s" % x[-3:].replace('-', ' ')}
}

# Workaround for db table where Dump2 is clobbering RealTime
def workaroundRTtable(htmlFile):
    """Workaround for db table where Dump2 is clobbering RealTime"""

    HEADER = '''<!DOCTYPE html>
        <html>
                <head>
                    <meta http-equiv="refresh" content="60">
                    <title>SAMS H&S</title>
                <style>
                
                        updatetag
                        {
                        font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
                        color:black;
                        text-align:left;
                        font-size: 0.83em;                        
                        }

                        hosttag
                        {
                        font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
                        color:gray;
                        text-align:left;
                        font-size: 0.75em;                        
                        }
                        
                        titletag
                        {
                        font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
                        color:black;
                        font-weight: bold;
                        font-size: 1.25em;                        
                        text-align:left;
                        }

                        captiontag
                        {
                        font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
                        color:black;
                        font-weight: bold;
                        font-size: 1.1em;                        
                        text-align:left;
                        }

                .df tbody tr:nth-child(even) {background: #CCC} tr:nth-child(odd) {background: #FFF}
                        .df
                        {
                        font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
                        width:100%;
                        border-collapse:collapse;
                        }
                        .df td, .df th 
                        {
                        font-size:0.9em;
                        border:1px solid #123456;
                        padding:3px 7px 2px 7px;
                        }
                        .df th 
                        {
                        font-size:1.0em;
                        text-align:left;
                        padding-top:5px;
                        padding-bottom:4px;
                        background-color:black;
                        border:1px solid #FFFFFF;
                        color:#ffffff;
                        }
                    </style>
                </head>
                <body>
            <titletag>SAMS Health and Status</titletag><br>
            '''
    HEADER += '<updatetag>updated at GMT %s</updatetag><br>' % str(datetime.datetime.now())[0:-7]
    HEADER += '<hosttag>host: %s (%s)</hosttag><br><br>' % (socket.gethostname(), get_cronjob())
    FOOTER = '''
        </body>
    </html>
    '''

    # write html to string
    s = ''
    s += HEADER
    
    # write each table type
    for d in [GSE, CU, EE]:
        df = get_processed_dataframe(d)
        s += '<captiontag>%s</captiontag>' % d['caption']
        s += df.to_html(classes='df', formatters=d['formatters'], index=False)
        s += '<br><br>'

    # write footer
    s += FOOTER
    
    # finally write the entire string to file
    fo = open(htmlFile, 'w')
    fo.write(s);
    fo.close()    
        
def demo():
    #right_now = (datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    #print '%s is GMT now' % right_now
    aos = SimpleQueryAOS(_HOST, _SCHEMA, _UNAME, _PASSWD)
    print aos
    gse = GseStatusQuery(_HOST, _SCHEMA, _UNAME, _PASSWD)
    gse_results = gse.run_query()
    if len(gse_results) == 0:
        print '\nNO RESULTS from following query:'
        print gse.query
    else:
        print '\nFive recent GSE packet records'
        print  '------------------------------'
        print gse_results

#demo()
#raise SystemExit

def demo3():
    df = pd.DataFrame({'correlation':[0.5, 0.1,0.9], 'p_value':[0.1,0.8,0.01]})
    df.to_html('/tmp/trash3.html',
               formatters={
                'p_value':lambda x: "*%f*" % x if x<0.05 else str(x),
                'correlation':lambda x: "%3.1f" % x
                })

# function to format percentages
def percentage_fmt(x):
    """function to format percentages"""
    if x < 50:               s = '<span style="color: red">%.1f</span>' % x
    elif x >= 50 and x < 75: s = '<span style="color: blue;">%.1f</span>' % x
    else:                    s = '%.1f' % x
    return s

# function to format hourlies
def hourly_fmt(x):
    """function to format hourlies"""
    d = pd.to_datetime(x)
    all_balls = d.minute == 0 and d.second == 0 and d.microsecond == 0
    if all_balls: s = '%s' % x
    else:         s = '<span style="color: red;">%s</span>' % x
    return s

def demo_conditional_cell_formatting():
    buf = StringIO()
    
    sensor = '121f04'
    df1 = pd.DataFrame(
        {'hour':[
        '2014-08-30 01:23:45.123',
        '2014-08-30 02:23:45.123',
        '2014-08-30 03:00:00.000',
        '2014-08-30 03:00:00.123',
        '2014-08-30 01:23:45.123'],
        'pct':  [0,        25,    50,    75,   100],
        'pkts': [28800, 28799, 12000, 28800, 24123]})
    df1.rename(columns={'pct': sensor + '<br>%', 'pkts': sensor + '<br>pkts'}, inplace=True)
    
    sensor = '121f02'
    df2 = pd.DataFrame(
        {'hour':[
        '2014-08-30 01:23:45.123',
        '2014-08-30 03:00:00.000',
        '2014-08-30 04:00:00.000'],
        'pct':  [   11,     22,     99],
        'pkts': [28800,  28800,  24123]})
    df2.rename(columns={'pct': sensor + '<br>%', 'pkts': sensor + '<br>pkts'}, inplace=True)
    
    sensor = '121f03'
    df3 = pd.DataFrame(
        {'hour':[
        '2014-08-30 01:23:45.123',
        '2014-08-30 03:00:00.000',
        '2014-08-30 04:00:00.000'],
        'pct':  [0,        25,    50],
        'pkts': [28800, 28800, 24123]})
    df3.rename(columns={'pct': sensor + '<br>%', 'pkts': sensor + '<br>pkts'}, inplace=True)
    
    sensor = '121f05'
    df4 = pd.DataFrame(
        {'hour':[
        '2014-08-30 01:23:59.123',
        '2014-08-30 02:00:00.000',
        '2014-08-30 04:00:00.000'],
        'pct':  [0,        25,    50],
        'pkts': [28800, 28800, 24123]})
    df4.rename(columns={'pct': sensor + '<br>%', 'pkts': sensor + '<br>pkts'}, inplace=True)
    
    df_merged = pd.merge(df1, df2, how='outer')
    for df in [df3, df4]:
        df_merged = pd.merge(df_merged, df, how='outer')
    df_merged.sort(columns=['hour'], inplace=True)
    
    df_merged.to_html(buf, formatters={
        'hour': hourly_fmt,
        '121f04<br>%': percentage_fmt,
        '121f04<br>%': percentage_fmt,
        }, escape=False, index=False, na_rep='nan')
    s = buf.getvalue()
    with open("/tmp/trash4.html", "w") as html_file:
        html_file.write( s.replace('nan', '') )

if __name__ == "__main__":
    workaroundRTtable('/misc/yoda/www/plots/user/sams/eetemp.html')    
