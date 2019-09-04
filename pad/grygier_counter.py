#!/usr/bin/env python

import os
import sys
import glob
import pandas as pd
import numpy as np
import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from collections import deque

from ugaudio.load import padread
from pims.padrunhist.main import get_pad_day_sensor_rate_mindur_files
from pims.utils.pimsdateutil import datetime_to_ymd_path, pad_fullfilestr_to_start_stop
from pims.pad.pad_buffer import PadBottomBuffer
from ugaudio.load import padread_hourpart

# input parameters
defaults = {
'start_str': '1983-12-01',       # string start day
'stop_str':          None,       # string stop day; None for start of next month after start_str's month
'sensor':        '121f03',       # string for sensor (e.g. 121f03 or 121f08006)
'fs':             '500.0',       # samples/second for data to be analyzed
'sec':           '3600.0',       # seconds of TSH data (v,x,y,z acceleration values) to summarize
'min_dur':          '5.0',       # minutes -- PAD file has at least this amount; otherwise skip file
'dry_run':        'False',       # boolean True to just dry run; False to actually run
}
parameters = defaults.copy()


def filespan_relativeto_dayhour(fullfilestr, dh):
    """return True if span suggested by PAD start/stop times overlaps any part of the hour in dh, a datetime object"""
    fstart, fstop = pad_fullfilestr_to_start_stop(fullfilestr)
    next_dh = dh + relativedelta(hours=1)
    ifile = pd.Interval(fstart, fstop, closed='both')
    ihour = pd.Interval(dh, next_dh, closed='left')
    if ifile.overlaps(ihour):
        return 0
    elif fstop < dh:
        return -1
    elif fstart >= next_dh:
        return +1


def get_day_files(d, sensor, fs, mindur=5, is_rev=True):
    """return list of files for given day, d, that match sensor, rate & min duration (sorted according to is_rev)"""
    ymd_dir = datetime_to_ymd_path(d)
    glob_pat = '%s/*_accel_%s/*%s' % (ymd_dir, sensor, sensor)
    fnames = glob.glob(glob_pat)
    files = get_pad_day_sensor_rate_mindur_files(fnames, d.strftime('%Y-%m-%d'), sensor, fs, mindur=mindur)
    files.sort(reverse=is_rev)
    return files


def old_demo():
    fs = 500.0
    sensor = '121f08'
    MINDUR = 5  # minutes
    start_str, stop_str = '2019-06-23', '2019-06-26'
    is_first_day = True
    files = []
    curr_dh = parser.parse(start_str)

    # iterate over date range of interest (excludes end date)
    dr = pd.date_range(start_str, stop_str, freq='1D')
    for d in dr[:-1]:

        if is_first_day:

            # get previous day's files
            prev_day = d - relativedelta(days=1)
            files = get_day_files(prev_day, sensor, mindur=MINDUR, is_rev=False)
            print prev_day.strftime('%Y-%m-%d'), len(files)
            is_first_day = False

        # get day's files
        files += get_day_files(d, sensor, mindur=MINDUR, is_rev=False)
        print d.strftime('%Y-%m-%d'), len(files)

        # FIXME this relies on sometimes faulty stop part of string in PAD filename
        # filter files to keep those with fstop > curr_dh's hour
        files = [f for f in files if pad_fullfilestr_to_start_stop(f)[1] > curr_dh]

        my_deck = deque(files)
        last_file = None
        while len(my_deck) > 0:
            f = my_deck.popleft()
            fspan_relative = filespan_relativeto_dayhour(f, curr_dh)

            if fspan_relative == 0:
                print 'extract', curr_dh, 'part of', f
                last_file = f

            elif fspan_relative < 0:
                print 'before', curr_dh, 'is', f
                raise Exception('this should never happen???')

            elif fspan_relative > 0:
                if last_file is not None:
                    # print 'prepending', last_file
                    my_deck.appendleft(last_file)
                curr_dh += relativedelta(hours=1)
                print 'current dh now', curr_dh

        print '-' * 55


    # # arr = np.empty((0, 4))
    # for fname in fnames_filt:
    #     # read data from file (not using double type here like MATLAB would, so we get courser demeaning)
    #     b = padread(fname)
    #     a = b - b.mean(axis=0)  # demean each column
    #     # a = np.delete(a, 0, 1)       # delete first (time) column
    #     a[:, 0] = np.sqrt(a[:, 1] ** 2 + a[:, 2] ** 2 + a[:, 3] ** 2)  # replace 1st column with vecmag
    #     p = np.percentile(np.abs(a), 99, axis=0)
    #     # print '{:e}  {:e}  {:e}  {:e}'.format(*p)
    #     # arr = np.append(arr, [p], axis=0)
    #     # print arr
    #     print p, fname


