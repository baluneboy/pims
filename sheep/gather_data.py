#!/usr/bin/env python

import os
import re
import pickle
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from dateutil.parser import parse
from matplotlib.dates import date2num
from collections import namedtuple

from pims.utils.iterabletools import pairwise
from pims.files.utils import filter_filenames
from pims.sheep.limits_measures import GROUP_MEASURES
from pims.files.filter_pipeline import FileFilterPipeline, EeStatsFile

#                                         datenum    yestmed          todayhi todaylo  todaymed  todayvolume
CandlePoint = namedtuple('CandlePoint', ['datenum', 'yesterday_median', 'high', 'low', 'median', 'volume'])

def parse_date_from_filename(fname):
    return parse(os.path.basename(fname).split('_')[-1].split('.')[0]).date()

def get_missing_date_range(pickle_dir):
    """use dead reckoning to determine date range for missing ee_stats files"""
    ee_stats_files = get_ee_stats_files(pickle_dir)
    ee_stats_files.sort()
    try:
        d1 = parse_date_from_filename(ee_stats_files[-1]) + relativedelta(days=1)
    except Exception, e:
        d1 = None
    if d1:
        d2 = datetime.datetime.now().date() - relativedelta(days=2)
    else:
        d2 = None
    return d1, d2
    
def fill_missing_date_range():
    """let us pickle the days to fill the missing date range"""
    #pickle_dir ='/misc/yoda/www/plots/user/sheep'
    pickle_dir = '/Users/ken/Downloads/sheep'
    d1, d2 = get_missing_date_range(pickle_dir)

def blank_record(datenum):
    """return CandlePoint [for missing file?] with datenum & volume; other values NaN"""
    yesterday_median, high, low, median = np.nan, np.nan, np.nan, np.nan
    volume = 0
    return CandlePoint(datenum, yesterday_median, high, low, median, volume)

def get_dataframe_pickle_files(df_pickle_dir='/misc/yoda/www/plots/user/sheep'):
    # FIXME refine this with date range or regexp maybe instead of always getting all files
    # FIXME elsewhere you should probably be pruning this list of files too (keep most recent 4 months?)
    fullfile_pattern = r'%s' % os.path.join(df_pickle_dir, 'df_ee_pkt_hs_.*\.pkl')
    files = list(filter_filenames(df_pickle_dir, re.compile(fullfile_pattern).match))
    files.sort()
    return files

def get_ee_stats_files(pickle_dir='/misc/yoda/www/plots/user/sheep'):
    fullfile_pattern = r'%s' % os.path.join(pickle_dir, 'ee_stats_.*\.pkl')
    files = list(filter_filenames(pickle_dir, re.compile(fullfile_pattern).match))
    return files

def read_ee_stats_file(fname):
    with open(fname, 'rb') as handle:
        ee_stats = pickle.load(handle)
    return ee_stats

def process_date_range(start_date, end_date, group_measures=GROUP_MEASURES, pickle_dir='/misc/yoda/www/plots/user/sheep'):

    # get EE stats as dict from pickle files
    temp_files = get_ee_stats_files(pickle_dir=pickle_dir)
    ffp = FileFilterPipeline(EeStatsFile(start_date=start_date, end_date=end_date))
    ee_stats_files = list(ffp(temp_files))
    ee_stats_files.sort()

    # before candlestick calcs, cache all ee stats (dataframes) with date as key
    # this to also establish master list of EEs to consider
    ee_set = set()
    cached_ee_stats = {}
    print 'caching EE stats from files',
    for f in ee_stats_files:
        d = parse_date_from_filename(f)
        ee_stats = read_ee_stats_file(f)
        cached_ee_stats[date2num(d)] = ee_stats
        ee_set = ee_set.union(ee_stats.keys())
        print '.',
    print 'done'
    ee_list = sorted(list(ee_set))
    
    # initialize output dict
    stats = {}

    # get date range to loop over
    date_range = pd.date_range(start=start_date, end=end_date)

    # loop calculations
    for group, measures in group_measures.iteritems():
        # note: group is like VOLTS or TEMPS; measures are like head0_tempX or head1_plus5V
        for ee in ee_list:
            for measure in measures:
                key = (group, ee, measure)
                today_candle_pts = []
                for d in date_range:

                    today = date2num(d)
                    yesterday = date2num( d - relativedelta(days=1) )

                    if today not in cached_ee_stats:
                        candle_point = blank_record(today)
                        today_candle_pts.append(candle_point)
                        continue

                    today_stats = cached_ee_stats[today]
                    
                    if yesterday not in cached_ee_stats:
                        #CandlePoint = namedtuple('CandlePoint', ['datenum', 'yesterday_median', 'high', 'low', 'median', 'volume'])
                        candle_point = CandlePoint(
                            today,
                            np.nan,
                            today_stats[ee][measure]['75%'],
                            today_stats[ee][measure]['25%'],
                            today_stats[ee][measure]['50%'],
                            today_stats[ee][measure]['count'])
                        today_candle_pts.append(candle_point)
                        continue

                    yesterday_stats = cached_ee_stats[yesterday]

                    candle_point = CandlePoint(
                        today,
                        yesterday_stats[ee][measure]['50%'],
                        today_stats[ee][measure]['75%'],
                        today_stats[ee][measure]['25%'],
                        today_stats[ee][measure]['50%'],
                        today_stats[ee][measure]['count'])
                    today_candle_pts.append(candle_point)

                stats[key] = today_candle_pts
                
    return stats

if __name__ == "__main__":
    d1, d2 = get_missing_date_range('/Users/ken/Downloads/sheep')
    print d1
    print d2
    raise SystemExit

    d1 = datetime.datetime(2016,12,2).date()
    d2 = datetime.datetime(2016,12,15).date()
    stats = process_date_range(d1, d2, pickle_dir='/Users/ken/Downloads/sheep')
    print stats[('TEMPS', '122-f02', 'tempbase')]
    #print stats[('VOLTS', '122-f07', 'head1_plus5V')]
