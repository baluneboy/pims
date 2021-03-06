#!/usr/bin/env python

"""Running histogram(s) of OTOB grms values (per-axis and RSS).

This module provides classes for computing/plotting running OTOB histograms of OTO (mat files) data.

"""

import os
import cPickle as pkl
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
import matplotlib.cbook as cbook


DEFAULT_INDIR = argparser.DEFAULT_INDIR
DEFAULT_OUTDIR = argparser.DEFAULT_OUTDIR
AXMAP = {'x': 0, 'y': 1, 'z': 2, 'v': 3}


class DateRangeException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


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


def get_oto_day_sensor_files_taghours(files, day, sensor, hours=None, verbosity=0):
    """return list of files that match day, sensor and hours criteria"""

    # handle hours; default as all hours
    if hours is None:
        hours = [(0, 24), ]

    # initialize callable classes that act as filters for our pipeline
    file_filter1 = OtoDaySensorHours(day, sensor, hours)
    
    # initialize processing pipeline with callable classes, but not using file list as input yet
    ffp = FileFilterPipeline(file_filter1)

    if verbosity > 1:
        print ffp

    # now apply processing pipeline to input files list
    return list(ffp(files))


def get_pickle_filename(start, stop, sensor, taghrs):
    """return string for basename of output mat-file name"""
    # LIKE 2016-01-01_2016-01-31_121f03_sleep_all_wake.mat
    return '_'.join([start.strftime('%Y-%m-%d'), stop.strftime('%Y-%m-%d'), sensor] + taghrs.keys()) + '_otorunhist.pkl'


def get_out_png_file_name(start, stop, sensor, tag):
    """return string for basename of output png filename"""
    # LIKE 2016-01-01_2016-01-31_121f03_sleep.png
    return '_'.join([start.strftime('%Y-%m-%d'), stop.strftime('%Y-%m-%d'), sensor] + [tag,]) + '_otorunhist.png'


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

    out_name = get_pickle_filename(start, stop, sensor, taghours)
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


def save_otorunhist_pickle_file(start, stop, sensor='121f03', taghours=None, verbosity=0):
    """save mat file with fat_array, filenames and file index for tag hours in day range"""

    # turn off some numpy warnings
    if verbosity <= 1:
        np.warnings.filterwarnings('ignore', r'All-NaN slice encountered')
        np.warnings.filterwarnings('ignore', r'Invalid value encountered')
        np.warnings.filterwarnings('ignore', r'All-NaN axis encountered')
        np.warnings.filterwarnings('ignore', r'Mean of empty slice')

    # we always want at least this tag
    if taghours is None:
        taghours = {'all': [(0, 24)]}

    # get list of files that we will build big fat_array from KxFx4 (F is num_freqs, K is num_files, 4 axes)
    files = []
    dr = get_date_range([start, stop])
    # print 'date range: {} to {}'.format(dr[0].strftime('%Y-%m-%d'), dr[-1].strftime('%Y-%m-%d'))

    for dt64 in dr:

        d = pd.to_datetime(dt64)
        day = d.strftime('%Y-%m-%d')

        # get list of OTO mat files for particular day, sensor and taghours
        pth = datetime_to_dailyhist_oto_path(d, sensor_subdir=sensor2subdir(sensor))

        # dive down to process files in YMD/sensor path
        print 'looking for files under %s' % pth,
        if os.path.exists(pth):
            unfiltered_files = [os.path.join(pth, f) for f in os.listdir(pth)]
            files += get_oto_day_sensor_files_taghours(unfiltered_files, day, sensor)
            print 'file sub-total is now %d files' % len(files)
        else:
            print 'path does not exist so skip it'

    out_pth = os.path.dirname(os.path.dirname(pth))

    print 'total of %d files were found' % len(files)

    # load frequency-grms array (and some parameters) from very first file
    oto_mat1 = OtoMatFile(files[0])
    freq_bands = oto_mat1.data['foto'].reshape((-1, 2))   # -1 tells numpy to infer first dimension
    freqs = np.mean(freq_bands, axis=1).reshape((-1, 1))  # reshape as column array via (-1, 1)
    num_freqs = len(freqs)

    # initialize dict to hold file index values, kind of an index/time-keeper per tag
    fidx = {}  # LIKE Dict[tag_str, List[hour_ranges]]
    for k in taghours.keys():
        fidx[k] = list()

    # initialize big fat_array with NaN's (add a 4th column after XYZ for v=RSS(x,y,z))
    num_files = len(files)
    fat_array = np.empty((num_files, num_freqs, 4), dtype=float)
    fat_array[:] = np.nan  # NEED THIS NAN-FILL IMMEDIATELY AFTER EMPTY TO CLEAN UP GARBAGE VALUES

    # iterate over OTO mat files to populate big fat_array depth-wise with per-file Fx4 arrays
    for c, f in enumerate(files):

        # verify OTO parameters from this file match the one from very 1st file
        oto_mat = OtoMatFile(f)
        if oto_mat != oto_mat1:
            print 'mismatch in OTO mat file params for %s' % f
            continue  # to next file since this one does not match

        # update fidx, which is our file index (time) tracker
        update_file_indexer_for_tags(c, f, taghours, fidx)

        # load data from file
        data = oto_mat.data

        # get desired xyz array from data
        a = data['grms'][0::2]  # stride 2 across rows because we redundantly saved in staircase fashion

        # compute RSS(x,y,z) to get 4th, overall RMS column (i.e. vecmag, v, as last column)
        xyzv = np.hstack((a, np.linalg.norm(a, axis=1).reshape((num_freqs, 1))))

        # insert OTO grms (xyzv) values at appropriate time index (c index) in TxFx4 big fat_array
        fat_array[:][:][c] = xyzv

    # for sleep_file in [files[i] for i in fidx['sleep']]:
    #     print sleep_file

    # idx_f = 12
    # for k, v in fidx.iteritems():
    #     print k
    #     tag_mins = np.nanmin(fat_array[np.array(v)], axis=0)
    #     tag_maxs = np.nanmax(fat_array[np.array(v)], axis=0)
    #     tag_means = np.nanmean(fat_array[np.array(v)], axis=0)
    #     print tag_means[idx_f, 3]
    #
    # # pluck vrms values for "all" hours for 12th freq band
    # fband = fat_array[:, idx_f, 3]
    # print np.percentile(fband, [25, 50, 75, 95], axis=0)

    # pickle save fat_array, fidx and files
    out_name = get_pickle_filename(start, stop, sensor, taghours)
    pickle_file = os.path.join(out_pth, out_name)

    my_dict = dict()
    my_dict['fat_array'] = fat_array
    my_dict['fidx'] = fidx
    my_dict['files'] = files
    my_dict['freqs'] = freqs
    my_dict['start'] = start
    my_dict['stop'] = stop
    my_dict['sensor'] = sensor
    my_dict['taghours'] = taghours

    with open(pickle_file, 'wb') as handle:
        pkl.dump(my_dict, handle, protocol=pkl.HIGHEST_PROTOCOL)

    print 'saved %s' % pickle_file


