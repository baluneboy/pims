#!/usr/bin/env python

import os
import re
import pandas as pd
from dateutil.parser import parse
from matplotlib.dates import date2num

from pims.utils.iterabletools import pairwise
from pims.files.utils import filter_filenames

def get_dataframe_pickle_files(pick_dir='/Users/ken/Downloads'):
    # FIXME refine this with date range or regexp maybe
    fullfile_pattern = r'%s' % os.path.join(pick_dir, 'df_ee_pkt_hs_.*\.pkl')
    files = list(filter_filenames(pick_dir, re.compile(fullfile_pattern).match))
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
    
    ee_stats1 = read_df_from_file(file_pair[0]) # yesterday's dict of ee stats
    ee_stats2 = read_df_from_file(file_pair[1]) # today's     dict of ee stats
    
    # FIXME with graceful acceptance of EE keys yesterday that do not match EE keys today
    #       for now though, we punt
    if sorted(ee_stats1.keys()) != sorted(ee_stats2.keys()):
        print 'SKIPPING MISMATCH EE STATS KEYS FOR', file_pair
        continue
    
    # get two-day pair into a "today tuple" (datenum, yestmed, todayhi, todaylo, todaymed, todayvolume)
    print '\n', date2, 'comparing to', date1
    print '^^^^^^^^^^'
    
    # FIXME this assumes no mismatch in ee_stats1.keys and ee_stats2.keys
    temps = [
            'head0_tempX',
            'head0_tempY',
            'head0_tempZ',
            'head1_tempX',
            'head1_tempY',
            'head1_tempZ',
            'tempbase'
            ]          
    
    volts = [
            'head0_plus5V',
            'head0_plus15V',
            'head0_minus15V',
            'head1_plus5V',
            'head1_plus15V',
            'head1_minus15V',
            'pc104_plus5V',
            'ref_plus5V',
            'ref_zeroV'
            ]

    # FIXME there is more info to consider; e.g. ee_stats2[ee] df has:
    # count   we call this today_volume  
    # mean    UNUSED BUT A CLASSIC, POSSIBLY SKEWED?
    # std     UNUSED BUT POSSIBLY THE MOST TELLING?
    # min     UNUSED sometimes sporadic min values
    # 25%     we call this today_low
    # 50%     we call this today_median
    # 75%     we call this today_high
    # max     UNUSED sometimes sporadic max values
    
    for meas in temps:
        print meas
        print '=========='
        for ee in sorted(ee_stats1.keys()):   
            today_tup = (
                date2num(date2),              # today as datenum
                ee_stats1[ee][meas]['50%']  , # yesterday_median
                ee_stats2[ee][meas]['50%']  , # today_median             
                ee_stats2[ee][meas]['75%']  , # today_high          
                ee_stats2[ee][meas]['25%']  , # today_low           
                ee_stats2[ee][meas]['count']  # today_volume
            )
            print ee, today_tup
        
        
        
