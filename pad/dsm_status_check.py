#!/usr/bin/env python

import datetime
import pandas as pd
from dateutil import parser

from pims.database.pimsquery import db_connect
from pims.utils.pimsdateutil import doytimestr_to_datetime, datetime_to_doytimestr

# get packet amount (in seconds assuming packets_per_second) from start to stop
def get_packets_timedelta(sensor, start, stop, host, packets_per_second=8):
    """get packet amount (in seconds assuming packets_per_second) from start to stop"""
    r = db_connect('select count(*) from %s where time > unix_timestamp("%s") and time < unix_timestamp("%s")' % (sensor, start, stop), host)
    m = r[0][0] / packets_per_second / 60.0
    return datetime.timedelta( minutes=m )

# query host's sensor table to calculate amount of packets from start to stop and return that as timedelta
def get_db_minutes(start, stop, sensor='121f03', host='manbearpig'):
    """query host's sensor table to calculate amount of packets from start to stop and return that as timedelta"""
    if not start: return None
    return get_packets_timedelta(sensor, str(start), str(stop), host)

df = pd.read_csv('/misc/yoda/www/plots/user/sams/gaps/summarize_gaps.txt', sep='\s\s')
df['date'] = df['date'].apply(parser.parse)
out = df.groupby(['date','sensor']).max()
out.to_csv('/tmp/out.csv')
raise SystemExit

df = pd.read_csv('/misc/yoda/www/plots/user/sams/gaps/input4dsmstatuschk.csv', sep='\s\s')
df['start'] = df['start'].apply(doytimestr_to_datetime)
df['stop'] = df['stop'].apply(doytimestr_to_datetime)
df['tdelta'] = df['stop'] - df['start']
#df.to_csv('/tmp/trash.csv')
#raise SystemExit
df['dbminutes'] = df.apply(lambda x: get_db_minutes(x['start'], x['stop'], sensor='121f03', host='manbearpig'), axis=1)
df['missing'] = df['tdelta'] - df['dbminutes']
#print df
df['start'] = df['start'].apply(datetime_to_doytimestr)
df['stop']  = df['stop'].apply(datetime_to_doytimestr)
print df[ df['missing'] > datetime.timedelta(minutes=2) ]
