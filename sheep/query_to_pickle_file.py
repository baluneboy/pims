#!/usr/bin/env python

import os
import pickle
import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta

from pims.files.utils import mkdir_p
from pims.database.samsquery import query_ee_packet_hs
from pims.sheep.gather_data import parse_date_from_filename, get_ee_stats_files

def get_missing_date_range(pickle_dir):
    """use dead reckoning to determine date range for missing ee_stats files"""
    ee_stats_files = get_ee_stats_files(pickle_dir)
    ee_stats_files.sort()
    try:
        last_file = ee_stats_files[-1]
        d1 = parse_date_from_filename(last_file) + relativedelta(days=1)
        d2 = datetime.datetime.now().date() - relativedelta(days=2)
        if d2 < d1:
            drange = None
        else:
            drange = (d1, d2)
    except Exception, e:
        drange = None
    return drange

def fill_missing_date_range():
    """let us pickle the days to fill the missing date range with ee_stats files"""
    pickle_dir ='/misc/yoda/www/plots/user/sheep'
    #pickle_dir = '/Users/ken/Downloads/sheep'
    drange = get_missing_date_range(pickle_dir)
    if drange:
        print 'fill date range', drange
        pickle_date_range(drange[0], drange[1])

def pickle_ee_stats(df, fname):
    ee_stats = {}
    ees = df.ee_id.unique()
    for ee in ees:
        df_ee = df[ df['ee_id'] == ee ]
        ee_stats[ee] = df_ee.describe()
    dir_path = os.path.dirname(fname)
    if not os.path.isdir(dir_path):
        mkdir_p(dir_path)
    with open(fname, 'wb') as f:
        pickle.dump(ee_stats, f, protocol=pickle.HIGHEST_PROTOCOL)

def pickle_date_range(start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date)
    for d1 in date_range:
        y1 = d1.year
        m1 = d1.month
        t1 = d1.strftime('%Y-%m-%d')
        d2 = d1 + relativedelta(days=1)
        print 'running query for %s' % t1,
        df = query_ee_packet_hs(d1, d2)
        #save_file = '/misc/yoda/www/plots/user/sheep/ee_stats_' + t1 + '.pkl'
        save_file = '/misc/yoda/www/plots/user/sheep/year%04d/month%02d/pickles/ee_stats_' % (y1, m1) + t1 + '.pkl'
        print 'saving %s' % save_file,
        pickle_ee_stats(df, save_file)
        print 'done'

def temp_fix():
    """let us pickle small ee_stats instead of huge df"""
    import os
    from dateutil.parser import parse
    from gather_data import read_df_from_file, get_dataframe_pickle_files

    df_pick_files = get_dataframe_pickle_files(df_pickle_dir='/Users/ken/Downloads')
    for f in df_pick_files:
        t1 = parse_date_from_filename(f)
        ee_stats = read_df_from_file(f)
        fname = '/Users/ken/Downloads/ee_stats_' + t1.strftime('%Y-%m-%d') + '.pkl'
        print 'saving to %s' % fname,
        with open(fname, 'wb') as fh:
            pickle.dump(ee_stats, fh, protocol=pickle.HIGHEST_PROTOCOL)
        print 'done'

if __name__ == "__main__":
    #temp_fix()
    fill_missing_date_range()
