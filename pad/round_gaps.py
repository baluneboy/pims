#!/usr/bin/env python

import pandas as pd
from pims.utils.pimsdateutil import ceil_minute, floor_minute, doytimestr_to_datetime, datetime_to_doytimestr

def convertstr_applyfunc(s, func):
    d = doytimestr_to_datetime(s)
    return datetime_to_doytimestr( func(d) )[0:-7]

def convert_start(s):
    return convertstr_applyfunc(s, floor_minute)

def convert_stop(s):
    return convertstr_applyfunc(s, ceil_minute)

df = pd.read_csv('/misc/yoda/tmp/2015_03_25to30_gaps.csv')
df['start'] = df['start'].apply(convert_start)
df['stop'] = df['stop'].apply(convert_stop)
print df