def plot_otohist(pickle_file):

    with open(pickle_file, 'rb') as handle:
        my_dict = pkl.load(handle)

    fidx = my_dict['fidx']
    fat_array = my_dict['fat_array']
    # files = my_dict['files']
    freqs = my_dict['freqs']
    start = my_dict['start']
    stop = my_dict['stop']
    sensor = my_dict['sensor']

    # iterate over tags (k becomes like 'sleep', 'wake', 'all' & v has index values for given tag)
    for k, v in fidx.iteritems():

        # create a figure instance
        fig = plt.figure(1, figsize=(10.0, 7.5))

        # create an axes instance
        ax = fig.add_subplot(111)

        # create the boxplot with fill color (via patch_artist); whisker caps at 1th & 99th percentiles
        bp = ax.boxplot(np.log10(fat_array[np.array(v)][:, :, 3]), whis=[1, 99], patch_artist=True)

        # change outline color, fill color and linewidth of the boxes
        for box in bp['boxes']:
            box.set(color='blue', linewidth=1)  # change outline color
            box.set(facecolor='white')  # change fill color

        # change color and linewidth of the whiskers
        for whisker in bp['whiskers']:
            whisker.set(color='gray', linewidth=1)

        # change color and linewidth of the caps
        for cap in bp['caps']:
            cap.set(color='lime', linewidth=1)

        # change color and linewidth of the medians
        for median in bp['medians']:
            median.set(color='red', linewidth=1)

        # change the style of fliers and their fill
        for flier in bp['fliers']:
            flier.set(marker='o', color='#e7298a', alpha=0.5, markersize=2)

        # custom x-tick labels
        locs, labels = plt.xticks()
        freq_ticks = [0.01, 0.1, 1, 10.0, 100.0]
        locs_new = np.interp(freq_ticks, np.concatenate(freqs).ravel(), locs)
        plt.xticks(locs_new, freq_ticks)

        # title
        title_str = '{0} through {1}, {2}, {3}'.format(
            start.strftime('%Y-%m-%d'), stop.strftime('%Y-%m-%d'),
            sensor, k)
        plt.title(title_str)

        # labels and grid
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Acceleration  $log_{10}(g_{rms})$')
        plt.grid(True)

        plt.tight_layout()

        # # save the figure
        # png_name = os.path.join(out_pth, get_out_png_file_name(start, stop, sensor, k))
        # pdf_name = png_name.replace('.png', '.pdf')
        # fig.savefig(pdf_name, bbox_inches='tight')
        # print 'saved %s' % pdf_name

        plt.show()
        # plt.close(fig)

# ---------------------------------------------------------------------------------------------


def get_log10_data_and_extrema(raw_data):
    """return log10(raw_data) and min & max"""
    data = np.log10(raw_data)
    return data, np.nanmin(data), np.nanmax(data)


def get_log10rms_bins():
    """return grms logarithmic bin width, edges, centers and count"""
    grms_min, grms_max = 1.0e-9, 1.0  # yes, hard coded
    data_min = np.log10(grms_min)
    data_max = np.log10(grms_max)
    bin_width = 0.001  # this is in log10 domain --> gives a bin count of 9000 bins
    bin_edges = np.arange(data_min, data_max + bin_width, bin_width)
    bin_centers = [i + bin_width / 2.0 for i in bin_edges[:-1]]
    num_bins = len(bin_edges)
    return bin_edges, bin_centers, bin_width, num_bins


def my_zeros(n):
    """return array of zeros with shape n (use either scalar or tuple for shape)"""
    return np.zeros(n, dtype='float64')  # int64 spoils downstream type somewhere


