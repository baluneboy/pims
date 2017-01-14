#!/usr/bin/env python

import re
import sys
import datetime
from cStringIO import StringIO
import pandas as pd
from bs4 import BeautifulSoup, Tag
from pims.patterns.dbstatuspats import _DBSTATUSLINE_PATTERN


# max age (seconds) of packet max time; otherwise, turn red
_MAX_AGE_SEC = 1 * 60 * 60 # try 1 hour for now


# table names (i.e. sensors) to ignore that otherwise get displayed with dbstatus.py
_IGNORE_SENSORS = ['121f08badtime', '121f08goodtime', 'Abias',
            'Abiasavg', 'Bbias', 'Bbiasavg', 'besttmf', 'Cbias', 'Cbiasavg',
            'cmg', 'finalbias_combine', 'gse', 'hirap_bogus', 'housek',
            'mcor_121f03', 'mcor_hirap', 'mcor_oss', 'pbesttmf', 'poss',
            'powerup', 'radgse', 'sec_hirap', 'sec_oss', 'soss', 'soss',
            'textm', 'emptytable'
            ] 


# HTML header
_HEADER = """<HEAD>
<META HTTP-EQUIV=Refresh CONTENT='300'>
</HEAD>
<HTML>
<BODY BGCOLOR=#FFFFFF TEXT=#000000 LINK=#0000FF VLINK=#800040 ALINK=#800040>
<TITLE>Active Sensors</TITLE>
<CENTER>
<B>This page will automatically refresh every 5 minutes.</B><BR>
<B>Last refreshed GMT %s<B><BR>
<a href="http://pims.grc.nasa.gov/plots/user/sams/samsresources.html">SAMS Resources</a><BR><BR>
<link rel="stylesheet" type="text/css" href="active_sensors.css" media="screen"/>
""" % datetime.datetime.now().strftime('%d-%b-%Y, %j/%H:%M:%S ')


# HTML footer
_FOOTER = """<BR>
</CENTER>
</BODY>
</HTML>
"""


# function to format location
def loc_fmt(s):
    """function to format location"""
    return s.replace(';', ',')


# function to format age
def age_fmt(x):
    """function to format age"""

    if x > _MAX_AGE_SEC: s = '<span style="color: red">%d' % x
    else:                s = '%d' % x
    return s


# function to format DOY GMT
def doy_fmt(x):
    """function to format DOY GMT"""

    d = pd.to_datetime(x)
    delta = datetime.datetime.now() - d
    deltasec = delta.total_seconds()
    if deltasec <= _MAX_AGE_SEC:
        s = '%s' % d.strftime('%j/%H:%M:%S ')
    else:
        s = '<span style="color: red">%s' % d.strftime('%j/%H:%M:%S ')
    return s


# return dataframe converted from stdin (file) object
def stdin_to_dataframe():
    """return dataframe converted from stdin (file) object"""

    buf = StringIO()
    buf.write('Host,Sensor,PktCount,FirstPkt,LastPkt,AgeSec,Rate,Location\n')
    got_topline = False
    # sys.stdin is a file object, so all the same functions that
    # can be applied to a file object can be applied to sys.stdin    
    for line in sys.stdin.readlines():
        if got_topline:
            line = line.replace(',', ';')
            m = re.match(_DBSTATUSLINE_PATTERN, line)
            if m:
                buf.write( '%s,%s,%s,%s,%s,%s,%s,%s\n' % (
                    m.group('Host'), m.group('Sensor'), m.group('PktCount'),
                    m.group('FirstPkt'), m.group('LastPkt'), m.group('AgeSec'), m.group('Rate'), m.group('Location')) )
            else:
                buf.write( 'no match\n' )        
        if re.match('.*COMPUTER.*', line):
            line = line.replace('_', ' ')
            line = line.replace('-', ' ')
            got_topline = True
    
     # "rewind" to the beginning of the StringIO object
    buf.seek(0)
    
    # read buf StringIO object as CSV into dataframe
    df = pd.read_csv(buf)

    # replace min/max times that are either zero or "None" with '1970-01-01 00:00:00'
    dict_replace = {'^0$': '1970-01-01 00:00:00', 'None': '1970-01-01 00:00:00'}
    df.replace(to_replace={'FirstPkt': dict_replace, 'LastPkt': dict_replace}, inplace=True)
    
    return df

    
