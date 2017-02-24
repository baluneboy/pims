#!/usr/bin/env python

import os
import re
import json
import datetime
from dateutil import relativedelta
import pandas as pd
from dateutil.parser import parse
from matplotlib.dates import date2num

from pims.utils.iterabletools import pairwise
from pims.files.utils import filter_filenames

# define measures to consider for truly tracking trending
MEAS_DICT = {
    
    'TEMPS':
        [
        'head0_tempX',
        'head0_tempY',
        'head0_tempZ',
        'head1_tempX',
        'head1_tempY',
        'head1_tempZ',
        'tempbase'
        ],
        
    'VOLTS':
        [
        'head0_plus5V',
        'head0_plus15V',
        'head0_minus15V',
        'head1_plus5V',
        'head1_plus15V',
        'head1_minus15V',
        'pc104_plus5V',
        'ref_plus5V',
        'ref_zeroV'        # this one never seems to change (probably not actual measurement)
        ]
}

def get_dataframe_pickle_files(df_pickle_dir='/misc/yoda/www/plots/user/sheep'):
    # FIXME refine this with date range or regexp maybe instead of always getting all files
    # FIXME elsewhere you should probably be pruning this list of files too (keep most recent 4 months?)
    fullfile_pattern = r'%s' % os.path.join(df_pickle_dir, 'df_ee_pkt_hs_.*\.pkl')
    files = list(filter_filenames(df_pickle_dir, re.compile(fullfile_pattern).match))
    files.sort()
    return files

def read_df_from_file(fname):
    df = pd.read_pickle(fname)
    ees = df.ee_id.unique()
    ee_stats = {}
    for ee in ees:
        df_ee = df[ df['ee_id'] == ee ]
        ee_stats[ee] = df_ee.describe()
    return ee_stats

def skeleton_get_stats(measures):
    pass

# FIXME this is bad form, we should have (measures, group) as inner loop; otherwise, you read same files for each group!
def get_stats(measures, group):
    
    # initialize output dict
    stats = {}
    # FIXME this assumes always same set of EEs are of interest (we have others you know)
    for e in ['122-f02', '122-f03', '122-f04', '122-f07']:
        for m in measures:
            key = (group, e, m)
            stats[key] = []
    
    # get EE HS info from dataframe pickle files (sorted by date)
    df_pick_files = get_dataframe_pickle_files()
    
    # consider days in pairwise fashion: yesterday-today
    # "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    for file_pair in pairwise(df_pick_files[0:3]):
        
        # we cannot assume 2 consecutive days, so check that
        # note we are splitting basenames like df_ee_pkt_hs_2017-01-02.pkl
        date1 = parse(os.path.basename(file_pair[0]).split('_')[-1].split('.')[0]).date()
        date2 = parse(os.path.basename(file_pair[1]).split('_')[-1].split('.')[0]).date()
        
        # if t2 minus t1 not equal exactly positive one (days), then we punt
        if (date2 - date1).days != 1:
            print 'SKIPPING NON-CONSECUTIVE DAYS FOR', file_pair
            continue
        
        # FIXME this is doubly inefficient, we could pre-loop snag yesterday's median!?
        ee_stats1 = read_df_from_file(file_pair[0]) # yesterday's dict of ee stats
        ee_stats2 = read_df_from_file(file_pair[1]) # today's     dict of ee stats
        
        # FIXME this is where you'd scrub each of ee_stats1 and ee_stats2 to see if head0 or head1 id changes (sensor moved)
        
        # FIXME if you scrubbed for head0, head1 changes, then at this point you can do column/label replace head0(1) with se_ids
        
        # FIXME with graceful acceptance of EE keys yesterday that do not match EE keys today
        #       for now though, we punt
        if sorted(ee_stats1.keys()) != sorted(ee_stats2.keys()):
            print 'SKIPPING MISMATCH EE STATS KEYS FOR', file_pair
            continue
        
        # get two-day pair into a "today tuple" (datenum, yestmed, todayhi, todaylo, todaymed, todayvolume)
        # this feeds directly into candlestick plot, which shows up/down trending
        print date2 # number two is today; one is yesterday
        
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
    
    return stats
            
def process_date_range(start_date, end_date, meas_dict):
    stats = {}
    date_range = pd.date_range(start=start_date, end=end_date)
    for group, measures in meas_dict.iteritems():
        for measure in measures:
            today_tups = []
            for d1 in date_range:
                t1 = d1.strftime('%Y-%m-%d')
                today_tups.append((d1, t1))
                d2 = d1 + relativedelta.relativedelta(days=1)
                #print 'working on %s' % t1,
                #print 'done'
            stats_tree[group][measure] = today_tups
    print json.dumps(stats_tree, sort_keys=True, indent=3, separators=(',', ':'))

if __name__ == "__main__":
    d1 = datetime.datetime(2016,12,31).date()
    d2 = datetime.datetime(2017,1,14).date()
    process_date_range(d1, d2, MEAS_DICT)
    #stats = get_stats(MEAS_DICT)