def OLDsum_otorunhist_pickle_files(pickle_files, tag, ax_cols=None):
    """Return summed otorunhist/tag data from pickle files generated by save_otorunhist_pickle_file routine.

     Good for grand boxplot (percentile) info on log10(grms) data.
     """

    # define our columns
    col_defs = {0: 'x', 1: 'y', 2: 'z', 3: 'v'}

    # handle columns (axes) we want to process
    # NOTE: 4th col for rss(x,y,z), use ax_cols = [3, ]; idx=3 is fourth (last) column
    if ax_cols is None:
        ax_cols = [0, 1, 2, 3]

    # get hard-coded RMS bin values
    log10rms_bin_edges, log10rms_bin_centers, log10rms_bin_width, num_log10rms_bins = get_log10rms_bins()

    # initialize running values for counting out-of-bound values & total count
    # NOTE: each of the following has a count for each ax_col
    count_out_bounds, total_count = my_zeros(len(ax_cols)), my_zeros(len(ax_cols))

    # initialize running values for histogram(s)
    hist_counts = my_zeros((num_log10rms_bins - 1, len(ax_cols)))

    # iterate over date-range, processed OTO count pickle files
    for pickle_file in pickle_files:

        with open(pickle_file, 'rb') as handle:
            my_dict = pkl.load(handle)

        fidx = my_dict['fidx']
        fat_array = my_dict['fat_array']
        # files = my_dict['files']
        # freqs = my_dict['freqs']
        # start = my_dict['start']
        # stop = my_dict['stop']
        # sensor = my_dict['sensor']

        if tag not in fidx.keys():
            print 'tag = %s not among keys in %s' % (tag, pickle_file)
            continue  # to next file since this one's missing tag

        v = fidx[tag]
        raw_data = fat_array[np.array(v)]  # shape: (num_times_this_tag, num_freqs, num_axes)

        # iterate over input for axes (columns), ax_cols to get counts
        for idx, c in enumerate(ax_cols):

            # let's get it so we are working with log10(raw_data) from this column, c
            data, data_min, data_max = get_log10_data_and_extrema(raw_data[:, :, c])  # this axis data shape: (num_times_this_tag, num_freqs)

            # update various counts (per-axis)
            non_nan_data = data[~np.isnan(data)]  # one way of suppressing annoying warnings
            count_out_bounds[idx] += np.sum((non_nan_data < log10rms_bin_edges[0]) | (non_nan_data >= log10rms_bin_edges[-1]))
            hist_counts[:, idx] += np.histogram(data, log10rms_bin_edges)[0]  # idx=0 bc no need for 2nd return value
            total_count[idx] += np.count_nonzero(~np.isnan(data))

            print "{:s}-axis (col={:d}) had {:,} good + {:,} outofbounds = {:,} total".format(col_defs[c], c,
                                                                                            sum(hist_counts[:, idx]),
                                                                                            count_out_bounds[idx],
                                                                                            total_count[idx])

    # now get highly-coveted cumulative sum percentage (for us to later pluck percentiles)
    csum_pct = 100.0 * np.cumsum(hist_counts, axis=0, dtype=float) / np.sum(hist_counts, axis=0)

    return hist_counts, total_count, count_out_bounds, csum_pct

    # # FIXME the next fixme and todo are hard-coded on 4th column (where idx = 3), so not generalized really
    #
    # # FIXME this is where we'd output spreadsheet like product for Gateway (percentile 5-number summary)
    # # # display just for ax_col = 3 (all)
    # # for k, left_edge in enumerate(log10rms_bin_edges[:-1]):
    # #     print hist_counts[k, 3], log10rms_bin_edges[k], log10rms_bin_edges[k + 1]
    #
    # # TODO this is where we use matplotlib's separate boxplot stats vs. plot parts to do plotting based on cumsum pctile
    #
    # csum_pct = 100.0 * np.cumsum(hist_counts[:, 3], dtype=float) / np.sum(hist_counts[:, 3])
    # print csum_pct
    #
    # return
    #
    # fig, ax = plt.subplots()
    #
    # # Plot the histogram heights against integers on the x axis
    # ax.bar(log10rms_bin_edges[:-1], hist_counts, width=1)
    # plt.xlim(min(log10rms_bin_edges), max(log10rms_bin_edges))
    #
    # # # Set the ticks to the center of the bins (bars)
    # # ax.set_xticks(log10rms_bin_edges)
    # #
    # # # Set the xticklabels to a string that tells us what the bin edges were
    # # ax.set_xticklabels(['{} - {}'.format(log10rms_bin_edges[i], log10rms_bin_edges[i + 1]) for i, j in enumerate(hist_counts)])
    #
    # # Set the ticks to the center of the bins (bars)
    # ax.set_xticks(log10rms_bin_centers)
    #
    # # Set the xticklabels to log10rms_bin_centers
    # ax.set_xticklabels(['{:0g}'.format(i) for i in log10rms_bin_centers])
    #
    # plt.show()


