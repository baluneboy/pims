#!/usr/bin/env python

"""Running histogram(s) of OTOB grms values (per-axis and RSS).

This module provides classes for computing/plotting running OTOB histograms of OTO (mat files) data.

"""

import os
import glob
import datetime
import numpy as np
import pandas as pd
import scipy.io as sio
import itertools
# from pathlib import Path
from matplotlib import rc, pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.font_manager import FontProperties

import argparser
# from plumb_line import plumblines
from pims.mathbase.basics import round_up
from pims.utils.pimsdateutil import datetime_to_ymd_path, datetime_to_dailyhist_oto_path
from pims.utils.pimsdateutil import otomat_fullfilestr_to_start_stop, ymd_pathstr_to_date
from pims.files.filter_pipeline import FileFilterPipeline, OtoDaySensorHours
from histpad.pad_filter_pipeline import sensor2subdir
from pims.otorunhist.otomatfile import OtoMatFile, OtoParamFileException
from histpad.file_disposal import DailyOtoHistFileDisposal, DailyOtoMinMaxFileDisposal
# from ugaudio.explore import padread, pad_file_percentiles


DEFAULT_INDIR = argparser.DEFAULT_INDIR
DEFAULT_OUTDIR = argparser.DEFAULT_OUTDIR


class DateRangeException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


# def ranges(i):
#     """return range from a list of integers"""
#     for a, b in itertools.groupby(enumerate(i), lambda (x, y): y - x):
#         b = list(b)
#         yield b[0][1], b[-1][1]


def get_date_range(value):
    """return pandas date range object"""
    if value is None:
        # value is None, so set to most recent weeks' range
        dr = pd.date_range(DAYONE, periods=7, normalize=True)
    elif isinstance(value, list) and len(value) == 2:
        # a list of 2 objects, we will try to shoehorn into a pandas date_range
        try:
            dr = pd.date_range(value[0], value[1])
        except Exception as exc:
            raise DateRangeException(str(exc))
    elif isinstance(value, pd.DatetimeIndex):
        # ftw, we have pandas date_range as input arg
        dr = value
    else:
        # not None, not pd.DatetimeIndex and not len=2 list that nicely converted
        raise TypeError('see pandas for date_range info')
    return dr


# FIXME should we be using this instead of listdir(pth)?
def get_oto_day_sensor_files_taghours(files, day, sensor, hours=None):

    # handle hours default as all hours
    if hours is None:
        hours = [(0, 24), ]

    # initialize callable classes that act as filters for our pipeline
    file_filter1 = OtoDaySensorHours(day, sensor, hours)
    
    # initialize processing pipeline with callable classes, but not using file list as input yet
    ffp = FileFilterPipeline(file_filter1)
    #print ffp

    # now apply processing pipeline to file list; at this point, ffp is callable
    return list(ffp(files))


def get_out_mat_file_name(start, stop, sensor, taghrs):
    """return string for basename of output mat-file name"""
    # LIKE 2016-01-01_2016-01-31_121f03_sleep_all_wake.mat
    return '_'.join([start.strftime('%Y-%m-%d'), stop.strftime('%Y-%m-%d'), sensor] + taghrs.keys()) + '_otorunhist.mat'


