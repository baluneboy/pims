#!/usr/bin/env python

import os
import re
import pickle
import datetime
from dateutil import relativedelta
import numpy as np
import pandas as pd
from dateutil.parser import parse
from matplotlib.dates import date2num
from collections import namedtuple

from pims.utils.iterabletools import pairwise
from pims.files.utils import filter_filenames
from pims.sheep.limits_measures import GROUP_MEASURES

#                                         datenum    yestmed          todayhi todaylo  todaymed  todayvolume
CandlePoint = namedtuple('CandlePoint', ['datenum', 'yesterday_median', 'high', 'low', 'median', 'volume'])

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
    # FIXME refine this with date range or regexp maybe instead of always getting all files
    fullfile_pattern = r'%s' % os.path.join(pickle_dir, 'ee_stats_.*\.pkl')
    files = list(filter_filenames(pickle_dir, re.compile(fullfile_pattern).match))
    files.sort()
    return files

def OLD_read_df_from_file(fname):
    df = pd.read_pickle(fname)
    ees = df.ee_id.unique()
    ee_stats = {}
    for ee in ees:
        df_ee = df[ df['ee_id'] == ee ]
        ee_stats[ee] = df_ee.describe()
    return ee_stats

def read_ee_stats_file(fname):
    with open(fname, 'rb') as handle:
        ee_stats = pickle.load(handle)
    return ee_stats

# FIXME this is bad form, we should have (measures, group) as inner loop; otherwise, you read same files for each group!
def OLD_get_stats(measures, group):

    # get EE HS info from dataframe pickle files (sorted by date)
    df_pick_files = get_dataframe_pickle_files(df_pickle_dir='/Users/ken/Downloads')

    # use first file to establish EEs, measures, etc.
    #   note: we are splitting basenames like df_ee_pkt_hs_2017-01-02.pkl
    f1 = df_pick_files[0]
    date1 = parse(os.path.basename(f1).split('_')[-1].split('.')[0]).date()
    ee_stats1 = read_df_from_file(f1) # the 1st yesterday's dict of ee stats

    # initialize output dict
    stats = {}
    # FIXME this assumes always same set of EEs are of interest (we may have others you know)
    #       but here we just naively allow first file to dictate what EEs to consider
    for e in sorted(ee_stats1.keys()):
        for m in measures:
            key = (group, e, m)
            stats[key] = []

    # consider days in pairwise fashion: yesterday-today
    for f2 in df_pick_files[1:4]:

        date2 = parse(os.path.basename(f2).split('_')[-1].split('.')[0]).date()

        # if t2 minus t1 not equal exactly positive one (days), then we punt
        if (date2 - date1).days != 1:
            print 'SKIPPING NON-CONSECUTIVE DAYS FOR', file_pair
            continue
        else:
            print date1, 'and', date2

        ee_stats2 = read_df_from_file(f2) # today's dict of ee stats

        # FIXME this is where you'd scrub each of ee_stats1 and ee_stats2 to see if head0 or head1 id changes (sensor moved)

        # FIXME if you scrubbed for head0, head1 changes, then at this point you can do column/label replace head0(1) with se_ids

        # FIXME with graceful acceptance of EE keys yesterday that do not match EE keys today
        #       for now though, we punt
        if sorted(ee_stats1.keys()) != sorted(ee_stats2.keys()):
            print 'SKIPPING MISMATCH EE STATS KEYS FOR', file_pair
            continue

        # we use two-day pair to get "today tuple" (datenum, yestmed, todayhi, todaylo, todaymed, todayvolume)
        # this feeds directly into candlestick plot, which shows up/down trending

        # FIXME this assumes no mismatch of keys in ee_stats1 vs. ee_stats2

        # FIXME there is more info to consider; e.g. ee_stats2[ee] df has:
        # count   we call this today_volume
        # mean    UNUSED BUT A CLASSIC, POSSIBLY SKEWED?
        # std     UNUSED BUT POSSIBLY THE MOST TELLING?
        # min     UNUSED sometimes sporadic min values
        # 25%     we call this today_low
        # 50%     we call this today_median
        # 75%     we call this today_high
        # max     UNUSED sometimes sporadic max values

        for measure in measures:
            for ee in sorted(ee_stats1.keys()):
                today_tup = (
                    date2num(date2),              # today as datenum
                    ee_stats1[ee][measure]['50%']  , # yesterday_median
                    ee_stats2[ee][measure]['50%']  , # today_median
                    ee_stats2[ee][measure]['75%']  , # today_high
                    ee_stats2[ee][measure]['25%']  , # today_low
                    ee_stats2[ee][measure]['count']  # today_volume
                )
                key = (group, ee, measure)
                stats[key].append(today_tup)

        date1 = date2
        ee_stats1 = ee_stats2

    return stats