def sum_otorunhist_pickle_files(pickle_files, tag, axs='xyzv'):
    """Return summed otorunhist/tag data from pickle files generated by save_otorunhist_pickle_file routine.

     Good for grand boxplot (percentile) info on log10(grms) data.
     """

    # define our columns
    ax_cols = [AXMAP[i] for i in axs]

    # get hard-coded RMS bin values
    log10rms_bin_edges, log10rms_bin_centers, log10rms_bin_width, num_log10rms_bins = get_log10rms_bins()

    # FIXME find a better way to get num_freqs without having to peek (load) first pickle file
    with open(pickle_files[0], 'rb') as fh:
        tmp_dict = pkl.load(fh)
    num_freqs = len(tmp_dict['freqs'])

    # initialize running values for histogram(s)
    hist_counts = my_zeros((len(ax_cols), len(log10rms_bin_centers), num_freqs))
    csum_pct = my_zeros((len(ax_cols), len(log10rms_bin_centers), num_freqs))

    # iterate over date-range, processed OTO count pickle files
    for pickle_file in pickle_files:

        with open(pickle_file, 'rb') as handle:
            my_dict = pkl.load(handle)

        fat_array = my_dict['fat_array']  # ndarray   972x46x4: type `float64`, ~(1 Mb)
        fidx = my_dict['fidx']            # dict      n=3 << ex/ sleep, wake and all
        # taghours = my_dict['taghours']    # dict      n=3 << ex/ sleep, wake and all
        # files = my_dict['files']          # list      n=972
        # freqs = my_dict['freqs']          # ndarray   46x1: 46 elems, type `float64`
        # sensor = my_dict['sensor']        # str       ex/ 121f03
        # start = my_dict['start']          # date      ex/ 2016-01-01
        # stop = my_dict['stop']            # date      ex/ 2016-01-07

        if tag not in fidx.keys():
            print 'tag = %s not among keys in %s' % (tag, pickle_file)
            continue  # to next file since this one's missing tag

        # get v array of file (i.e. time) indexes
        v = fidx[tag]
        raw_data = fat_array[np.array(v)]  # shape: (num_times_this_tag, num_freqs, num_axes)

        print pickle_file

        # iterate over input for axes (columns), ax_cols to get counts
        for idx, c in enumerate(ax_cols):

            # let's get it so we are working with log10(raw_data) from this column, c
            data, data_min, data_max = get_log10_data_and_extrema(raw_data[:, :, c])  # this ax data shape is: (num_times_this_tag, num_freqs)

            # update counts (per-axis)
            hist_counts[idx] += np.apply_along_axis(lambda a: np.histogram(a, log10rms_bin_edges)[0], 0, data)

    # print np.max(sum(sum(hist_counts)))

    # now get cumulative sum percentage (to later pluck percentiles from)
    for idh, k in enumerate(ax_cols):
        top = np.cumsum(hist_counts, axis=1, dtype='float64')[idh]
        bot = np.sum(hist_counts, axis=1, dtype='float64')[idh]
        csum_pct[idh] = 100.0 * np.true_divide(top, bot, out=np.zeros_like(top, dtype='float64'), where=(bot != 0))

    return hist_counts, csum_pct


def get_percentile_index(csum_pct, pctile):
    """Return indices where cumulative sum percentage value >= input percentile value."""
    cma = np.ma.masked_where(csum_pct < pctile, csum_pct)
    yma = np.ma.masked_where(x < pctile, y)
    na, nb, nf = csum_pct.shape
    idxs = np.empty((na, 1, nf))
    idxs[:] = np.nan
    print csum_pct.shape
    print idxs.shape
    return np.argwhere(csum_pct >= pctile)


def get_percentile(log10rms_bin_centers, csum_pct, pctile, axs='xyzv'):
    """Return ugRMS @ percentile, actual percentile and index into csum_pct for actual percentile."""

    # get index values where csum_pct >= pctile
    idxs_ge_pctile = get_percentile_index(csum_pct, pctile)

    # now use index values to pluck milli-g rms values for percentile value of interest
    ugrms_pctile = [10.0 ** log10rms_bin_centers[idx_pctile] / 1.0e-6 for idx_pctile in idxs_pctile]

    # for completeness, get actual percentile value (close to, just above desired one)
    actual_pctile = list()
    for i, idx_pctile in enumerate(idxs_pctile):
        a = axs[i]
        ia = AXMAP[a]
        # print i, idx_pctile, a, ia
        actual_pctile.append(csum_pct[idx_pctile, i])

    return ugrms_pctile, actual_pctile, idxs_pctile


