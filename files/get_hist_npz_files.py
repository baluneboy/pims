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


if __name__ == "__main__":

    # get NPZ files (FIXME just focus on abs mag for now)
    start, end = '2019-08-01', '2019-08-21'
    for sensor in ['121f03', '121f04', 'es20']:
        npzs = get_npz_files(sensor, end, start=start)
        data = np.load(npzs[0])
        hx, hy, hz = data['hx'], data['hy'], data['hz']
        center, width = data['center'], data['width']
        print np.sum(hx), np.sum(hy), np.sum(hz), npzs[0]
        for npz in npzs[1:]:
            data = np.load(npz)
            hx += data['hx']
            hy += data['hy']
            hz += data['hz']
            print np.sum(hx), np.sum(hy), np.sum(hz), npz

        axpairs = [('x', hx), ('y', hy), ('z', hz)]

        for tup in axpairs:
            a, hh = tup[0], tup[1]
            fig, ax = plt.subplots()
            # ax.bar(center, hh/1e3, align='center', width=width)
            cpct = 100.0*np.cumsum(hh)/np.sum(hh)
            # print a, 1.0e3 * center[np.argmax(cpct>=95)], cpct[np.argmax(cpct>=95)]
            print '{:s}: {:6.3f} mg, {:6.3f}th percentile'.format(a, 1.0e3 * center[np.argmax(cpct>=95)], cpct[np.argmax(cpct>=95)])
            # ax.plot(center, cpct)
            # plt.xlabel('Accel. Magnitude (g)')
            # plt.ylabel('Count (thousands)')
            # plt.title('Histogram for %s, %s-Axis' % (sensor, a))
            # suffix_str = '%s_%s' % (sensor, a)
            # fname = '%s_%s.pdf' % (day_str, suffix_str)
            # fig.savefig(os.path.join(save_dir, fname))
            # print 'evince %s &' % fname
            # plt.show()
            # plt.close(fig)

        print 'for %s from GMT %s to %s' % (sensor, start, end)
