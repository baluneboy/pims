#!/usr/bin/env python

import re
import sys
import csv
import numpy as np
import pandas as pd
import datetime
from cStringIO import StringIO
from pims.utils.pimsdateutil import hours_in_month

# filter and pivot to get aggregate sum of monthly hours
def monthly_hours(df, s):
    """filter and pivot to get aggregate sum of monthly hours"""
    ndf = df.filter(regex='Date|Year|Month|Day|' + s + '.*_hours')
    cols = [i for i in ndf.columns if i not in ['Date', 'Year', 'Month', 'Day']]
    t = pd.pivot_table(ndf, rows=['Year','Month'], values=cols, aggfunc=np.sum)
    series = t.transpose().sum()
    return series

# put systems' monthly hours (each a series) into pd.DataFrame
def monthly_hours_dataframe(df, systems_series):
    """put systems' monthly hours (each a series) into pd.DataFrame"""
    for k, v in systems_series.iteritems():
        systems_series[k] = monthly_hours(df, k)    
    monthly_hours_df = pd.DataFrame(systems_series)
    monthly_hours_df.columns = [ s.upper() for s in monthly_hours_df.columns ]
    return monthly_hours_df

# parse date/times from the csv
def parse(s):
    doy = int(s[0:3])
    hr =  int(s[4:6])
    mi = int(s[7:9])
    sec = int(s[10:12])
    yr =  int(s[14:18])
    #print doy, hr, mi, sec, yr; raise SystemExit
    mu_sec = 0
    dt = datetime.datetime(yr - 1, 12, 31)
    delta = datetime.timedelta(days=doy, hours=hr, minutes=mi, seconds=sec, microseconds=mu_sec)
    return dt + delta

#s = '078 11:46:46  2014'
#print parse(s)
#raise SystemExit

def csvDOY2dataframe(csvfile):
    with open(csvfile, 'rb') as f:
        labels = f.next().strip().split(',')
        df = pd.read_csv( csvfile, parse_dates={'time': ['Time']}, date_parser=parse) #, index_col='time') 
    return df

def csv2dataframe(csvfile):
    with open(csvfile, 'rb') as f:
        labels = f.next().strip().split(',')
        df = pd.read_csv( csvfile, parse_dates={'time' : [0]} )
    return df

csvfile = '/tmp/cmdlog.csv'
df1 = csvDOY2dataframe(csvfile)
csvfile = '/tmp/cmdlog2.csv'
df2 = csv2dataframe(csvfile)
df1.to_csv('/tmp/c1.csv')
df2.to_csv('/tmp/c2.csv')
raise SystemExit


## produce output csv with per-system monthly sensor hours totals & rolling means
#def OLD_main(csvfile):
#    """produce output csv with per-system monthly sensor hours totals & rolling means"""
#    # read input CSV into big pd.DataFrame
#    df = csv2dataframe(csvfile)
#
#    # systems' monthly hours (each a series from pivot) into dataframe
#    systems_series = {'sams':None, 'mams':None}
#    monthly_hours_df = monthly_hours_dataframe(df, systems_series)
#    
#    # pd.concat rolling means (most recent n months) into growing dataframe
#    systems = list(monthly_hours_df.columns)
#    original_mdf = monthly_hours_df.copy()
#    num_months = [3, 6, 9]
#    clip_value = 0.01 # threshold to clip tiny values with
#    for n in num_months:
#        roll_mean = pd.rolling_mean(original_mdf, window=n)
#        # rolling mean can produce tiny values (very close to zero), so clip/replace with zeros
#        for system in systems:
#            roll_mean[system] = roll_mean[system].clip(clip_value, None)
#            roll_mean.replace(to_replace=clip_value, value=0.0, inplace=True)
#        roll_mean.columns = [ i + '-%d' % n for i in systems]
#        monthly_hours_df = pd.concat([monthly_hours_df, roll_mean], axis=1)
#    
#    # save csv output file
#    csvout = csvfile.replace('.csv','_monthly.csv')
#    monthly_hours_df.to_csv(csvout)
#    print 'wrote %s' % csvout

# produce output csv with per-system monthly sensor hours totals & rolling means
def main(csvfile, resource_csvfile):
    """produce output csv with per-system monthly sensor hours totals & rolling means"""
    
    # read resource config csv file
    df_cfg = resource_csv2dataframe(resource_csvfile)
    regex_sensor_hours = '.*' + '_hours|.*'.join(df_cfg['Resource']) + '_hours'
    
    # read input CSV into big pd.DataFrame
    df = csv2dataframe(csvfile)

    # filter to keep only hours columns (gets rid of bytes columns) for each sensor
    # that shows up in df_cfg's Resource column
    ndf = df.filter(regex='Date|Year|Month|Day|' + regex_sensor_hours)
    
    # pivot to aggregate monthly sum for each "sensor_hours" column
    t = pd.pivot_table(ndf, rows=['Year','Month'], aggfunc=np.sum)
    
    # drop the unwanted "Day" column
    df_monthly_hours = t.drop('Day', 1)
    
    # convert index, which are tuples like (YEAR, MONTH), to tuples like (YEAR, MONTH, 1)
    date_tuples = [ ( t + (1,) ) for t in df_monthly_hours.index.values ]

    # convert date_tuples each to hours_in_month
    hours = [ hours_in_month( datetime.date( *tup ) ) for tup in date_tuples ]

    # before we add hours_in_month column, get list of columns for iteration below
    cols = df_monthly_hours.columns.tolist()
    
    # now we can append month_hours column
    df_monthly_hours['hours_in_month'] = pd.Series( hours, index=df_monthly_hours.index)
    
    # iterate over columns (excluding hours_in_month) to get 100*sensor_hours/hours_in_month
    for c in cols:
        pctstr = c + '_pct'
        pct = 100 * df_monthly_hours[c] / df_monthly_hours['hours_in_month']
        df_monthly_hours[pctstr] = pd.Series( pct, index=df_monthly_hours.index)
    
    # save csv output file
    csvout = csvfile.replace('.csv','_monthly_hours.csv')
    df_monthly_hours.to_csv(csvout)
    print 'wrote %s' % csvout
        
if __name__ == '__main__':
    if len(sys.argv) == 3:
        csvfile = sys.argv[1]
        resource_csvfile = sys.argv[2]
    else:
        csvfile = '/misc/yoda/www/plots/batch/padtimes/padtimes.csv'
        resource_csvfile = '/misc/yoda/www/plots/batch/padtimes/kpi_track.csv'
    main(csvfile, resource_csvfile)    