def OBSOLETE_save_dailyhistoto(start, stop, sensor='121f03', taghours=None, bins=np.logspace(-12, -2, 11), indir=DEFAULT_INDIR, outdir=DEFAULT_OUTDIR, verbosity=None):
    """iterate over each day, then iterate over day's files & finally by taghours to build/sum results"""

    if verbosity <= 1:
        np.warnings.filterwarnings('ignore', r'All-NaN slice encountered')
        np.warnings.filterwarnings('ignore', r'invalid value encountered')
        np.warnings.filterwarnings('ignore', r'All-NaN axis encountered')

    if taghours is None:
        taghours = {'all': [(0, 24)]}

    dr = get_date_range([start, stop])
    for d in dr:
        
        day = d.strftime('%Y-%m-%d')
        
        # get list of OTO mat files for particular day, sensor and taghours
        pth = datetime_to_dailyhist_oto_path(d, sensor_subdir=sensor2subdir(sensor))

        # initialize file counts with same keys as taghours (count files for each tag)
        fcounts = dict.fromkeys(taghours.keys(), 0)

        # initialize dict to hold file index values, kind of a time-keeper per tag
        fidx = {}
        for k in taghours.keys():
            fidx[k] = []

        # dive down to process files in YMD/sensor path
        if os.path.exists(pth):

            # files = [n for n in [os.path.join(pth, f) for f in os.listdir(pth)] if n.endswith('%s.mat' % sensor)]
            unfiltered_files = [os.path.join(pth, f) for f in os.listdir(pth)]
            files = get_oto_day_sensor_files_taghours(unfiltered_files, day, sensor)

            if len(files) < 1:
                print 'no matching OTO mat files for %s' % pth
                continue

            # load particulars for very first file
            oto_mat1 = OtoMatFile(files[0])
            num_freqs = len(oto_mat1.data['foto'])

            # initialize FreqAxisTime (fat) array for this day/sensor
            fat_day = np.empty((len(files), num_freqs, 3))  # CAREFUL EMPTY INIT HAS GARBAGE VALUES
            fat_day[:] = np.nan  # NEED FILL IMMEDIATELY AFTER EMPTY TO CLEAN UP GARBAGE VALUES

            # initialize daily-ever-replacing stat arrays (init on first day only)
            if d == dr[0]:
                mins, maxs = np.empty((num_freqs, 3)), np.empty((num_freqs, 3))
                sums, counts = np.empty((num_freqs, 3)), np.empty((num_freqs, 3))
                mins[:] = np.inf
                maxs[:] = -np.inf
                sums[:] = 0.0
                counts[:] = 0
                out_pth = os.path.dirname(os.path.dirname(pth))

            # iterate over OTO mat files that we have to work with
            for c, f in enumerate(files):

                # verify OTO parameters from this file match the one from very 1st file
                oto_mat = OtoMatFile(f)
                if oto_mat != oto_mat1:
                    print 'mismatch in OTO mat file params for %s' % f
                    continue  # to next file since this one does not match

                # load data from file
                a = oto_mat.data

                # insert OTO's grms values at appropriate time index (c index) in Fx3xT fat array
                fat_day[:][:][c] = a['grms']

                # iterate over taghours items to keep track of c index values for each taghours item
                for tag, hrs in taghours.iteritems():

                    fstart, fstop = otomat_fullfilestr_to_start_stop(f)

                    for hrange in hrs:

                        h1 = datetime.datetime.combine(d.to_pydatetime().date(),
                                                  datetime.time(hrange[0], 0))
                        
                        # special handling of right end in hour range to capture hour 23 to end of day
                        if hrange[1] == 24:
                            hh, mm, ss = 23, 59, 59
                        else:
                            hh, mm, ss = hrange[1], 0, 0
                        h2 = datetime.datetime.combine(d.to_pydatetime().date(),
                                                       datetime.time(hh, mm, ss))

                        # if completely within hour range, then include with this tag
                        if fstart >= h1 and fstop <= h2:
                            fcounts[tag] += 1
                            fidx[tag].append(c)  # append file idx, c, to include w/ this tag

            print pth, fcounts,\
                '{:7d} non-NaNs in fat array for day {:s}'.\
                format(np.count_nonzero(~np.isnan(fat_day)), day)

            if verbosity > 1:
                print 'verbosity', verbosity

            # TODO this is where we use per-day fidx (indexing) for next phase of analysis
            for k, v in fidx.iteritems():
                # print '\t', k, len(v)  # np.nanmax(fat[np.array(v)], axis=0)
                # np.nanmin(fat[np.array(v)], axis=0)
                # np.nanmax(fat[np.array(v)], axis=0)
                # np.nansum(fat[np.array(v)], axis=0)
                # FOR COUNT, USE NEXT LINE:
                # np.divide(np.nansum(fat[np.array(v)], axis=0), np.nanmean(fat[np.array(v)], axis=0))

                if k in ['sleep', 'wake']:
                    continue

                print '{:>9s} accrued {:>4d} file indexes'.format(k, len(v)),
                print np.nanmin(fat_day[np.array(v)], axis=0).shape  # Fx3 array of mins per day&tag

                # replace evolving mins array in case this day's worth goes below in array sense
                np.fmin(mins, np.nanmin(fat_day[np.array(v)], axis=0), out=mins)
                # print 'MINS'; print mins[9:13][:]; print '-'*22

                # replace evolving maxs array in case this day's worth goes above in array sense
                np.fmax(maxs, np.nanmax(fat_day[np.array(v)], axis=0), out=maxs)
                # print 'MAXS'; print maxs[9:13][:]; print '+'*22

                # replace growing sums array with this day's contribution
                day_sum = np.nansum(fat_day[np.array(v)], axis=0)
                np.nansum(np.dstack((sums, day_sum)), axis=2, out=sums)
                # print 'SUMS'; print sums[9:13][:]; print 's'*22

                # add this day's count of non-NaN values onto growing counts array
                day_count = np.count_nonzero(~np.isnan(fat_day[np.array(v)]), axis=0)
                np.nansum(np.dstack((counts, day_count)), axis=2, out=counts)
                # print 'COUNTS'; print counts[9:13][:]; print 'c'*22

        else:

            print '%s had NO FILES to work with' % day

    out_name = get_out_mat_file_name(start, stop, sensor, taghours)
    out_mat_file_name = os.path.join(out_pth, out_name)

    mdict = {'sums': sums, 'counts': counts, 'mins': mins, 'maxs': maxs}
    sio.savemat(out_mat_file_name, mdict)
    print 'saved %s' % out_mat_file_name


