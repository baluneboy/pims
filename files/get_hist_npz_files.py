#!/usr/bin/env python

import os
import glob
import pandas as pd
import numpy as np
from dateutil.parser import parse
from matplotlib import pyplot as plt


def get_npz_files(sensor, end, start=None, base_path='/misc/yoda/www/plots/batch/results/dailyhistpad'):
    """get hist NPZ files (for a given day(s)/sensor)"""

    if start is None:
        start = parse(end)  # - datetime.timedelta(days=7)
        # print start.date()

    npz_files = []
    for d in pd.date_range(start, end):
        # print d.date(), sensor, " > "

        # LIKE /misc/yoda/www/plots/batch/results/dailyhistpad/year2019/month08/day11/2019-08-11_121f03_hist_mat_500_mag.npz
        ymd = d.strftime('year%Y/month%m/day%d')
        glob_pat = os.path.join(base_path, ymd, '*_%s_hist_mat_*_mag.npz' % sensor)
        # print glob_pat
        day_files = glob.glob(glob_pat)
        npz_files.extend(day_files)

    return npz_files


def plot_cumpct__for_percentile_info(start, end, sensors):
    # get NPZ files (FIXME just focus on abs mag for now)
    start, end = '2019-08-01', '2019-08-21'
    ymd = start.split('-')
    ymd_str = os.path.join('year%s' % ymd[0], 'month%s' % ymd[1], 'day%s' % ymd[2])
    save_dir = os.path.join('/misc/yoda/www/plots/batch/results/dailyhistpad', ymd_str)
    for sensor in ['121f03', '121f04', 'es20']:
        npzs = get_npz_files(sensor, end, start=start)
        data = np.load(npzs[0])
        hx, hy, hz = data['hx'], data['hy'], data['hz']
        center, width = data['center'], data['width']
        # TODO find out why x-, y- and z-axis sums are different...should those always be identical?
        print np.sum(hx), np.sum(hy), np.sum(hz), npzs[0]
        for npz in npzs[1:]:
            data = np.load(npz)
            hx += data['hx']
            hy += data['hy']
            hz += data['hz']
            # TODO find out why x-, y- and z-axis sums are different...should those always be identical?
            print np.sum(hx), np.sum(hy), np.sum(hz), npz

        axpairs = [('x', hx), ('y', hy), ('z', hz)]
        for tup in axpairs:
            a, hh = tup[0], tup[1]
            fig, ax = plt.subplots()
            # ax.bar(center, hh/1e3, align='center', width=width)
            cpct = 100.0*np.cumsum(hh)/np.sum(hh)
            ax.plot(center, cpct)
            plt.xlabel('Accel. Magnitude (g)')
            plt.ylabel('Count (thousands)')
            plt.title('Histogram for %s, %s-Axis' % (sensor, a))
            suffix_str = '%s_%s' % (sensor, a)
            fname = os.path.join(save_dir, '%s_%s_%s.pdf' % (start, end, suffix_str))
            fig.savefig(fname)
            print 'evince %s &' % fname
            plt.close(fig)


def show_nth_percentile_info(start, end, sensors, nth=95):
    # get NPZ files (FIXME just focus on abs mag for now)
    start, end = '2019-08-01', '2019-08-21'
    out_str = 'From GMT %s to %s\n' % (start, end)
    for sensor in ['121f03', '121f04', 'es20']:
        out_str += 'For %s...' % sensor
        npzs = get_npz_files(sensor, end, start=start)
        data = np.load(npzs[0])
        hx, hy, hz = data['hx'], data['hy'], data['hz']
        center, width = data['center'], data['width']
        # TODO find out why x-, y- and z-axis sums are different...should those always be identical?
        print np.sum(hx), np.sum(hy), np.sum(hz), npzs[0]
        for npz in npzs[1:]:
            data = np.load(npz)
            hx += data['hx']
            hy += data['hy']
            hz += data['hz']
            # TODO find out why x-, y- and z-axis sums are different...should those always be identical?
            print np.sum(hx), np.sum(hy), np.sum(hz), npz

        axpairs = [('x', hx), ('y', hy), ('z', hz)]
        for tup in axpairs:
            a, hh = tup[0], tup[1]
            cpct = 100.0*np.cumsum(hh)/np.sum(hh)
            # print a, 1.0e3 * center[np.argmax(cpct>=95)], cpct[np.argmax(cpct>=95)]
            out_str += '\n{:s}: {:6.3f} mg, {:6.3f}th percentile'.format(a, 1.0e3 * center[np.argmax(cpct>=nth)], cpct[np.argmax(cpct>=nth)])

        out_str += '\n' + '-' * 44 + '\n'

    print out_str


if __name__ == "__main__":

    start, end = '2019-08-01', '2019-08-21'
    sensors = ['121f03', '121f04', 'es20']
    show_nth_percentile_info(start, end, sensors, nth=95)  # to show nth percentile (e.g. 95th) values (per-axis)
    # plot_cumpct__for_percentile_info(start, end, sensors)  # to plot to file cumulative percentage derived from hist

    # SEE grygier_rms_plucker in /home/pims/dev/programs/python/pims/sandbox/boxplot_minmaxrms.py for best/worst 4-hour
    # average across days that result from ensemble processing of grygier_counter.py results
