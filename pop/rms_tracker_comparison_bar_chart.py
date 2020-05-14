#!/usr/bin/env python

import os
import sys
import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import datetime
from dateutil import parser
import numpy as np
import matplotlib.dates as dates
import mpl_toolkits.axes_grid.axes_size as Size
from mpl_toolkits.axes_grid import Divider
from matplotlib.dates import MonthLocator, DateFormatter

from pims.files.utils import mkdir_p


def gmt_parse(s):
    """parse GMT datetime for pandas dataframe"""
    try:
        d = pd.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        d = pd.datetime.strptime(s, '%Y-%m-%d')
    return d


def my_savefig(plotdir, prefix, sensorstr, axisstr, hourstr, plottype):
    for ext in ['pdf', 'png']:
        outfile = os.path.join(plotdir, '_'.join([prefix, sensorstr, axisstr, hourstr]) + '_' + plottype + '.' + ext)
        plt.savefig( outfile )
        print 'saved figure %s' % outfile


def get_sensor_dataframe(sensor, f):
    unwanted_cols = [
        'sdn1',
        'sdn2',
        'sams' + sensor + 'RMSx0p1to6',
        'sams' + sensor + 'RMSy0p1to6',
        'sams' + sensor + 'RMSz0p1to6',
        'sams' + sensor + 'PSDx0p1to6',
        'sams' + sensor + 'PSDy0p1to6',
        'sams' + sensor + 'PSDz0p1to6',
        'sams' + sensor + 'FPKx0p1to6',
        'sams' + sensor + 'FPKy0p1to6',
        'sams' + sensor + 'FPKz0p1to6',
        'sams' + sensor + 'RMSx6to200',
        'sams' + sensor + 'RMSy6to200',
        'sams' + sensor + 'RMSz6to200',
        'sams' + sensor + 'PSDx6to200',
        'sams' + sensor + 'PSDy6to200',
        'sams' + sensor + 'PSDz6to200',
        'sams' + sensor + 'FPKx6to200',
        'sams' + sensor + 'FPKy6to200',
        'sams' + sensor + 'FPKz6to200',
        'sams' + sensor + 'RMS6to200',
    ]
    df = pd.read_csv(f, parse_dates=['t1', 't2'], date_parser=gmt_parse)
    rms1 = df['sams' + sensor + 'RMS0p1to6'].values
    rms2 = df['sams' + sensor + 'RMS6to200'].values
    rms3 = np.array([np.sqrt(a**2 + b**2) for a, b in zip(rms1, rms2)])
    df['sams' + sensor + 'RMS0p1to200'] = rms3

    # drop unwanted columns
    for c in unwanted_cols:
        df = df.drop(c, axis=1)

    return df


def main(glob_pat, sensor1, sensor2):

    # make output dir for plots
    plot_dir = os.path.join(os.path.dirname(glob_pat), 'plots')
    mkdir_p(plot_dir)

    # get lists of files
    file1 = glob.glob(glob_pat.replace('SENSOR', sensor1))[0]
    file2 = glob.glob(glob_pat.replace('SENSOR', sensor2))[0]

    df1 = get_sensor_dataframe(sensor1, file1)
    df2 = get_sensor_dataframe(sensor2, file2)

    # merge two sensors' dataframes based on time range
    result = pd.merge(df1, df2, how='outer', on=['t1', 't2'])

    # get rid of any rows that have NaN (or NaT)
    df = result.dropna()

    # create an hour column based on t1 column
    df['hour'] = df.apply(lambda row: row.t1.hour, axis=1)
    df = df.set_index(['hour'])

    # show hourly mean for each RMS column
    dfm = df.groupby(['hour']).mean()

    # plot low-freq (and high-freq) results
    #           REGIME       UNWANTED_COLS
    regimes = {'Low-Freq.':  ('RMS0p1to200', 90.0),
               'High-Freq.': ('RMS0p1to6', 9000.0)}
    for regime, tup in regimes.iteritems():
        suffix, upper = tup
        unwanted_cols = ['sams' + s + suffix for s in [sensor1, sensor2]]
        df_new = dfm.drop(unwanted_cols, axis=1)

        fig = plt.figure(1, figsize=(8, 6), dpi=300, facecolor='w', edgecolor='k')

        # plot bar chart
        ax = df_new.plot.bar(rot=0)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.set_ylabel('Acceleration (ug)')
        ax.set_xlabel('GMT Hour of Day')
        ax.set_ylim([0, upper])

        # title
        title_str = regime + 'Regime, Hourly Average Root-Mean-Square'
        plt.title(title_str, fontsize=12)

        # rework legend strings (e.g. old = 'sams121f03RMS0p1to6')
        L = plt.legend()
        for leg_entry in L.get_texts():
            old = leg_entry.get_text()
            new = old.lstrip('sams').replace('RMS', ': ').replace('p', '.').replace('to', ' to ') + ' Hz'
            leg_entry.set_text(new)

        # save figure
        out_file = '/tmp/' + regime + 'pdf'
        plt.savefig(out_file)
        print 'saved figure %s' % out_file

        plt.close(fig)


if __name__ == "__main__":

    sensor1, sensor2 = '121f03', '121f04'
    glob_pat = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_Rodent_Activity_2019-Aug/rmstracker_comprehensive_stats_for_rodent_2bands_SENSOR_rodent_active_subset.csv'

    main(glob_pat, sensor1, sensor2)