def update_file_indexer_for_tags(c, f, taghours, fidx):
    """iterate over taghours items to keep track of c index values for each taghours item"""

    for tag, hrs in taghours.iteritems():

        fstart, fstop = otomat_fullfilestr_to_start_stop(f)
        h1_file = fstart.time()
        h2_file = fstop.time()

        # compensate for file times that straddle beginning or end of a day
        if h2_file < h1_file:
            if h2_file.hour <= 12:
                # straddles beginning of day
                h1_file = datetime.time(0, 0, 0)
            else:
                # straddles end of day
                h2_file = datetime.time(23, 59, 59)

        for hrange in hrs:

            # h1 = datetime.datetime.combine(d.to_pydatetime().date(),
            #                                datetime.time(hrange[0], 0))
            h1 = datetime.time(hrange[0], 0)

            # special handling of right end in hour range to capture hour 23 to end of day
            if hrange[1] == 24:
                hh, mm, ss = 23, 59, 59
            else:
                hh, mm, ss = hrange[1], 0, 0
            # h2 = datetime.datetime.combine(d.to_pydatetime().date(),
            #                                datetime.time(hh, mm, ss))
            h2 = datetime.time(hh, mm, ss)

            # if completely within hour range, then include with this tag
            if h1_file >= h1 and h2_file <= h2:
                fidx[tag].append(c)  # append file idx, c, to include w/ this tag


def save_dailyhistoto(start, stop, sensor='121f03', taghours=None, bins=np.logspace(-12, -2, 11), indir=DEFAULT_INDIR,
                      outdir=DEFAULT_OUTDIR, verbosity=None):
    """iterate over each day, then iterate over day's files & finally by taghours to build/sum results"""

    if verbosity <= 1:
        np.warnings.filterwarnings('ignore', r'All-NaN slice encountered')
        np.warnings.filterwarnings('ignore', r'invalid value encountered')
        np.warnings.filterwarnings('ignore', r'All-NaN axis encountered')
        np.warnings.filterwarnings('ignore', r'Mean of empty slice')

    if taghours is None:
        taghours = {'all': [(0, 24)]}

    # get list of files that we will build big array from F x 3 x K (K is num_files)
    files = []
    dr = get_date_range([start, stop])
    for d in dr:

        day = d.strftime('%Y-%m-%d')

        # get list of OTO mat files for particular day, sensor and taghours
        pth = datetime_to_dailyhist_oto_path(d, sensor_subdir=sensor2subdir(sensor))

        # dive down to process files in YMD/sensor path
        if os.path.exists(pth):
            unfiltered_files = [os.path.join(pth, f) for f in os.listdir(pth)]
            files += get_oto_day_sensor_files_taghours(unfiltered_files, day, sensor)

    print 'found %d files to work with' % len(files)

    # load frequency-grms array (and some parameters) from very first file
    oto_mat1 = OtoMatFile(files[0])
    num_freqs = len(oto_mat1.data['foto'])

    # initialize dict to hold file index values, kind of an index/time-keeper per tag
    fidx = {}
    for k in taghours.keys():
        fidx[k] = []

    # initialize big fat array with NaN's
    num_files = len(files)
    fat_array = np.empty((num_files, num_freqs, 3), dtype=float)
    fat_array[:] = np.nan  # NEED FILL IMMEDIATELY AFTER EMPTY TO CLEAN UP GARBAGE VALUES

    # iterate over OTO mat files to populate big fat array depth-wise with per-file Fx3 arrays
    for c, f in enumerate(files):

        # verify OTO parameters from this file match the one from very 1st file
        oto_mat = OtoMatFile(f)
        if oto_mat != oto_mat1:
            print 'mismatch in OTO mat file params for %s' % f
            continue  # to next file since this one does not match

        # update file index (time) tracker
        update_file_indexer_for_tags(c, f, taghours, fidx)

        # load data from file
        a = oto_mat.data

        # insert OTO's grms values at appropriate time index (c index) in Fx3xT big fat array
        fat_array[:][:][c] = a['grms']

    print fat_array.shape

    # for sleep_file in [files[i] for i in fidx['sleep']]:
    #     print sleep_file

    for k, v in fidx.iteritems():
        print k
        tag_mins = np.nanmin(fat_array[np.array(v)], axis=0)
        tag_maxs = np.nanmax(fat_array[np.array(v)], axis=0)
        tag_means = np.nanmean(fat_array[np.array(v)], axis=0)
        print tag_means[9:13, :]