def run_reverse(sensor, fs, start_str, stop_str, sec=3600.0, min_dur=5.0):
    """iterate backwards through time to get files, load data and process on hourly basis writing to interim CSV file"""

    # print sensor, fs, start_str, stop_str, sec, min_dur
    # raise SystemExit

    # create stub string for csv_file
    csv_dir = '/misc/yoda/www/plots/batch/results/monthly_minmaxrms'

    # get files for all of stop_str's day
    stop_day = parser.parse(stop_str).replace(hour=0, minute=0, second=0, microsecond=0)
    print stop_day.strftime('%Y-%m-%d'), '<< getting stop_day files before iteration begins'
    files = get_day_files(stop_day, sensor, fs, mindur=min_dur)

    # get files for all of last_day
    last_day = stop_day - relativedelta(days=1)
    print last_day.strftime('%Y-%m-%d'), '<< getting last_day files before iteration begins'
    files += get_day_files(last_day, sensor, fs, mindur=min_dur)

    # print 'len(files) = %d' % len(files)

    # create deque of files
    dfiles = deque(files)

    # iterate from last dh of prev_day's day/hour down to, and including start_str's day/hour
    dhr = pd.date_range(start_str, stop_str, freq='1H')[:-1]
    for dh in dhr[::-1]:  # note: fancy indexing here gets us the reversed chronological ordering for dhr iteration

        # create data buffer
        buffer = PadBottomBuffer(fs, sec)

        # check if deque of files is empty, extend as needed
        dfiles_empty = False if dfiles else True
        if dfiles_empty:
            days_ago = 0
            while dfiles_empty:
                days_ago += 1
                prior_day = dh.replace(hour=0) - relativedelta(days=days_ago)
                print prior_day.strftime('%Y-%m-%d'), '<< deque of files empty, so extending deque with prior day files'
                prior_day_files = get_day_files(prior_day, sensor, fs, mindur=min_dur)
                dfiles.extend(prior_day_files)
                print 'extended deque by adding %d more files from %s' % (len(prior_day_files), prior_day.strftime('%Y-%m-%d'))
                dfiles_empty = False if dfiles else True

        # # if it's high noon, then get list of matching files for prior day and extend deque
        # if dh.hour == 12:
        #     prior_day = dh.replace(hour=0) - relativedelta(days=1)
        #     print prior_day.strftime('%Y-%m-%d'), '<< high noon, so extending deque with prior day files'
        #     prior_day_files = get_day_files(prior_day, sensor, fs, mindur=min_dur)
        #     dfiles.extend(prior_day_files)
        #     print 'extended deque by adding %d more files from %s' % (len(prior_day_files), prior_day.strftime('%Y-%m-%d'))

        # print 'len(dfiles) = %d' % len(dfiles)

        # iterate over deque, popping only files that overlap Interval from dh:dh+relativedelta(hours=1)
        print dh.strftime('%Y-%m-%d/%H'), 'extracting (t,x,y,z,v) data from files for this dh'
        last_file = None
        while True:
            if dfiles:
                f = dfiles.popleft()
                fspan_relative = filespan_relativeto_dayhour(f, dh)

                if fspan_relative == 0:
                    a = padread_hourpart(f, fs, dh)
                    buffer.add(a)
                    print 'extract', dh, 'part of', f, 'count =', np.count_nonzero(~np.isnan(buffer.vxyz[:, 0]))
                    last_file = f

                elif fspan_relative < 0:
                    dfiles.appendleft(f)
                    if last_file is not None:
                        # print 'prepending', last_file
                        dfiles.appendleft(last_file)
                    #ex /misc/yoda/www/plots/batch/results/monthly_minmaxrms/year1983/month12/1983-12_121f00_minmaxrms.csv
                    ym_subdir = dh.strftime('year%Y/month%m')
                    csv_name = '_'.join([dh.strftime('%Y-%m'), sensor, 'minmaxrms.csv'])
                    csv_file = os.path.join(csv_dir, ym_subdir, csv_name)
                    if not os.path.exists(os.path.dirname(csv_file)):
                        os.makedirs(os.path.dirname(csv_file))
                    if not os.path.exists(csv_file):
                        labels = 'date,hour,'
                        labels += 'vmin(g),xmin(g),ymin(g),zmin(g),'
                        labels += 'vmax(g),xmax(g),ymax(g),zmax(g),'
                        labels += 'vrms(g),xrms(g),yrms(g),zrms(g)\n'
                        # labels += 'xmag(g),ymag(g),zmag(g)\n'
                        with open(csv_file, 'w') as fd:
                            fd.write(labels)
                    buffer.append_to_csv(csv_file, dh)
                    print 'before', dh, 'is', f, csv_file
                    break

                elif fspan_relative > 0:
                    print 'after', dh, 'is', f

            else:

                print 'no more files to pop from deque'

                # deque of files is empty, extend as needed
                dfiles_empty = True
                if dfiles_empty:
                    days_ago = 0
                    while dfiles_empty:
                        days_ago += 1
                        prior_day = dh.replace(hour=0) - relativedelta(days=days_ago)
                        print prior_day.strftime('%Y-%m-%d'), '<< deque of files empty, so extending deque with prior day files'
                        prior_day_files = get_day_files(prior_day, sensor, fs, mindur=min_dur)
                        dfiles.extend(prior_day_files)
                        print 'extended deque by adding %d more files from %s' % (len(prior_day_files), prior_day.strftime('%Y-%m-%d'))
                        dfiles_empty = False if dfiles else True


