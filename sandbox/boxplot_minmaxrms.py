#!/usr/bin/env python

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def p1(a):
    return np.nanpercentile(a, 1)


def p25(a):
    return np.nanpercentile(a, 25)


def p75(a):
    return np.nanpercentile(a, 75)


def p99(a):
    return np.nanpercentile(a, 99)


def box_plotter(vstr, df, pdf_out):
    """boxplot (Tufte style) for min/max/rms hourly percentile summary"""

    fig, ax = plt.subplots(figsize=(11, 8.5))

    # draw horizontal lines at median values in red
    hour_mins = np.arange(-0.25, 23.75, 1.0)
    hour_maxs = np.arange(0.25, 23.75, 1.0)
    meds = df.xs('median', level=1, axis=1)
    plt.hlines(y=meds, xmin=hour_mins, xmax=hour_maxs, linewidth=3.5, alpha=0.75, color='red')

    # draw lower, vertical (whisker) lines from 1st to 25th percentiles in black
    bot = df.xs('p1', level=1, axis=1)[vstr].values
    top = df.xs('p25', level=1, axis=1)[vstr].values
    plt.vlines(x=np.arange(0, 24, 1), ymin=bot, ymax=top, linewidth=3.5, alpha=0.75, color='blue')

    # draw upper, vertical (whisker) lines from 75th to 99th percentiles in black
    bot = df.xs('p75', level=1, axis=1)[vstr].values
    top = df.xs('p99', level=1, axis=1)[vstr].values
    plt.vlines(x=np.arange(0, 24, 1), ymin=bot, ymax=top, linewidth=3.5, alpha=0.75, color='blue')

    plt.yscale('log')

    plt.xlim(-1, 24)
    plt.ylim(5e-6, 1e-2)

    plt.xticks(np.arange(0, 24, 1))
    plt.grid(True, which='both', axis='both', alpha=0.25)

    plt.xlabel('GMT Hour')
    plt.ylabel('Acceleration (g)')

    pdf_file = pdf_out.replace('minmaxrms_summary.pdf', vstr + '_pctile_summary.pdf').replace('(g)', '')

    k = os.path.basename(pdf_file).replace('.pdf', '').split('_')
    title_str = 'GMT Span from {0} to {1}, Sensor {2}, Var = {3}'.format(*k[0:4])
    plt.title(title_str)
    fig.savefig(pdf_file, pad_inches=(1.0, 1.0))

    print('wrote %s' % pdf_file)


def get_files(start_month_str, stop_month_str, sensor, base_dir='G:\data\monthly_minmaxrms'):
    """return list of monthly files that match sensor in range from start:stop"""
    csv_files = []
    ymr = pd.date_range(start_month_str, stop_month_str, freq='1M')
    for ym in ymr:
        fname = '_'.join(['%d-%02d' % (ym.year, ym.month), sensor, 'minmaxrms.csv'])
        csv_file = os.path.join(base_dir, 'year%d' % ym.year, 'month%02d' % ym.month, fname)
        if os.path.exists(csv_file):
            csv_files.append(csv_file)
        else:
            print('does NOT exist', csv_file)
    return csv_files


def grygier_summary_stdout(start_month_str, stop_month_str, sensor, base_dir='G:\data\monthly_minmaxrms'):
    """write stdout summary of hourly min/max/rms stats presumably over a long time span"""

    # set pandas display options
    pd.options.display.float_format = ' {:,.4e}'.format
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # build output filename
    csv_fname_out = '_'.join([start_month_str, stop_month_str, sensor, 'minmaxrms', 'summary.csv'])
    csv_file_out = os.path.join(base_dir, csv_fname_out)

    # get source csv files that were produced by grygier_counter.py
    csv_files = get_files(start_month_str, stop_month_str, sensor, base_dir=base_dir)

    # read first file into dataframe
    df = pd.read_csv(csv_files[0])

    # concatenate remaining files onto dataframe
    for f in csv_files[1:]:
        df2 = pd.read_csv(f)
        df = pd.concat([df, df2], ignore_index=True)

    # compute per-axis value (called "mag") that is max(abs(ymin, ymax))
    df['xmag(g)'] = df.apply(lambda row: np.max([np.abs(row['xmin(g)']), np.abs(row['xmax(g)'])]), axis=1)
    df['ymag(g)'] = df.apply(lambda row: np.max([np.abs(row['ymin(g)']), np.abs(row['ymax(g)'])]), axis=1)
    df['zmag(g)'] = df.apply(lambda row: np.max([np.abs(row['zmin(g)']), np.abs(row['zmax(g)'])]), axis=1)

    # enumerate columns to be summarized on hourly basis
    vals = [
        'xmag(g)',
        'ymag(g)',
        'zmag(g)',
        'vmax(g)',
        'xrms(g)',
        'yrms(g)',
        'zrms(g)',
        'vrms(g)',
    ]

    # iterate over values to be summarized, group and compute aggregate functions (percentiles, min, max)
    for v in vals:
        my_group = df.groupby('hour').agg({v: [p1, p25, 'median', p75, p99, 'min', 'max']})
        print(my_group.T)