if __name__ == '__main__':

    # PROCESS SLEEP/WAKE example
    # ./main.py -s SENSOR -d STARTDATE  -e STOPDATE   -t TAG1,h1,h2 TAG2,h3,h4
    # ./main.py -s 121f03 -d 2016-01-01 -e 2016-03-31 -t sleep,0,4  wake,8,16
    
    # PLOT example for daterange
    # ./main.py -s SENSOR -d STARTDATE  -e STOPDATE --plot
    # ./main.py -s 121f03 -d 2017-01-01 -e 2017-03-30 --plot
    
    # FROMFILE list of dates for this sensor
    # ./main.py -s es05 -f /home/pims/Documents/simple_test.txt
    # ./main.py -s es05 -f /home/pims/Documents/CIR_PaRIS_Based_on_es05_spgs_below_20hz_Quieter.txt

    # FIRST RUN THIS BASH (WITHOUT PLOTTING)
    # for F in 020 006 ""; do for S in es05 121f03; do for C in QUIET LOUD; do echo /home/pims/dev/programs/python/pims/padrunhist/main.py -s ${S}${F} -f /home/pims/Documents/CIR_PaRIS_Based_on_es05_spgs_below_20Hz_${C}ER.txt; done; done; done
    #
    # 2nd RUN THIS BASH (WITH PLOTTING)
    # for F in 020 006 ""; do for S in es05 121f03; do for C in QUIET LOUD; do echo /home/pims/dev/programs/python/pims/padrunhist/main.py -s ${S}${F} --plot -f /home/pims/Documents/CIR_PaRIS_Based_on_es05_spgs_below_20Hz_${C}ER.txt; done; done; done

    args = argparser.parse_inputs()

    # print args
    # raise SystemExit

    # handle the case when we get ad hoc dates from file (not typical date range)
    if args.fromfile is not None:
        
        raise Exception('FIXME: in a hurry for gateway, so skipping "fromfile" processing type [NEEDS WORK], for now')
        
        # for each date in list, verify padrunhist.mat exists along typical path (if not, then try to create it)
        oto_mat_files = process_date_list_from_file(args.fromfile, args.sensor)

        # parse tag out of fromfile name
        bname_noext = os.path.splitext(args.fromfile)[0]
        tag = bname_noext.split('_')[-1]

        if args.plot:
            # create plot for this ad hoc list of dates
            plotnsave_otomatfiles(oto_mat_files, args.sensor, tag)
        
    else:    
        if args.plot:
            raise Exception('FIXME: in a hurry for gateway, so skipping "plot" [NEEDS WORK], for now')        
            plotnsave_daterange_histoto(args.start, args.stop, sensor=args.sensor, taghours=args.taghours, verbosity=args.verbosity)
        else:
            # iterate over each day, then iterate over day's files & finally by taghours to build/sum results
            save_dailyhistoto(args.start, args.stop, sensor=args.sensor, taghours=args.taghours, indir=args.indir, outdir=args.outdir, verbosity=args.verbosity)