def parameters_ok():
    """check for reasonableness of parameters"""

    # convert start day to date object
    try:
        start = parser.parse(parameters['start_str'])
        parameters['start_str'] = str(start.date())
    except Exception, e:
        print 'could not get start_str input as date object: %s' % e.message
        return False

    # convert stop day to date object
    if parameters['stop_str'] is None:
        stop = start + relativedelta(months=1)
        parameters['stop_str'] = str(stop.date())
    else:
        try:
            parameters['stop_str'] = str(parser.parse(parameters['stop_str']).date())
        except Exception, e:
            print 'could not get stop_str input as date object: %s' % e.message
            return False

    # convert fs to float
    try:
        parameters['fs'] = float(parameters['fs'])
    except Exception, e:
        print 'could not convert fs to float: %s' % e.message
        return False

    # convert sec to float
    try:
        parameters['sec'] = float(parameters['sec'])
    except Exception, e:
        print 'could not convert sec to float: %s' % e.message
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
    """print short description of how to run the program"""

    print 'USAGE:    %s [options]' % os.path.abspath(__file__)
    print 'EXAMPLE1: %s # FOR DEFAULTS' % os.path.abspath(__file__)
    print 'EXAMPLE2: %s dry_run=True sensor=es20 fs=500 start_str=2019-05-01 stop_str=2019-07-01 # DRY RUN' % os.path.abspath(__file__)
    print 'EXAMPLE3: %s sensor=es20 fs=500 start_str=2019-05-01 stop_str=2019-07-01 # ACTUAL RUN' % os.path.abspath(__file__)


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
            # print parameters
            run_reverse(parameters['sensor'], parameters['fs'], parameters['start_str'],
                        parameters['stop_str'], sec=parameters['sec'], min_dur=parameters['min_dur'])
            return 0

    print_usage()

# FIXME dry_run input arg does nothing at the moment - it'd be nice if it traced run w/o actually loading files or calc


# ----------------------------------------------------------------------
# EXAMPLES:
# put example(s) here
if __name__ == '__main__':

    sys.exit(main(sys.argv))