def grygier_summary_csvfile(start_month_str, stop_month_str, sensor, base_dir='G:\data\monthly_minmaxrms'):
    """write csv file summary of hourly min/max/rms stats presumably over a long time span"""

    # set pandas display options
    pd.options.display.float_format = ' {:,.4e}'.format
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # build output filename
    csv_fname_out = '_'.join([start_month_str, stop_month_str, sensor, 'minmaxrms', 'summary.csv'])
    csv_file_out = os.path.join(base_dir, csv_fname_out)

    # get source csv files that were produced by grygier_counter.py
    csv_files = get_files(start_month_str, stop_month_str, sensor, base_dir=base_dir)

    # read first file into dataframe
    df = pd.read_csv(csv_files[0])

    # concatenate remaining files onto dataframe
    for f in csv_files[1:]:
        df2 = pd.read_csv(f)
        df = pd.concat([df, df2], ignore_index=True)

    # compute per-axis value (called "mag") that is max(abs(ymin, ymax))
    df['xmag(g)'] = df.apply(lambda row: np.max([np.abs(row['xmin(g)']), np.abs(row['xmax(g)'])]), axis=1)
    df['ymag(g)'] = df.apply(lambda row: np.max([np.abs(row['ymin(g)']), np.abs(row['ymax(g)'])]), axis=1)
    df['zmag(g)'] = df.apply(lambda row: np.max([np.abs(row['zmin(g)']), np.abs(row['zmax(g)'])]), axis=1)

    # enumerate columns to be summarized on hourly basis
    vals = [
        'xmag(g)',
        'ymag(g)',
        'zmag(g)',
        'vmax(g)',
        'xrms(g)',
        'yrms(g)',
        'zrms(g)',
        'vrms(g)',
    ]

    # iterate over values to be summarized, group and compute aggregate functions (percentiles, min, max)
    csv_strings = ''
    for v in vals:
        my_group = df.groupby('hour').agg({v: [p1, p25, 'median', p75, p99, 'min', 'max']})
        # boxplotter(my_group)
        csv_strings += my_group.T.to_csv(index=True)
    # print(csv_strings)

    # write to output csv file
    with open(csv_file_out, 'w', newline='') as fd:
        fd.write(csv_strings)

    print('wrote %s' % csv_file_out)


def grygier_summary_boxplot(start_month_str, stop_month_str, sensor, base_dir='G:\data\monthly_minmaxrms'):
    """write boxplot summary of hourly min/max/rms stats presumably over a long time span"""

    # set pandas display options
    pd.options.display.float_format = ' {:,.4e}'.format
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # build output filename
    box_fname_out = '_'.join([start_month_str, stop_month_str, sensor, 'minmaxrms', 'summary.pdf'])
    box_file_out = os.path.join(base_dir, box_fname_out)

    # get source csv files that were produced by grygier_counter.py
    csv_files = get_files(start_month_str, stop_month_str, sensor, base_dir=base_dir)

    # read first file into dataframe
    df = pd.read_csv(csv_files[0])

    # concatenate remaining files onto dataframe
    for f in csv_files[1:]:
        df2 = pd.read_csv(f)
        df = pd.concat([df, df2], ignore_index=True)

    # compute per-axis value (called "mag") that is max(abs(ymin, ymax))
    df['xmag(g)'] = df.apply(lambda row: np.max([np.abs(row['xmin(g)']), np.abs(row['xmax(g)'])]), axis=1)
    df['ymag(g)'] = df.apply(lambda row: np.max([np.abs(row['ymin(g)']), np.abs(row['ymax(g)'])]), axis=1)
    df['zmag(g)'] = df.apply(lambda row: np.max([np.abs(row['zmin(g)']), np.abs(row['zmax(g)'])]), axis=1)

    # enumerate columns to be summarized on hourly basis
    vals = [
        'xmag(g)',
        'ymag(g)',
        'zmag(g)',
        'vmax(g)',
        'xrms(g)',
        'yrms(g)',
        'zrms(g)',
        'vrms(g)',
    ]

    # iterate over values to be summarized, group and compute aggregate functions (percentiles, min, max)
    for v in vals:
        my_group = df.groupby('hour').agg({v: [p1, p25, 'median', p75, p99, 'min', 'max']})
        box_plotter(v, my_group, box_file_out)



if __name__ == '__main__':

    start_month_str = '2018-12'
    stop_month_str = '2019-07'
    sensors = ['121f03006', '121f08006']
    for sensor in sensors:
        # grygier_summary_stdout(start_month_str, stop_month_str, sensor)
        # grygier_summary_csvfile(start_month_str, stop_month_str, sensor)
        grygier_summary_boxplot(start_month_str, stop_month_str, sensor)