# css implementation for improved (colorized) html converted from dataframe to stdout
def active_sensors_css_html(df, which):
    """css implementation for improved (colorized) html converted from dataframe to stdout"""

    buf_html = StringIO()
    df.to_html(buf_html, formatters={
        'LastPkt': doy_fmt,
        'Age(sec)': age_fmt,
        'Location': loc_fmt},
        escape=False, index=False, na_rep='nan')
    s = buf_html.getvalue()
    
    # turn string into bs
    soup = BeautifulSoup(s)
    
    # get the one and only table here
    tables = soup.find_all('table')
    if len(tables) != 1:
        raise Exception('expected one and only one table here')
    table = tables[0]
    
    # modify class and border on this table
    table.attrs['class'] = which
    table.attrs['border'] = 3
    headings = table.find_all('th')

    # modify 6 column headings attrs for our css formatting
    headings[0].attrs['class'] = 'column-1 column-location'
    headings[1].attrs['class'] = 'column-2 column-two'
    headings[2].attrs['class'] = 'column-3 column-lastpkt'
    headings[3].attrs['class'] = 'column-4 column-age'
    headings[4].attrs['class'] = 'column-5 column-rate'
    headings[5].attrs['class'] = 'column-6 column-host'

    # format first 2 columns of all table rows
    all_rows = soup.find_all('tr')
    for row in all_rows:
        cells = row.find_all(['th','td'])
        cells[0].attrs['style'] = 'text-align: right'
        cells[1].attrs['style'] = 'text-align: center'

    # return stirred soup :)
    return str(soup)


# filter dataframe to get rid of non-interesting sensors (sensors are really just table names)
def filter_active_sensors(df):
    """filter dataframe to get rid of non-interesting sensors (sensors are really just table names)"""
    
    # get rid of some sensor (rows)
    df = df[~df['Sensor'].isin(_IGNORE_SENSORS)]
    
    # sort
    df.sort(columns='LastPkt', axis=0, ascending=False, inplace=True)
    
    # clarify rate
    df.rename(columns={'Rate': 'Rate(sa/sec)', 'AgeSec': 'Age(sec)'}, inplace=True)    
    
    # order the columns
    df = df[['Location', 'Sensor', 'LastPkt', 'FirstPkt', 'Age(sec)', 'Rate(sa/sec)', 'PktCount', 'Host']]
    return df


# drop unwanted columns from dataframe
def drop_unwanted_columns(df):
    """drop unwanted columns from dataframe"""
    
    unwanted_columns = [ 'FirstPkt', 'PktCount' ]
    for uc in unwanted_columns:
        df = df.drop(uc, 1)    
    return df


def keep_only(df, str_contains):
    """keep only rows that have Sensor designations per str_contains"""
    
    df = df[df['Sensor'].str.contains(str_contains)]
    
    # sort by sensor (not by GMT LastPkt)
    df.sort(columns='Sensor', axis=0, ascending=True, inplace=True)    
    
    return df


def drop_MAMS(df):
    """drop rows that have Sensor designations (oss or hirap)"""
    
    df = df[~df['Sensor'].str.contains('oss|hirap')]    
    return df


def drop_EE(df):
    """drop rows that have EE designations (122f0*); ALREADY SORTED BY LastPkt GMT"""
    
    df_not_ee = df[~df['Sensor'].str.contains('^122f0')]
    df_sams = drop_MAMS(df_not_ee)

    # sort by sensor (not by GMT LastPkt)
    df_sams.sort(columns='Sensor', axis=0, ascending=True, inplace=True)
    
    df_mams = keep_only(df_not_ee, 'oss|hirap')
    
    # change column name
    df_mams = df_mams.rename(columns = {'Location': 'MAMS Location'})    
    df_sams = df_sams.rename(columns = {'Location': 'SAMS SE Location'})    
    
    return df_sams, df_mams

    
# USAGE EXAMPLE: dbstatus.py | dbstatushtml.py > /tmp/trash2.html
if __name__ == "__main__":
    """USAGE EXAMPLE: dbstatus.py | dbstatushtml.py > /tmp/trash2.html"""
    
    # convert stdin to dataframe
    df = stdin_to_dataframe()

    # filter out for "Active Sensors" page
    df_filt = filter_active_sensors(df)
    
    # drop some columns that we do not want
    df = drop_unwanted_columns(df_filt)
    
    # top table will be EE "Unit" (not "Sensor")
    df_EE = keep_only(df, '^122f0')
    df_EE = df_EE.rename(columns = {'Location': 'SAMS EE Location', 'Sensor': 'Unit'})    
    
    # bottom table will be remainder, which should be SE "Sensor"
    df_sams, df_mams = drop_EE(df)
    
    # write for piped output
    sys.stdout.write(_HEADER)
    sys.stdout.write( active_sensors_css_html(df_EE, 'other') )
    sys.stdout.write( '<br>')
    sys.stdout.write( active_sensors_css_html(df_sams, 'sams') )
    sys.stdout.write( '<br>')
    sys.stdout.write( active_sensors_css_html(df_mams, 'mams') )    
    sys.stdout.write(_FOOTER)
