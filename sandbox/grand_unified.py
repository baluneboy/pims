#!/usr/bin/env python

import re
import datetime
import pandas as pd
import numpy as np
from cStringIO import StringIO
from pims.utils.pimsdateutil import doytimestr_to_datetime, timedelta_hours

# parse date from input text file
def parse(s):
    """parse date from input text file"""
    m, d, y = s.split('/')
    mo = int(m)
    da =  int(d)
    yr = int(y)
    d = datetime.date(yr, mo, da)
    return d

# get rid of NaN and dash in timestr
def replace_timestr(t):
    """get rid of NaN and dash in timestr"""
    if isinstance(t, float):
        return None
    if '-' == t:
        return None
    return t

# boolean True if matches LIKE '123/12:15'
def matches_timestr(s):
    """boolean True if matches LIKE '123/12:15'"""
    if re.match('^\d{3}\/\d{2}:\d{2}$', s):
        return True
    else:
        return False

# merge year and timestr to clean up times
def times_filter(d, times, meets_criteria=matches_timestr):
    """merge year and timestr to clean up times"""
    mapping = map(type, times)
    if [ str, type(None), type(None) ] == mapping and meets_criteria(times[0]):
        d1 = doytimestr_to_datetime('%d:%s:00' % (d[0].year, times[0].replace('/',':')))
        #return '%s'  % d1
        return d1, d1, 0
    elif [ str, str, type(None) ] == mapping and meets_criteria(times[0]) and meets_criteria(times[1]):
        d1 = doytimestr_to_datetime('%d:%s:00' % (d[0].year, times[0].replace('/',':')))
        d2 = doytimestr_to_datetime('%d:%s:00' % (d[1].year, times[1].replace('/',':')))
        #return '%s to %s' % (d1, d2)
        return d1, d2, timedelta_hours(d2-d1)
    else:
        #return ''
        return None, None, None

# clean up events
def events_filter(events):
    """clean up events"""
    mapping = map(type, events)
    if [ str, float, float ] == mapping:
        return '%s'  % events[0]
    else:
        return 'MORE THAN ONE EVENT???'

# clean up remarks
def remarks_filter(remarks):
    """clean up remarks"""
    mapping = map(type, remarks)
    if [ str, float, float ] == mapping:
        return '%s'  % remarks[0]
    if [ float, float, float ] == mapping:
        return 'no remarks'
    else:
        return 'MORE THAN ONE REMARK???'

# clean up attitude name
def att_filter(att):
    """clean up remarks"""
    mapping = map(type, att)
    if [ str, float, float ] == mapping:
        return '%s'  % att[0]
    if [ str, str, float ] == mapping:
        return ' '.join(att[0:2])
    if [ str, str, str ] == mapping:
        return ' '.join(att)
    if [ float, float, float ] == mapping:
        return 'unknown'
    else:
        return 'UNEXPECTED ATTITUDE TRIO???'

# clean up YPR
def ypr_filter(ypr):
    """clean up ypr"""
    return '[ %5.1f, %5.1f, %5.1f ]' % (ypr[0], ypr[1], ypr[2])

#d = [ datetime.date(2014, 9, 5), datetime.date(2014, 9, 5), datetime.date(2014, 9, 5) ]
#times = ('123/12:14', np.nan, np.nan)
#times = ('248/12:14', '249/12:15', np.nan)
#print times_filter(d, times)
#raise SystemExit

# read tab-delimited file (not csv, because some cells have commas)
tab_file = '/home/pims/dev/programs/python/pims/sandbox/data/scratch.csv'
tab_file = '/home/pims/Downloads/Grand_Unified_ATL_tabdelim.txt'
tab_file = '/home/pims/Documents/ATL/raw/inc40a.txt'

##import csv
##def replace_nonprint(s):
##    return ''.join([i if ord(i) < 128 else ' ' for i in s])
### open the csv file to read line-by-line
##with open(tab_file) as fin:
##    #read the csv
##    reader = csv.reader(fin)
##    #enumerate the rows, so that you can
##    #get the row index for the xlsx
##    for index,row in enumerate(reader):
##        #clean_row = replace_nonprint(row[0])
##        #columns = row[0].split('\t')
##        print '%03d %02d' % (index, row[0].count('\t')), row
##        #print index, row[0].split('\t')
##        #for c in columns:
##        #    print c,
##raise SystemExit

df = pd.read_csv(tab_file, sep='\t')

# get rid of rows that have NaN as a value for "set"
df = df[ ~np.isnan(df['set']) ]
df['gmt'] = df['date'].map(parse)

# fix timestr (mostly, but still a string)
df['range'] = df['Maneuver Start-Stop GMT'].map(replace_timestr)

# group by tag to get/work on unique tags
grp = df.groupby(['gmt', 'tag'])
for tag, dfss in iter(grp):
    datetag, tag = tag
        
    # group by set number to get/work set-by-set
    setgrp = dfss.groupby('set')
    for s, dfset in iter(setgrp):
        outstr = ''
        #print dfset
        ##print 'set %04d' % s,
        ##print 'date: %s: main: %s' % (datetag, tag),
        outstr += '%04d' % s
        outstr += '\t%s\t%s' % (datetag, tag)
        
        ypr = [ i for i in dfset['YPR'] ]
        #print ', ypr:', np.round(ypr, decimals=1),
        ##print ', ypr:', ypr_filter(ypr),
        outstr += '\t%5.1f\t%5.1f\t%5.1f' % (ypr[0], ypr[1], ypr[2])
        
        times = [ i for i in dfset['range'] ]
        #print ', time(s):', times,
        
        # first input is for date only, times input is for times
        gmts = times_filter( [ i for i in dfset['gmt'] ], times)
        ##print ', gmt(s):', gmts,
        if gmts[2]:
            dur_minutes = gmts[2]*60.0
            outstr += '\t%s\t%s\t%4.2f' % (gmts[0], gmts[1], dur_minutes)
        else:
            outstr += '\t%s\t%s\t' % (gmts[0], gmts[1])
        
        # Beta Angle
        beta = [ i for i in dfset['Beta Angle'] ]
        outstr += '\t%s' % beta[0]
        
        # Attitude Name
        att = [ i for i in dfset['Attitude Name'] ]
        outstr += '\t%s' % att_filter(att)
        
        # Ref Frame
        ref = [ i for i in dfset['Ref Frame'] ]
        outstr += '\t%s' % ref[0]  
        
        events = [ i for i in dfset['Event'] ]
        ##print ', Event:', events_filter(events),
        outstr += '\t%s' % events_filter(events)
        
        remarks = [ i for i in dfset['Remarks'] ]
        ##print ', Remarks:', remarks_filter(remarks)
        outstr += '\t%s' % remarks_filter(remarks)
        print outstr

    #print '=' * 44