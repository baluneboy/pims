#!/usr/bin/env python

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


def get_day_files(d, sensor, mindur=5, is_rev=True):
    ymd_dir = datetime_to_ymd_path(d)
    glob_pat = '%s/*_accel_%s/*%s' % (ymd_dir, sensor, sensor)
    fnames = glob.glob(glob_pat)
    files = get_pad_day_sensor_rate_mindur_files(fnames, d.strftime('%Y-%m-%d'), sensor, mindur=mindur)
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


def simple_demo_rev():

    # inputs
    fs = 500.0
    sensor = '121f08'
    min_dur = 5  # minutes
    start_str, stop_str = '2019-02-01', '2019-02-03'

    # get empty one-hour bucket to fill (bigger than we need)
    a = np.empty((0, 5), dtype=np.float32)    # float32 matches what we read from PAD file


    # get files for all of stop_str's day
    stop_day = parser.parse(stop_str).replace(hour=0, minute=0, second=0, microsecond=0)
    print stop_day.strftime('%Y-%m-%d'), '<< getting stop_day files before iteration begins'
    files = get_day_files(stop_day, sensor, mindur=min_dur)

    # get files for all of last_day
    last_day = stop_day - relativedelta(days=1)
    print last_day.strftime('%Y-%m-%d'), '<< getting last_day files before iteration begins'
    files += get_day_files(last_day, sensor, mindur=min_dur)

    # print 'len(files) = %d' % len(files)

    # create deque of files
    dfiles = deque(files)

    # iterate from last dh of prev_day's day/hour down to, and including start_str's day/hour
    dhr = pd.date_range(start_str, stop_str, freq='1H')[:-1]
    for dh in dhr[::-1]:  # fancy indexing gets us the reversed chronological ordering

        # if it's high noon, then get list of matching files for prior day and extend deque
        if dh.hour == 12:
            prior_day = dh.replace(hour=0) - relativedelta(days=1)
            print prior_day.strftime('%Y-%m-%d'), '<< high noon, so extending deque with prior day files'
            dfiles.extend(get_day_files(prior_day, sensor, mindur=min_dur))

        # print 'len(dfiles) = %d' % len(dfiles)

        # iterate over deque, popping only files that overlap Interval from dh:dh+relativedelta(hours=1)
        print dh.strftime('%Y-%m-%d/%H'), 'extracting (t,x,y,z,v) data from files for this dh'
        last_file = None
        while True:
            f = dfiles.popleft()
            fspan_relative = filespan_relativeto_dayhour(f, dh)

            if fspan_relative == 0:
                print 'extract', dh, 'part of', f
                last_file = f

            elif fspan_relative < 0:
                print 'before', dh, 'is', f
                dfiles.appendleft(f)
                if last_file is not None:
                    # print 'prepending', last_file
                    dfiles.appendleft(last_file)
                break

            elif fspan_relative > 0:
                print 'after', dh, 'is', f


if __name__ == '__main__':
    # old_demo()
    simple_demo_rev()