def create_ptile_boxplot_for_ax(out_file, a, arf_pctiles_for_ax, sensor, start, stop, tag, freq_bin_ctrs, nice_freqs=True):
    """create percentile boxplot for given axis"""

    m = np.array([
        [0.0088, 0.0098, 0.0110, 1.8000e-006],
        [0.0110, 0.0124, 0.0139, 1.8000e-006],
        [0.0139, 0.0156, 0.0175, 1.8000e-006],
        [0.0175, 0.0197, 0.0221, 1.8000e-006],
        [0.0221, 0.0248, 0.0278, 1.8000e-006],
        [0.0278, 0.0313, 0.0351, 1.8000e-006],
        [0.0351, 0.0394, 0.0442, 1.8000e-006],
        [0.0442, 0.0496, 0.0557, 1.8000e-006],
        [0.0557, 0.0625, 0.0702, 1.8000e-006],
        [0.0702, 0.0787, 0.0891, 1.8000e-006],
        [0.0891, 0.1000, 0.1122, 1.8000e-006],
        [0.1122, 0.1250, 0.1413, 2.2500e-006],
        [0.1413, 0.1600, 0.1778, 2.8800e-006],
        [0.1778, 0.2000, 0.2239, 3.6000e-006],
        [0.2239, 0.2500, 0.2818, 4.5000e-006],
        [0.2818, 0.3150, 0.3548, 5.6700e-006],
        [0.3548, 0.4000, 0.4467, 7.2000e-006],
        [0.4467, 0.5000, 0.5623, 9.0000e-006],
        [0.5623, 0.6300, 0.7079, 1.1340e-005],
        [0.7079, 0.8000, 0.8913, 1.4400e-005],
        [0.8913, 1.0000, 1.1220, 1.8000e-005],
        [1.1220, 1.2500, 1.4130, 2.2500e-005],
        [1.4130, 1.6000, 1.7780, 2.8800e-005],
        [1.7780, 2.0000, 2.2390, 3.6000e-005],
        [2.2390, 2.5000, 2.8180, 4.5000e-005],
        [2.8180, 3.1500, 3.5480, 5.6700e-005],
        [3.5480, 4.0000, 4.4670, 7.2000e-005],
        [4.4670, 5.0000, 5.6230, 9.0000e-005],
        [5.6230, 6.3000, 7.0790, 1.1340e-004],
        [7.0790, 8.0000, 8.9130, 1.4400e-004],
        [8.9130, 10.0000, 11.2200, 1.8000e-004],
        [11.2200, 12.5000, 14.1300, 2.2500e-004],
        [14.1300, 16.0000, 17.7800, 2.8800e-004],
        [17.7800, 20.0000, 22.3900, 3.6000e-004],
        [22.3900, 25.0000, 28.1800, 4.5000e-004],
        [28.1800, 31.5000, 35.4800, 5.6700e-004],
        [35.4800, 40.0000, 44.6700, 7.2000e-004],
        [44.6700, 50.0000, 56.2300, 9.0000e-004],
        [56.2300, 64.0000, 71.8380, 1.1520e-003],
        [71.8380, 80.6350, 90.5100, 1.4514e-003],
        [90.5100, 101.5900, 114.0400, 1.8000e-003],
        [114.0400, 128.0000, 143.6800, 1.8000e-003],
        [143.6800, 161.2700, 181.0200, 1.8000e-003],
        [181.0200, 203.1900, 228.0700, 1.8000e-003],
        [228.0700, 256.0000, 287.3500, 1.8000e-003],
        [287.3500, 322.5400, 362.0400, 1.8000e-003]])

    fig, ax = plt.subplots(figsize=(10, 7.5))

    # draw steps for ISS requirement in light, transparent blue
    plt.step(m[:, 0], m[:, 3], where='post', label='post', alpha=0.3, color='blue')

    p = np.power(10, np.float64(arf_pctiles_for_ax))

    # draw horizontal lines at median value of grms in red
    plt.hlines(y=[p[2, :]], xmin=m[:, 0], xmax=m[:, 2], linewidth=1.5, alpha=0.85, color='red')

    # draw lower, vertical (whisker) lines from 1st to 25th percentiles in black
    plt.vlines(x=m[:, 1], ymin=p[0, :], ymax=p[1, :], linewidth=1.5, alpha=0.75, color='black')

    # draw upper, vertical (whisker) lines from 75th to 99th percentiles in black
    plt.vlines(x=m[:, 1], ymin=p[3, :], ymax=p[4, :], linewidth=1.5, alpha=0.75, color='black')

    plt.xscale('log')
    plt.yscale('log')

    # title
    if a == 'v':
        ax_str = 'RSS(X,Y,Z)'
    else:
        ax_str = '%s-Axis' % a.upper()
    title_str = 'ISS RMS Acceleration vs. One-Third Octave Band\n'
    title_str += 'GMT {0} through {1}, Condition:{2}\nSAMS Sensor:{3}, {4}'.\
        format(start.strftime('%Y-%m-%d'), stop.strftime('%Y-%m-%d'), tag.upper(), sensor.upper(), ax_str)
    plt.title(title_str)

    # labels and grid
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Acceleration  $(g_{rms})$')
    plt.grid(True)

    plt.ylim([1e-8, 1e-2])

    # annotate ISS requirements curve
    plt.text(0.75*m[0, 1], 1.25*m[0, -1], 'ISS Microgravity\nControl Plan', alpha=0.65, color='blue', fontsize=9)

    ################################################################
    # this is an inset axes over the main axes to use as a legend
    ax_leg = plt.axes([0.16, 0.64, 0.2, 0.2], facecolor='ivory')
    plt.plot([], [])
    # plt.title('Legend')

    plt.vlines(x=[10.0], ymin=[75.0], ymax=[99.0], linewidth=1.5, alpha=0.75, color='black')
    plt.hlines(y=[50.0], xmin=[5.0], xmax=[15.0], linewidth=2.5, alpha=0.85, color='red')
    plt.vlines(x=[10.0], ymin=[1.0], ymax=[25.0], linewidth=1.5, alpha=0.75, color='black')

    plt.hlines(y=[1, 25, 50, 75, 99], xmin=[10, 10, 16, 10, 10], xmax=[30, 30, 30, 30, 30], linewidth=1, color='gray',
               linestyle=':')

    plt.text(31, 99, '99th percentile', verticalalignment='center')
    plt.text(31, 75, '75th percentile', verticalalignment='center')
    plt.text(31, 50, 'median', verticalalignment='center')
    plt.text(31, 25, '25th percentile', verticalalignment='center')
    plt.text(31, 1, '1st percentile', verticalalignment='center')

    plt.xlim(-10, 110)
    plt.ylim(-10, 110)

    plt.xticks([])
    plt.yticks([])

    # plt.show()

    fig.savefig(out_file, pad_inches=(1.0, 1.0))  # 1-inch pad since figsize was chopped 1-inch all-around

    print 'saved %s' % out_file


