#!/usr/bin/env python

import pickle
import datetime
import pandas as pd
from dateutil import relativedelta

from pims.database.samsquery import query_ee_packet_hs

def pickle_ee_stats(df, fname):
    ee_stats = {}
    ees = df.ee_id.unique()
    for ee in ees:
        df_ee = df[ df['ee_id'] == ee ]
        ee_stats[ee] = df_ee.describe()
    with open(fname, 'wb') as f:
        pickle.dump(ee_stats, f, protocol=pickle.HIGHEST_PROTOCOL)
    
def OLDpickle_date_range(start_date, end_date, just_weekdays=False):
    if just_weekdays:
        date_range_func = pd.bdate_range # just weekdays
    else:
        date_range_func = pd.date_range  # all days
    date_range = date_range_func(start=start_date, end=end_date)
    for d1 in date_range:
        t1 = d1.strftime('%Y-%m-%d')
        d2 = d1 + relativedelta.relativedelta(days=1)
        print 'working on %s' % t1,
        df = query_ee_packet_hs(d1, d2)
        df.to_pickle('/misc/yoda/www/plots/user/sheep/df_ee_pkt_hs_' + t1 + '.pkl')
        print 'done'

def pickle_date_range(start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date)
    for d1 in date_range:
        t1 = d1.strftime('%Y-%m-%d')
        d2 = d1 + relativedelta.relativedelta(days=1)
        print 'running query for %s' % t1,
        df = query_ee_packet_hs(d1, d2)
        save_file = '/misc/yoda/www/plots/user/sheep/ee_stats_' + t1 + '.pkl'
        print 'saving ee_stats to file',
        pickle_ee_stats(df, save_file)
        print 'done'

def temp_fix():
    """let's pickle small ee_stats instead of huge df"""
    import os
    from dateutil.parser import parse
    from gather_data import read_df_from_file, get_dataframe_pickle_files
    
    df_pick_files = get_dataframe_pickle_files(df_pickle_dir='/Users/ken/Downloads')    
    for f in df_pick_files:
        t1 = parse(os.path.basename(f).split('_')[-1].split('.')[0]).date()        
        ee_stats = read_df_from_file(f)
        fname = '/Users/ken/Downloads/ee_stats_' + t1.strftime('%Y-%m-%d') + '.pkl'
        print 'saving to %s' % fname,
        with open(fname, 'wb') as fh:
            pickle.dump(ee_stats, fh, protocol=pickle.HIGHEST_PROTOCOL)
        print 'done'
        
if __name__ == "__main__":
    #temp_fix()
    d1 = datetime.datetime(2016,11,1).date()
    d2 = datetime.datetime(2016,12,30).date()
    pickle_date_range(d1, d2)