def NEWER_get_stats(measures, group):

    # get EE HS info from dataframe pickle files (sorted by date)
    df_pick_files = get_dataframe_pickle_files(df_pickle_dir='/Users/ken/Downloads')

    # use first file to establish EEs, measures, etc.
    #   note: we are splitting basenames like df_ee_pkt_hs_2017-01-02.pkl
    f1 = df_pick_files[0]
    date1 = parse(os.path.basename(f1).split('_')[-1].split('.')[0]).date()
    ee_stats1 = read_df_from_file(f1) # the 1st yesterday's dict of ee stats

    # initialize output dict
    stats = {}
    # FIXME this assumes always same set of EEs are of interest (we may have others you know)
    #       but here we just naively allow first file to dictate what EEs to consider
    for measure in measures:
        for ee in sorted(ee_stats1.keys()):

            key = (group, ee, measure)
            stats[key] = []

            # consider days in pairwise fashion: yesterday-today
            for f2 in df_pick_files[1:4]:

                date2 = parse(os.path.basename(f2).split('_')[-1].split('.')[0]).date()

                # if t2 minus t1 not equal exactly positive one (days), then we punt
                if (date2 - date1).days != 1:
                    print 'SKIPPING NON-CONSECUTIVE DAYS FOR', date1, 'and', date2
                    continue
                else:
                    print date1, 'and', date2, 'for', ee

                ee_stats2 = read_df_from_file(f2) # today's dict of ee stats

                # FIXME this is where you'd scrub each of ee_stats1 and ee_stats2 to see if head0 or head1 id changes (sensor moved)

                # FIXME if you scrubbed for head0, head1 changes, then at this point you can do column/label replace head0(1) with se_ids

                # FIXME with graceful acceptance of EE keys yesterday that do not match EE keys today
                #       for now though, we punt
                if sorted(ee_stats1.keys()) != sorted(ee_stats2.keys()):
                    print 'SKIPPING MISMATCH EE STATS KEYS FOR', file_pair
                    continue

                # we use two-day pair to get "today tuple" (datenum, yestmed, todayhi, todaylo, todaymed, todayvolume)
                # this feeds directly into candlestick plot, which shows up/down trending

                # FIXME this assumes no mismatch of keys in ee_stats1 vs. ee_stats2

                # FIXME there is more info to consider; e.g. ee_stats2[ee] df has:
                # count   we call this today_volume
                # mean    UNUSED BUT A CLASSIC, POSSIBLY SKEWED?
                # std     UNUSED BUT POSSIBLY THE MOST TELLING?
                # min     UNUSED sometimes sporadic min values
                # 25%     we call this today_low
                # 50%     we call this today_median
                # 75%     we call this today_high
                # max     UNUSED sometimes sporadic max values

                today_tup = (
                    date2num(date2),              # today as datenum
                    ee_stats1[ee][measure]['50%']  , # yesterday_median
                    ee_stats2[ee][measure]['50%']  , # today_median
                    ee_stats2[ee][measure]['75%']  , # today_high
                    ee_stats2[ee][measure]['25%']  , # today_low
                    ee_stats2[ee][measure]['count']  # today_volume
                )
                key = (group, ee, measure)
                stats[key].append(today_tup)

                date1 = date2
                ee_stats1 = ee_stats2

def process_date_range(start_date, end_date, group_measures=GROUP_MEASURES, pickle_dir='/Users/ken/Downloads'):

    # FIXME with better file-fetching here (USE DATE RANGE MINUS ONE FOR FIRST DATE TO GET YESTERDAY AS #1)
    # get EE stats as dict from pickle files (sorted by date)
    ee_stats_files = get_ee_stats_files(pickle_dir='/Users/ken/Downloads')

    # before candlestick calcs, cache all ee stats (dataframes) with date as key
    # this to also establish master list of EEs to consider
    ee_set = set()
    cached_ee_stats = {}
    print 'caching EE stats from files',
    for f in ee_stats_files:
        # note: we are splitting basenames like ee_stats_2017-01-02.pkl
        d = parse(os.path.basename(f).split('_')[-1].split('.')[0]).date()
        ee_stats = read_ee_stats_file(f)
        cached_ee_stats[date2num(d)] = ee_stats
        ee_set = ee_set.union(ee_stats.keys())
        print '.',
    print 'done'
    ee_list = sorted(list(ee_set))
    
    # FIXME candlestick plots only handle exactly 4 EEs at the moment
    if len(ee_list) != 4:
        msg = 'candlestick plots only handle exactly 4 (not %d) EEs right now' % len(ee_list)
        raise Exception(msg)

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
                    yesterday = date2num( d - relativedelta.relativedelta(days=1) )

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
    d1 = datetime.datetime(2017,1,1).date()
    d2 = datetime.datetime(2017,1,14).date()
    stats = process_date_range(d1, d2)
    print stats[('TEMPS', '122-f02', 'tempbase')]
    print stats[('VOLTS', '122-f07', 'head1_plus5V')]
