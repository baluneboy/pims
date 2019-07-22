#!/usr/bin/env python

import os
import pandas as pd
import glob


def get_csv_files(glob_pat):
    """return list of csv files that match glob pattern"""
    return glob.glob(glob_pat)


if __name__ == "__main__":
    
    # FIXME more pythonic way to get header labels on output file (interleave xyz with min,mean,std,max strings)    
    hdr = ''
    for op in ['min','mean', 'std', 'max']:
        for ax in 'xyz':
            hdr += '%s%s,' % (ax, op)
    print hdr.rstrip(',') + ',csvfile'
    
    # iterate over date range in 2017 (stray date in 2018-09?)
    for ym in pd.date_range('2017-09-01', '2018-01-01', freq='1M'):
        ymd = 'year%4d/month%02d/day??' % (ym.year, ym.month)
        glob_pat = '/misc/yoda/www/plots/batch/%s/*_ossbtmf_gvt3_historical_time-shifted_quasi-steady_estimate.csv' % ymd
        # glob_pat = '/tmp/on?.csv'
        csv_files = get_csv_files(glob_pat)
        for csv_file in csv_files:
            df = pd.read_csv(csv_file, names=['sdn', 'x', 'y', 'z'], usecols=['x', 'y', 'z'])
            mins = df.min(axis=0)
            means = df.mean(axis=0)
            stds = df.std(axis=0)
            maxs = df.max(axis=0)
            s = '{:+7.4f},{:+7.4f},{:+7.4f},'.format(*mins.values)
            s += '{:+7.4f},{:+7.4f},{:+7.4f},'.format(*means.values)
            s += '{:+7.4f},{:+7.4f},{:+7.4f},'.format(*stds.values)
            s += '{:+7.4f},{:+7.4f},{:+7.4f},'.format(*maxs.values)
            s += '%s' % os.path.basename(csv_file)
            print s