def create_ptile_spreadsheet_for_ax(out_file, a, arf_pctiles_for_ax, sensor, start, stop, tag, freq_bin_ctrs):

    print a, tag

    num_freqs = len(freq_bin_ctrs)

    moto = get_oto_iss_req_steps()

    # get percentiles [1, 25, 50, 75, 99] at each OTO freq. band
    for n in range(len(freq_bin_ctrs)):
        p = np.power(10, np.float64(arf_pctiles_for_ax[:, n])) / 1e-6
        if all(np.isnan(p)):
            pass
        else:
            print 'cf = {:8.4f}, P01 = {:9.4f}, P25 = {:9.4f}, P50 = {:9.4f}, P75 = {:9.4f}, P99 = {:9.4f} ugrms'.\
                format(freq_bin_ctrs[n][0], *p)


def OLDdo_manual_boxplot(bin_centers):

    num_freqs = len(bin_centers)

    # fake data to get stats as placeholder
    np.random.seed(19841211)
    data = np.random.lognormal(size=(4, num_freqs), mean=123, sigma=4.56)
    labels = 'A' * num_freqs

    # compute the boxplot stats
    stats = cbook.boxplot_stats(data, labels=labels)

    # After we've computed the stats, we can go through and change anything. Just to prove it, I'll
    # set the median of each set to the median of all the data, and double the means

    for n in range(len(stats)):
        stats[n]['whishi'] = np.float64(5)
        stats[n]['q3'] = np.float64(4)
        stats[n]['med'] = np.float64(3)
        stats[n]['q1'] = np.float64(2)
        stats[n]['whislo'] = np.float64(1)
        # -----------------------------------
        stats[n]['label'] = 'A'
        stats[n]['mean'] = np.nan
        stats[n]['cilo'] = -np.inf
        stats[n]['cihi'] = np.inf
        stats[n]['fliers'] = np.array([np.nan, ])
        stats[n]['iqr'] = np.nan

    # print list(stats[0])  # ['label', 'mean', 'iqr', 'cilo', 'cihi', 'whishi', 'whislo', 'fliers', 'q1', 'med', 'q3']

    font_size = 10  # fontsize

    fig, ax = plt.subplots(figsize=(10, 7.5))

    ax.bxp(stats, showfliers=False)

    ax.set_title('Manual Boxplots', fontsize=font_size)

    # Set the ticks to the center of the bins (bars)
    ax.set_xticks(range(1, num_freqs + 1))

    # Set the xticklabels to bin_centers
    ax.set_xticklabels(['{:0g}'.format(i) for i in bin_centers])

    # # custom x-tick labels
    # locs, labels = plt.xticks()
    # freq_ticks = [0.01, 0.1, 1, 10.0, 100.0]
    # locs_new = np.interp(freq_ticks, np.concatenate(freqs).ravel(), locs)
    # plt.xticks(locs_new, freq_ticks)

    plt.show()

# ---------------------------------------------------------------------------------------------


def demo_pluck_show_percentiles(pickle_files):

    log10rms_bin_edges, log10rms_bin_centers, log10rms_bin_width, log10rms_num_bins = get_log10rms_bins()

    arf = get_grand_percentiles_from_pickle_files(pickle_files, log10rms_bin_centers)


    axs = 'xyzv'
    # ax_cols = [AXMAP[i] for i in axs]

    # sum over otorunhist pickle files
    hist_counts, csum_pct = sum_otorunhist_pickle_files(pickle_files, 'sleep', axs=axs)

    print csum_pct.shape

    percentiles = [1.0, 25.0, 50.0, 75.0, 99.0]

    for pctile in pctiles:

        # pluck ugRMS @ percentile value and actual percentile and index into csum_pct for actual percentile
        ugrms_pctile, actual_pctile, idxs_pctile = get_percentile(log10rms_bin_centers, csum_pct, pctile, axs=axs)

        for ia, a in enumerate(axs):
            print '{:s}-axis'.format(axs[ia]),
            print '({:6.3f}%, {:8.2f} ugrms)'.format(actual_pctile[ia], ugrms_pctile[ia]),
            print 'at csum_pct index = {:d}'.format(idxs_pctile[ia])


def my_manual_boxplotter(pickle_files):

    sensor = '121f0x'
    start = datetime.datetime(1988, 1, 2)
    stop = datetime.datetime(1988, 1, 15)
    tag = 'sleep'

    axs = 'v'
    ax_cols = [AXMAP[i] for i in axs]

    with open(pickle_files[0], 'rb') as handle:
        my_dict = pkl.load(handle)

    freq_bin_centers = my_dict['freqs']  # np.arange(0.01, 0.46 + 0.01, 0.01)

    # sum over otorunhist pickle files
    hist_counts, total_count, count_out_bounds, csum_pct = sum_otorunhist_pickle_files(pickle_files, 'sleep', ax_cols=ax_cols)

    # stats = compute_otorunhist_percentiles(hist_counts, total_count, count_out_bounds)
    create_ptile_boxplot_for_ax(sensor, start, stop, tag, freq_bin_centers, hist_counts, total_count, count_out_bounds, nice_freqs=True)


def get_log10rms_values_at_pctile(csum_pct, log10rms_bin_centers, pctile):
    """Return log10(rms) values at the given percentile value."""

    # use shape to tile rms bin center values for plucking via mask
    num_f, num_r, num_a = csum_pct.shape  # LHS is num of freqs, rms and axes, respectively
    rms_tiles = np.tile(np.array(log10rms_bin_centers).reshape(-1, 1), (num_f, 1, num_a))

    # mask off/out RMS values where cumsum percentage is strictly less than percentile value
    log10rms_values = np.ma.masked_where(csum_pct < pctile, rms_tiles)  # ... so keep at/above pctile

    # create outer list, one outer list element for each axis
    log10rms_values_at_pctile = list()
    for ax in log10rms_values:
        # inner list for this axis holds 1st RMS value where percentile meets/beats pctile (or None if all masked out)
        values_for_this_ax = list()
        for fr in ax.T:
            rms_list = list(fr.compressed())
            values_for_this_ax.append(next(iter(rms_list), None))
        log10rms_values_at_pctile.append(values_for_this_ax)

    return log10rms_values_at_pctile


