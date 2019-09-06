#!/usr/bin/env python

import os
import sys
import glob
import datetime
from dateutil import parser
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

from ugaudio.load import padread
from pims.pad.grygier_counter import get_day_files
from pims.files.utils import mkdir_p

_TWODAYSAGO = (datetime.datetime.now().date() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')

# input parameters
defaults = {
'start':      _TWODAYSAGO,       # string start day
'stop':              None,       # string stop day
'sensor':        '121f03',       # string for sensor (e.g. 121f03 or 121f08006)
'fs':             '500.0',       # samples/second for data to be analyzed
'min_dur':          '5.0',       # minutes -- PAD file has at least this amount; otherwise skip file
'dry_run':        'False',       # boolean True to just dry run; False to actually run
}
parameters = defaults.copy()


def load_file(filename, show_files=False):
    # read data from file (not using double type here like MATLAB would, so we get courser demeaning)
    b = padread(filename)

    # demean each column
    a = b - b.mean(axis=0)

    if show_files:
        print '{0:s}, {1:>.4e}, {2:>.4e}, {3:>.4e}, {4:>.4e}, {5:>.4e}, {6:>.4e}'.format(filename,
                                           a.min(axis=0)[1], a.max(axis=0)[1], a.min(axis=0)[2],
                                           a.max(axis=0)[2], a.min(axis=0)[3], a.max(axis=0)[3] )

    return a


def load_hist_params(vecmag=False):

    if vecmag:
        datamin, datamax, numbins = 0.0, 0.05, 800
    else:
        datamin, datamax, numbins = -0.05, 0.05, 1000

    bins = np.linspace(datamin, datamax, numbins)
    hx = np.zeros(numbins-1, dtype='int64')
    hy = np.zeros(numbins-1, dtype='int64')
    hz = np.zeros(numbins-1, dtype='int64')

    return datamin, datamax, numbins, bins, hx, hy, hz


def parameters_ok():
    """check for reasonableness of parameters"""

    # convert start day to date object
    try:
        start = parser.parse(parameters['start'])
        parameters['start'] = str(start.date())
    except Exception, e:
        print 'could not get day input as date object: %s' % e.message
        return False

    # convert stop day to date object
    if parameters['stop'] is None:
        stop = start
        parameters['stop'] = str(stop.date())
    else:
        try:
            parameters['stop'] = str(parser.parse(parameters['stop']).date())
        except Exception, e:
            print 'could not get stop input as date object: %s' % e.message
            return False

    # convert fs to float
    try:
        parameters['fs'] = float(parameters['fs'])
    except Exception, e:
        print 'could not convert fs to float: %s' % e.message
        return False

    # convert min_dur to float
    try:
        parameters['min_dur'] = float(parameters['min_dur'])
    except Exception, e:
        print 'could not convert min_dur to float: %s' % e.message
        return False

    # convert dry_run to boolean
    try:
        parameters['dry_run'] = True if parameters['dry_run'].lower() in ['true', '1', 'yes', 'y'] else False
    except Exception, e:
        print 'could not convert dry_run to boolean: %s' % e.message
        return False

    return True  # params are OK; otherwise, we returned False above


def print_usage():
    print "print short description of how to run the program"""
    #
    # print 'USAGE:    %s [options]' % os.path.abspath(__file__)
    # print 'EXAMPLE1: %s # FOR DEFAULTS' % os.path.abspath(__file__)
    # print 'EXAMPLE2: %s dry_run=True sensor=es20 fs=500 start_str=2019-05-01 stop_str=2019-07-01 # DRY RUN' % os.path.abspath(__file__)
    # print 'EXAMPLE3: %s sensor=es20 fs=500 start_str=2019-05-01 stop_str=2019-07-01 # ACTUAL RUN' % os.path.abspath(__file__)


def run_hist(day, sensor, fs, mindur=5, is_rev=False, show_files=True):

    # FIXME these bins will best come by doing some homework for say the past umpteen years (all 200 Hz SAMS data)

    # get histogram parameters
    dmin, dmax, nbins, bins, hx, hy, hz = load_hist_params(vecmag=False)
    dmina, dmaxa, nbinsa, binsa, hxa, hya, hza = load_hist_params(vecmag=True)

    # get files
    files = get_day_files(day, sensor, fs, mindur=mindur, is_rev=is_rev)

    for f in files:

        a = load_file(f, show_files=show_files)

        xhist, junk = np.histogram(a[:, 1], bins)
        yhist, junk = np.histogram(a[:, 2], bins)
        zhist, junk = np.histogram(a[:, 3], bins)

        hx += xhist
        hy += yhist
        hz += zhist

        xhista, junk = np.histogram(np.abs(a[:, 1]), binsa)
        yhista, junk = np.histogram(np.abs(a[:, 2]), binsa)
        zhista, junk = np.histogram(np.abs(a[:, 3]), binsa)

        hxa += xhista
        hya += yhista
        hza += zhista

    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2

    widtha = 0.7 * (binsa[1] - binsa[0])
    centera = (binsa[:-1] + binsa[1:]) / 2

    fs_str = '%.0f' % fs
    bdir = '/misc/yoda/www/plots/batch/results/dailyhistpad'
    ymd_str = day.strftime('year%Y/month%m/day%d')
    day_str = day.strftime('%Y-%m-%d')
    suffix_str = '%s_hist_mat_%s' % (sensor, fs_str)
    mat_name = '%s_%s' % (day_str, suffix_str)
    save_dir = os.path.join(bdir, ymd_str)
    mkdir_p(save_dir)
    np.savez(os.path.join(save_dir, mat_name),
             width=width, center=center, dmin=dmin, dmax=dmax, nbins=nbins, bins=bins, hx=hx, hy=hy, hz=hz)
    print 'saved %s' % mat_name

    suffix_str = '%s_hist_mat_%s_mag' % (sensor, fs_str)
    mat_name = '%s_%s' % (day_str, suffix_str)
    np.savez(os.path.join(save_dir, mat_name),
             width=widtha, center=centera, dmin=dmina, dmax=dmaxa, nbins=nbinsa, bins=binsa, hx=hxa, hy=hya, hz=hza)
    print 'saved %s' % mat_name

    hh = {'x': (hx, hxa), 'y': (hy, hya), 'z': (hz, hza)}

    for h in ['x', 'y', 'z']:

        fig, ax = plt.subplots()
        ax.bar(center, hh[h][0], align='center', width=width)
        plt.xlabel('Accel. (g)')
        plt.ylabel('Count')
        plt.title('Histogram for %s, %s-Axis' % (sensor, h))
        suffix_str = '%s_%s_%s' % (sensor, h, fs_str)
        fname = '%s_%s.pdf' % (day_str, suffix_str)
        fig.savefig(os.path.join(save_dir, fname))
        print 'evince %s &' % fname
        plt.close(fig)

        figa, axa = plt.subplots()
        axa.bar(centera, hh[h][1], align='center', width=widtha)
        plt.xlabel('Accel. (g)')
        plt.ylabel('Count')
        plt.title('Vector Magnitude Histogram for %s, %s-Axis' % (sensor, h))
        fnamea = '%s_%s_mag.pdf' % (day_str, suffix_str)
        figa.savefig(os.path.join(save_dir, fnamea))
        print 'evince %s &' % fnamea
        plt.close(figa)


def main(argv):
    """parse input arguments and run routine that reverses through time to process file-by-file"""

    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if 2 != len(pair):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parameters_ok():
            # print parameters; raise SystemExit
            for d in pd.date_range(parameters['start'], parameters['stop']):
                 day = d.to_pydatetime().date()
                 # print day
                 run_hist(day, parameters['sensor'], parameters['fs'])
            return 0

        print_usage()

# FIXME change NPZ output file names from like:
# FIXME 2019-08-21_es20006_hist_mat_142.0   or 2019-08-21_es20006_hist_mat_142.0_mag    to like:
# FIXME 2019-08-21_es20006_hist_mat_142.npz or 2019-08-21_es20006_hist_mat_142_mag.npz

# FIXME histogram plot title include date & small font total pts
# FIXME histogram ylabel "Count (thousands)" & scale counts for this during plot
# FIXME overlay x-, y- and z-axis all on same plot with legend (lines, not bars)

# FIXME dry_run input arg does nothing at the moment - it'd be nice if it traced run w/o actually loading files or calc


# ----------------------------------------------------------------------
# EXAMPLES:
# put example(s) here
if __name__ == '__main__':
    sys.exit(main(sys.argv))