def get_grand_percentiles_from_pickle_files(pickle_files, log10rms_bin_centers, tag, axs):
    """Return AxRxF array """

    # sum over otorunhist pickle files
    hist_counts, csum_pct = sum_otorunhist_pickle_files(pickle_files, tag, axs=axs)

    # build list for percentiles' RMS values
    percentile_stats = list()
    percentiles = [1.0, 25.0, 50.0, 75.0, 99.0]
    for pctile in percentiles:
        log10rms_vals_for_pctile = get_log10rms_values_at_pctile(csum_pct, log10rms_bin_centers, pctile)
        percentile_stats.append(log10rms_vals_for_pctile)

    # since we reversed 1st two dimensions above, let's get back to AxRxF ordering here
    raf = np.array(percentile_stats)    # RxAxF is RMSxAXISxFREQ
    arf = np.transpose(raf, (1, 0, 2))  # AxRxF is AXISxRMSxFREQ

    return arf


def get_oto_iss_req_steps():

    moto = np.array([
        [0.0088, 0.0098, 0.0110, 1.8000e-006],
        [0.0110, 0.0124, 0.0139, 1.8000e-006],
        [0.0139, 0.0156, 0.0175, 1.8000e-006],
        [0.0175, 0.0197, 0.0221, 1.8000e-006],
        [0.0221, 0.0248, 0.0278, 1.8000e-006],
        [0.0278, 0.0313, 0.0351, 1.8000e-006],
        [0.0351, 0.0394, 0.0442, 1.8000e-006],
        [0.0442, 0.0496, 0.0557, 1.8000e-006],
        [0.0557, 0.0625, 0.0702, 1.8000e-006],
        [0.0702, 0.0787, 0.0891, 1.8000e-006],
        [0.0891, 0.1000, 0.1122, 1.8000e-006],
        [0.1122, 0.1250, 0.1413, 2.2500e-006],
        [0.1413, 0.1600, 0.1778, 2.8800e-006],
        [0.1778, 0.2000, 0.2239, 3.6000e-006],
        [0.2239, 0.2500, 0.2818, 4.5000e-006],
        [0.2818, 0.3150, 0.3548, 5.6700e-006],
        [0.3548, 0.4000, 0.4467, 7.2000e-006],
        [0.4467, 0.5000, 0.5623, 9.0000e-006],
        [0.5623, 0.6300, 0.7079, 1.1340e-005],
        [0.7079, 0.8000, 0.8913, 1.4400e-005],
        [0.8913, 1.0000, 1.1220, 1.8000e-005],
        [1.1220, 1.2500, 1.4130, 2.2500e-005],
        [1.4130, 1.6000, 1.7780, 2.8800e-005],
        [1.7780, 2.0000, 2.2390, 3.6000e-005],
        [2.2390, 2.5000, 2.8180, 4.5000e-005],
        [2.8180, 3.1500, 3.5480, 5.6700e-005],
        [3.5480, 4.0000, 4.4670, 7.2000e-005],
        [4.4670, 5.0000, 5.6230, 9.0000e-005],
        [5.6230, 6.3000, 7.0790, 1.1340e-004],
        [7.0790, 8.0000, 8.9130, 1.4400e-004],
        [8.9130, 10.0000, 11.2200, 1.8000e-004],
        [11.2200, 12.5000, 14.1300, 2.2500e-004],
        [14.1300, 16.0000, 17.7800, 2.8800e-004],
        [17.7800, 20.0000, 22.3900, 3.6000e-004],
        [22.3900, 25.0000, 28.1800, 4.5000e-004],
        [28.1800, 31.5000, 35.4800, 5.6700e-004],
        [35.4800, 40.0000, 44.6700, 7.2000e-004],
        [44.6700, 50.0000, 56.2300, 9.0000e-004],
        [56.2300, 64.0000, 71.8380, 1.1520e-003],
        [71.8380, 80.6350, 90.5100, 1.4514e-003],
        [90.5100, 101.5900, 114.0400, 1.8000e-003],
        [114.0400, 128.0000, 143.6800, 1.8000e-003],
        [143.6800, 161.2700, 181.0200, 1.8000e-003],
        [181.0200, 203.1900, 228.0700, 1.8000e-003],
        [228.0700, 256.0000, 287.3500, 1.8000e-003],
        [287.3500, 322.5400, 362.0400, 1.8000e-003]])

    return moto


def generate_perctile_boxplots(pickle_files, tags, axs):
    """produce tufte boxplot(s) one for each tag/axs combo"""

    # use first pickle file to gather needed info
    with open(pickle_files[0], 'rb') as handle:
        my_dict = pkl.load(handle)

    freq_bin_ctrs = my_dict['freqs']
    taghours = my_dict['taghours']  # dict  n=3 << ex/ sleep, wake and all
    sensor = my_dict['sensor']  # ....str   ex/ 121f03
    start = my_dict['start']  # ......date  ex/ datetime 2016-01-01
    stop = my_dict['stop']  # ........date  ex/ datetime 2016-01-07

    # be sure tags exist among keys in our first pickle file
    if not all([t in taghours.keys() for t in tags]):
        raise Exception('could not find all tags among taghours keys')

    # TODO verify the rest of pickle files match: freqs, taghours and sensor

    # TODO accounting of time (steps, temporal resolution refactoring???)

    # FIXME kludge just use stop from last pickle file for now
    # use first pickle file to gather needed info
    with open(pickle_files[-1], 'rb') as handle:
        my_dict2 = pkl.load(handle)
    final_stop = my_dict2['stop']  # ........date  ex/ datetime 2016-03-31

    # get log10(rms) bin centers
    log10rms_bin_edges, log10rms_bin_centers, log10rms_bin_width, num_log10rms_bins = get_log10rms_bins()

    for tag in tags:
        # Get array of percentile results for just this tag
        # A x R x F
        # |   |   |
        # |   |   \-- number of Frequency bands, OTO bands = 46
        # |   \-------- number of RMS percentile values    =  5  [1, 25, 50, 75, 99]
        # \-------------- number of Axes                   =  4  'xyzv'
        arf_pctiles = get_grand_percentiles_from_pickle_files(pickle_files, log10rms_bin_centers, tag, axs)

        for a in axs:
            ax = AXMAP[a]
            arf_pctiles_for_ax = arf_pctiles[ax]

            # Do manual boxplot with percentile results array
            out_base = '%s-%s_%s_%saxis_%s.pdf' %(start.strftime('%Y-%m-%d'),
                                                  final_stop.strftime('%Y-%m-%d'), sensor, a, tag)
            out_file = os.path.join(os.path.dirname(pickle_files[0]), out_base)

            create_ptile_boxplot_for_ax(out_file, a, arf_pctiles_for_ax, sensor, start, final_stop, tag,
                                        freq_bin_ctrs, nice_freqs=True)

            # create_ptile_spreadsheet_for_ax(out_file.replace('.pdf', '.csv'), a, arf_pctiles_for_ax, sensor, start,
            #                                 final_stop, tag, freq_bin_ctrs)


if __name__ == '__main__':

    # TODO make it so that python can do the first step too
    # 1. Run MATLAB code on mr-hankey to generate batch/results/onethird/YMD/sensor/*.mat [OTO RMS] data
    # 2. Produce otorunhist pickle files that have fat_array segregated by taghours for a date range [maybe a month].
    # 3. Produce RMS vs. OTO band frequency percentile plots for a given tag and axis (xyzv).
    # SEE EX#2 & EX#3 BELOW FOR STEPS #2 AND #3 ABOVE.

    #####################################################
    # EX#2 Produce sleep/wake/all otorunhist pickle files << fat_array, fidx, freqs, taghours, files, sensor, start, stop
    #                                                    hour-range   hour-range
    #                                                         vv vv        vv vv
    # ./main.py -s SENSOR -d STARTDATE  -e STOPDATE   -t TAG1,h1,h2   TAG2,h3,h4
    # ./main.py -s 121f03 -d 2016-01-01 -e 2016-01-31 -t sleep,0,4    wake,8,16 -vv
    # OR
    #      an example of non-contiguous set of hour ranges     v v                  vv vv
    # ./main.py -s 121f03 -d 2016-01-01 -e 2016-03-31 -t sleep,0,4  wake,8,16 sleep,23,24 -vv

    ################################################################
    # EX#3 Sum/combine otorunhist pickle files to produce boxplot(s)
    # ./main.py -s SENSOR -d STARTDATE  -e STOPDATE -t sleep --plot
    # ./main.py -s 121f03 -d 2017-01-01 -e 2017-03-30 -t sleep --plot

    args = argparser.parse_inputs()

    if args.verbosity > 2:
        print "args", args

    # handle the case when we get random dates from file (not a typical date range)
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

            # TODO make this a smart search for files instead of manually-created list  [re-purpose input args?]

            pickle_files = [
                '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-01_2016-01-07_121f03_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-08_2016-01-14_121f03_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-01_2016-01-31_121f03_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2016/month02/2016-02-01_2016-02-29_121f03_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2016/month03/2016-03-01_2016-03-31_121f03_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2018/month01/2018-01-18_2018-01-31_121f03_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2018/month02/2018-02-01_2018-02-28_121f03_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2018/month03/2018-03-01_2018-03-31_121f03_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2018/month04/2018-04-01_2018-04-17_121f03_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2018/month01/2018-01-18_2018-01-31_121f05_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2018/month02/2018-02-01_2018-02-28_121f05_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2018/month03/2018-03-01_2018-03-31_121f05_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2018/month04/2018-04-01_2018-04-17_121f05_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2018/month01/2018-01-18_2018-01-31_121f08_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2018/month02/2018-02-01_2018-02-28_121f08_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2018/month03/2018-03-01_2018-03-31_121f08_sleep_all_wake_otorunhist.pkl',
                '/misc/yoda/www/plots/batch/results/onethird/year2018/month04/2018-04-01_2018-04-17_121f08_sleep_all_wake_otorunhist.pkl',
            ]

            tags = ['sleep', 'wake', 'all']
            axs = 'xyzv'
            generate_perctile_boxplots(pickle_files[2:5], tags, axs)
            generate_perctile_boxplots(pickle_files[5:9], tags, axs)
            generate_perctile_boxplots(pickle_files[9:13], tags, axs)
            generate_perctile_boxplots(pickle_files[13:], tags, axs)

        else:
            # iterate over each day, then iterate over day's files & finally by taghours to build/sum results
            save_otorunhist_pickle_file(args.start, args.stop, sensor=args.sensor, taghours=args.taghours, verbosity=args.verbosity)
