#!/usr/bin/env python

"""Running histogram(s) of acceleration vector magnitude.

This module provides classes for computing/plotting running histograms of SAMS (PAD file) data.

"""

import os
import sys
import glob
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
import scipy.io as sio
from pathlib import Path
from dateutil import parser
from matplotlib import rc, pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.font_manager import FontProperties

import argparser
from plumb_line import plumblines
from pims.mathbase.basics import round_up
from pims.utils.pimsdateutil import datetime_to_ymd_path, datetime_to_dailyhist_path, year_month_to_dtm_start_stop, ymd_pathstr_to_date
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop
from pims.files.filter_pipeline import FileFilterPipeline, BigFile
from histpad.pad_filter_pipeline import PadDataDaySensorWhere, sensor2subdir, PadDataDaySensorWhereMinDur
from histpad.file_disposal import DailyHistFileDisposal, DailyMinMaxFileDisposal
from ugaudio.explore import padread, pad_file_percentiles


DEFAULT_PADDIR = argparser.DEFAULT_PADDIR
DEFAULT_HISTDIR = argparser.DEFAULT_HISTDIR


def list_mat_files(glob_pat):
    """print length of filenames list that matches input glob pattern"""
    fnames = glob.glob(glob_pat)
    #print len(fnames)
    return fnames

#list_mat_files('/misc/yoda/www/plots/batch/results/dailyhistpad/year2017/month*/day*/*_accel_121f03/dailyhistpad.mat')
#files = list_mat_files('/misc/yoda/pub/pad/year2017/month*/day*/*_accel_es05006/*es05006')
#for f in files:
#    print f
#raise SystemExit


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


def get_where_clause(sensor):
    if sensor.endswith('006'):
        dwhere = {'CutoffFreq': 6.0}
    elif sensor.endswith('020'):
        dwhere = {'CutoffFreq': 20.0}        
    elif sensor.startswith('es0'):
        dwhere = {'CutoffFreq': 204.2}
    else:
        dwhere = {'CutoffFreq': 200}
    return dwhere


def get_pad_day_sensor_files_minbytes(files, day, sensor, min_bytes=2*1024*1024):

    # initialize callable classes that act as filters for our pipeline
    dwhere = get_where_clause(sensor)
    file_filter1 = PadDataDaySensorWhere(day, sensor, where=dwhere)  # fc = 200 Hz (or 204.2 Hz)
    file_filter2 = BigFile(min_bytes=min_bytes)                      # at least 2 MB
    
    # initialize processing pipeline with callable classes, but not using file list as input yet
    ffp = FileFilterPipeline(file_filter1, file_filter2)
    #print ffp

    # now apply processing pipeline to file list; at this point, ffp is callable
    return list( ffp(files) )


def get_pad_day_sensor_rate_mindur_files(files, day, sensor, fs, mindur=5):

    # FIXME rate implied at 500.0 (needs attention in PadDataDaySensorWhereMinDur)

    # initialize callable classes that act as filters for our pipeline
    file_filter1 = PadDataDaySensorWhereMinDur(day, sensor, where={'SampleRate': fs}, mindur=mindur)

    # initialize processing pipeline with callable classes, but not using file list as input yet
    ffp = FileFilterPipeline(file_filter1)

    # now apply processing pipeline to file list; at this point, ffp is callable
    return list( ffp(files) )


def demo_pad_pct99(sensor, y, m, d, min_bytes=2*1024*1024):
    from ugaudio.load import padread
    ymd_dir = datetime_to_ymd_path(datetime.date(y, m, d))
    glob_pat = '%s/*_accel_%s/*%s' % (ymd_dir, sensor, sensor)
    fnames = glob.glob(glob_pat)
    fnames_filt = get_pad_day_sensor_files_minbytes(fnames, '%4d-%02d-%02d' % (y, m, d), sensor, min_bytes=min_bytes)
    arr = np.empty((0, 4))
    for fname in fnames_filt:
        # read data from file (not using double type here like MATLAB would, so we get courser demeaning)
        b = padread(fname)
        a = b - b.mean(axis=0)       # demean each column
        #a = np.delete(a, 0, 1)       # delete first (time) column
        a[:,0] = np.sqrt(a[:,1]**2 + a[:,2]**2 + a[:,3]**2)  # replace 1st column with vecmag
        p = np.percentile(np.abs(a), 99, axis=0)
        #print '{:e}  {:e}  {:e}  {:e}'.format(*p)
        arr = np.append(arr, [p], axis=0)

    return arr


def demo_99pct_vecmag_array(min_bytes):
    #drange = pd.date_range('2017-09-01', '2017-12-01')
    #drange = pd.date_range('2017-09-01', '2017-09-02')
    #sensor = '121f03006'
    drange = pd.date_range('2017-01-01', '2018-01-01')
    sensor = 'es05020'
    print sensor
    print '{:>9}  {:4}  {:2}  {:2}'.format('# Files', 'Year', 'Mo', 'Da')
    def do_plot():
        pcts = np.empty((0, 4), np.float)
        for d in drange:
            pct = demo_pad_pct99(sensor, d.year, d.month, d.day, min_bytes=min_bytes)
            pcts = np.append(pcts, pct, axis=0)
            print '{:9}  {:4}  {:02}  {:02}'.format(pcts.shape[0], d.year, d.month, d.day)
        plt.plot(pcts[:,0] * 1e3)
        plt.ylabel('99th Pctile of Accel. Mag. (mg)')
        plt.title(sensor)
        plt.show()
    do_plot()


########min_bytes = 2*1024*1024
########demo_99pct_vecmag_array(min_bytes) # shows ~2.2mg for 99th pctile es05020
########raise SystemExit


def save_dailyhistpad(start, stop, sensor='121f03', where={'CutoffFreq': 200}, bins=np.arange(-0.2, 0.2, 5e-5), vecmag_bins=np.arange(0, 0.5, 5e-5), min_bytes=2*1024*1024, indir=DEFAULT_PADDIR, outdir=DEFAULT_HISTDIR):

    dr = get_date_range([start, stop])
    for d in dr:
    
        day = d.strftime('%Y-%m-%d')

        # get list of PAD data files for particular day and sensor
        pth = os.path.join( datetime_to_ymd_path(d), sensor2subdir(sensor) )
        print pth
        if os.path.exists(pth):
            tmp = os.listdir(pth)
            files = [ os.path.join(pth, f) for f in tmp ]

            # now filter files
            my_files = get_pad_day_sensor_files_minbytes(files, day, sensor, min_bytes=min_bytes)            
            print '%s gives %d files' % (day, len(my_files))
            
            len_files = len(my_files)
            if len_files > 0:
                my_files.sort(key=os.path.basename)
                outfile = os.path.join( pth.replace(indir, outdir), 'dailyhistpad.mat')
                if os.path.exists(outfile):
                    raise Exception('OUTPUT FILE %s ALREADY EXISTS' % outfile)
                else:
                    directory = os.path.dirname(outfile)
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                dh = DailyHistFileDisposal(my_files[0], bins, vecmag_bins)
                Nx, Ny, Nz, Nv = dh.run()
                print '>> completed %s' % my_files[0]
                for f in my_files[1:]:
                    dh = DailyHistFileDisposal(f, bins, vecmag_bins)
                    nx, ny, nz, nv = dh.run()
                    Nx += nx
                    Ny += ny
                    Nz += nz
                    Nv += nv
                    print '>> completed %s' % f
                sio.savemat(outfile, {'Nx': Nx, 'Ny': Ny, 'Nz': Nz, 'Nv': Nv})
                print
        else:
            print '%s gives NO FILES' % day


def Jan_thru_Sep_2017():
    start = datetime.date(2017,  1, 1)
    stop  = datetime.date(2017, 10, 1) - datetime.timedelta(days=1)
    save_dailyhistpad(start, stop, sensor='121f03', where={'CutoffFreq': 200}, min_bytes=2*1024*1024)


def save_monthlyhistpad(year, month, sensor='121f03', fc=200):

    # load bins and vecmag_bins
    name_bins_mat = 'dailyhistpad_bins_%d.mat' % fc
    # a = sio.loadmat(os.path.join(DEFAULT_OUTDIR, 'dailyhistpad_bins.mat'))  # DELETEME
    a = sio.loadmat(os.path.join(DEFAULT_HISTDIR, name_bins_mat))
    vecmag_bins = a['vecmag_bins'][0]
    bins = a['bins'][0]

    # initialize start/stop for month of interest
    start, stop = year_month_to_dtm_start_stop(year, month)

    hv = np.zeros_like(vecmag_bins)
    hx = np.zeros_like(bins)
    hy = np.zeros_like(bins)
    hz = np.zeros_like(bins)
    
    files = []
    for d in pd.date_range(start, stop):
        f = os.path.join(datetime_to_dailyhist_path(d), 'dailyhistpad.mat')
        if os.path.exists(f):
            files.append(f)
            data = sio.loadmat(f)
            hv += data['Nv'][0]
            hx += data['Nx'][0]
            hy += data['Ny'][0]
            hz += data['Nz'][0]
            print '%d' % np.sum(hv)
    print ''
    
    # output filename relative to common path
    outdir = DEFAULT_HISTDIR
    tmpdir = datetime_to_dailyhist_path(datetime.datetime(year, month, 1))
    outdir = str(Path(tmpdir).parents[1])  # this moves 2 levels up
    outfile = os.path.join(outdir, 'month%02dhistpad_%s.mat' % (month, sensor))
    
    # save to output file
    sio.savemat(outfile, {'vecmag_bins': vecmag_bins, 'bins': bins, 'hx': hx, 'hy': hy, 'hz': hz, 'hv': hv, 'files': files})
    print outfile


def get_axis_settings(xvals):
    xvals_max = max(xvals)
    mult = 5  
    xMajorLoc = MultipleLocator(1)
    xMinorLoc = MultipleLocator(0.5)
    print 'xvals_max', xvals_max
    if xvals_max > 40:
        #mult = 220
        #xMajorLoc = MultipleLocator(20)
        #xMinorLoc = MultipleLocator(10)
        mult = 120
        xMajorLoc = MultipleLocator(20)
        xMinorLoc = MultipleLocator(10)        
    elif xvals_max > 30:
        mult = 60
        xMajorLoc = MultipleLocator(5)
        xMinorLoc = MultipleLocator(1)
    elif xvals_max > 12:
        mult = 24
        xMajorLoc = MultipleLocator(2)
        xMinorLoc = MultipleLocator(1)
    #xmax = round_up(max(xvals), mult)
    xmax = round_up(xvals_max, mult)
    axlims = [-1, xmax, -5, 105]
    yticks = np.arange(0, 104, 5)
    xticks = np.arange(xmax)
    return xMajorLoc, xMinorLoc, axlims, yticks, xticks


def get_axis_settings_xyz(x, y, z, axlims):
    if axlims[1] > 30:
        xMajorLoc = MultipleLocator(10)
        xMinorLoc = MultipleLocator(5)
        axlims = [-60, 60, -0.01, 0.51]
        yticks = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
        xticks = np.arange(-60, 60, 10)
    else:
        xMajorLoc = MultipleLocator(1)
        xMinorLoc = MultipleLocator(0.5)
        axlims = [-5, 5, -0.1, 5.1]
        yticks = np.arange(0, 6)
        xticks = np.arange(-5, 5, 1)
    return xMajorLoc, xMinorLoc, axlims, yticks, xticks


def OBSOLETE_plotnsave_daterange_histpad(start, stop, sensor='121f03', fc=200):

    # load bins and vecmag_bins
    name_bins_mat = 'dailyhistpad_bins_%d.mat' % fc
    # a = sio.loadmat(os.path.join(DEFAULT_OUTDIR, 'dailyhistpad_bins.mat'))  # DELETEME
    a = sio.loadmat(os.path.join(DEFAULT_HISTDIR, name_bins_mat))
    vecmag_bins = a['vecmag_bins'][0]
    bins = a['bins'][0]

    hv = np.zeros_like(vecmag_bins)
    hx = np.zeros_like(bins)
    hy = np.zeros_like(bins)
    hz = np.zeros_like(bins)
    
    files = []
    for d in pd.date_range(start, stop):
        f = os.path.join(datetime_to_dailyhist_path(d, sensor_subdir=sensor2subdir(sensor)), 'dailyhistpad.mat')
        if os.path.exists(f):
            files.append(f)
            data = sio.loadmat(f)
            hv += data['Nv'][0]
            hx += data['Nx'][0]
            hy += data['Ny'][0]
            hz += data['Nz'][0]
            num_pts = np.sum(hv)
            #print '%s %d %s' % (d.date(), np.sum(hv), f)
            print "{} {:20,.0f} {}".format(str(d.date()), num_pts, f)
    print ''
    
    # output filename relative to common path
    outdir = os.path.join(DEFAULT_HISTDIR, 'plots')
    outname = '%s_to_%s_%s' % (start, stop, sensor)
    outstub = os.path.join(outdir, outname)
    
    # save to output mat file
    outmat = outstub + '.mat'
    sio.savemat(outstub + '.mat', {'vecmag_bins': vecmag_bins, 'bins': bins, 'hx': hx, 'hy': hy, 'hz': hz, 'hv': hv, 'files': files})
    print outmat

    font = {'family' : 'DejaVu Sans',
            'weight' : 'normal',
            'size'   : 18}
    
    rc('font', **font)

    hFig = plt.figure();
    hFig.set_size_inches(11, 8.5)  # landscape

    majorFormatter = FormatStrFormatter('%d')
    yMajorLoc = MultipleLocator(10)
    yMinorLoc = MultipleLocator(5)
    plt.minorticks_on

    # title
    ht = plt.title('SAMS 200 Hz Vibratory Data (Mean Subtracted) for\nSensor %s from GMT %s through %s' % (sensor, start, stop))
    #ht.set_fontsize(16)

    bins_mg = vecmag_bins/1e-3
    pctiles = 100*np.cumsum(hv)/np.sum(hv)
    hLine, = plt.plot(bins_mg, pctiles, linewidth=3, color='k')  # note comma for tuple unpacking on LHS gets hLine out of list returned
    plt.xlabel('Acceleration Vector Magnitude (milli-g)')
    num_pts_str = "{:,.0f} data pts".format(num_pts)
    bbox = {'fc': '0.8', 'pad': 4}
    font0 = FontProperties()
    font = font0.copy()
    font.set_size(9)
    # plt.text(-0.01, 103.0, num_pts_str, {'ha': 'center', 'va': 'center', 'bbox': bbox}, rotation=0, fontproperties=font)

    # FIXME can we get text annotation with num_pts_str to find its own location somehow
    #an2 = ax.annotate("Test 2", xy=(1, 0.5), xycoords=an1.get_window_extent, xytext=(30,0), textcoords="offset points")    
    
    plt.ylabel('Cumulative Distribution (%)')

    # draw typical plumb lines with annotation
    yvals = [50, 95, ]  # one set of annotations for each of these values
    reddots, horlines, verlines, anns, xvals = plumblines(hLine, yvals)

    # get axis settings based on data
    xMajorLoc, xMinorLoc, axlims, yt, xt = get_axis_settings(xvals)
    plt.axis(axlims)
    plt.yticks(yt)
    plt.xticks(xt)

    # now add num_pts text box top/center
    xspan = axlims[1] - axlims[0]
    xtxt = axlims[0] + ( 0.5 * xspan )
    yspan = axlims[3] - axlims[2]
    ytxt = axlims[2] + 0.98* yspan
    plt.text(xtxt, ytxt, num_pts_str, {'ha': 'center', 'va': 'center', 'bbox': bbox}, rotation=0, fontproperties=font)

    # set xaxis major tick
    plt.gca().xaxis.set_major_locator(xMajorLoc)
    plt.gca().xaxis.set_major_formatter(majorFormatter)
    
    # set yaxis major tick
    plt.gca().yaxis.set_major_locator(yMajorLoc)
    plt.gca().yaxis.set_major_formatter(majorFormatter)    
    
    # for the minor ticks, use no labels; default NullFormatter
    plt.gca().xaxis.set_minor_locator(xMinorLoc)    
    plt.gca().yaxis.set_minor_locator(yMinorLoc)    
    plt.gca().grid(True, which='both', linestyle='dashed')

    outpdf = outmat.replace('.mat', '.pdf')    
    plt.savefig(outpdf)
    print "evince", outpdf, "&"


def plotnsave_daterange_histpad(start, stop, sensor='121f03', fc=200):

    # load bins and vecmag_bins
    name_bins_mat = 'dailyhistpad_bins_%d.mat' % fc
    # a = sio.loadmat(os.path.join(DEFAULT_OUTDIR, 'dailyhistpad_bins.mat'))  # DELETEME
    a = sio.loadmat(os.path.join(DEFAULT_HISTDIR, name_bins_mat))
    vecmag_bins = a['vecmag_bins'][0]
    bins = a['bins'][0]

    hv = np.zeros_like(vecmag_bins)
    hx = np.zeros_like(bins)
    hy = np.zeros_like(bins)
    hz = np.zeros_like(bins)

    files = []
    for d in pd.date_range(start, stop):
        f = os.path.join(datetime_to_dailyhist_path(d, sensor_subdir=sensor2subdir(sensor)), 'dailyhistpad.mat')
        if os.path.exists(f):
            files.append(f)
            data = sio.loadmat(f)
            hv += data['Nv'][0]
            hx += data['Nx'][0]
            hy += data['Ny'][0]
            hz += data['Nz'][0]
            num_pts = np.sum(hv)
            # print '%s %d %s' % (d.date(), np.sum(hv), f)
            print "{} {:20,.0f} {}".format(str(d.date()), num_pts, f)
    print ''

    # output filename relative to common path
    outdir = os.path.join(DEFAULT_HISTDIR, 'plots')
    outname = '%s_to_%s_%s' % (start, stop, sensor)
    outstub = os.path.join(outdir, outname)

    # save to output mat file
    outmat = outstub + '.mat'
    sio.savemat(outstub + '.mat',
                {'vecmag_bins': vecmag_bins, 'bins': bins, 'hx': hx, 'hy': hy, 'hz': hz, 'hv': hv, 'files': files})
    print outmat

    # ################################################
    # plot vector magnitude cumulative distribution
    # ################################################

    ylabstr = 'Cumulative Distribution (%)'
    xlab_prefix = 'Acceleration Vector Magnitude'
    bins_mg = vecmag_bins / 1e-3
    pctiles = 100 * np.cumsum(hv) / np.sum(hv)

    font = {'family': 'DejaVu Sans',
            'weight': 'normal',
            'size': 18}

    rc('font', **font)

    hFig = plt.figure()
    hFig.set_size_inches(11, 8.5)  # landscape

    majorFormatter = FormatStrFormatter('%d')
    yMajorLoc = MultipleLocator(10)
    yMinorLoc = MultipleLocator(5)
    plt.minorticks_on

    # title
    ht = plt.title(
        'SAMS 200 Hz Vibratory Data (Mean Subtracted) for\nSensor %s from GMT %s through %s' % (sensor, start, stop))
    # ht.set_fontsize(16)

    hLine, = plt.plot(bins_mg, pctiles, linewidth=3,
                      color='k')  # note comma for tuple unpacking on LHS gets hLine out of list returned
    plt.xlabel('%s (milli-g)' % xlab_prefix)
    num_pts_str = "{:,.0f} data pts".format(num_pts)
    bbox = {'fc': '0.8', 'pad': 4}
    font0 = FontProperties()
    font = font0.copy()
    font.set_size(9)
    # plt.text(-0.01, 103.0, num_pts_str, {'ha': 'center', 'va': 'center', 'bbox': bbox}, rotation=0, fontproperties=font)

    # FIXME can we get text annotation with num_pts_str to find its own location somehow
    # an2 = ax.annotate("Test 2", xy=(1, 0.5), xycoords=an1.get_window_extent, xytext=(30,0), textcoords="offset points")

    plt.ylabel(ylabstr)

    # draw typical plumb lines with annotation
    #yvals = [50, 95, ]  # one set of annotations for each of these values
    yvals = [50, 99.9, ]  # one set of annotations for each of these values
    reddots, horlines, verlines, anns, xvals = plumblines(hLine, yvals)

    # get axis settings based on data
    xMajorLoc, xMinorLoc, axlims, yt, xt = get_axis_settings(xvals)
    plt.axis(axlims)
    plt.yticks(yt)
    plt.xticks(xt)

    # now add num_pts text box top/center
    xspan = axlims[1] - axlims[0]
    xtxt = axlims[0] + (0.5 * xspan)
    yspan = axlims[3] - axlims[2]
    ytxt = axlims[2] + 0.98 * yspan
    plt.text(xtxt, ytxt, num_pts_str, {'ha': 'center', 'va': 'center', 'bbox': bbox}, rotation=0, fontproperties=font)

    # set xaxis major tick
    plt.gca().xaxis.set_major_locator(xMajorLoc)
    plt.gca().xaxis.set_major_formatter(majorFormatter)

    # set yaxis major tick
    plt.gca().yaxis.set_major_locator(yMajorLoc)
    plt.gca().yaxis.set_major_formatter(majorFormatter)

    # for the minor ticks, use no labels; default NullFormatter
    plt.gca().xaxis.set_minor_locator(xMinorLoc)
    plt.gca().yaxis.set_minor_locator(yMinorLoc)
    plt.gca().grid(True, which='both', linestyle='dashed')

    outpdf = outmat.replace('.mat', '_vcdf.pdf')  # xyzh
    plt.savefig(outpdf)
    print "evince", outpdf, "&"

    # ################################################
    #  plot xyz probability densities
    # ################################################

    ylabstr = 'Probability Density (%)'
    xlab_prefix = 'Acceleration'
    bins_mg = bins / 1e-3
    xvalues = 100 * hx / np.sum(hx)
    yvalues = 100 * hy / np.sum(hy)
    zvalues = 100 * hz / np.sum(hz)
    num_pts = np.sum(hx)
    num_pts_str = "{:,.0f} records".format(num_pts)

    hFig = plt.figure()
    hFig.set_size_inches(11, 8.5)  # landscape

    # title
    ht = plt.title(
        'SAMS 200 Hz Vibratory Data (Mean Subtracted) for\nSensor %s from GMT %s through %s' % (sensor, start, stop))
    # ht.set_fontsize(16)

    hLineX, = plt.plot(bins_mg, xvalues, linewidth=2,
                      color='r')  # note comma for tuple unpacking on LHS gets hLine out of list returned
    hLineY, = plt.plot(bins_mg, yvalues, linewidth=2,
                      color='g')  # note comma for tuple unpacking on LHS gets hLine out of list returned
    hLineZ, = plt.plot(bins_mg, zvalues, linewidth=2,
                      color='b')  # note comma for tuple unpacking on LHS gets hLine out of list returned
    plt.xlabel('%s (milli-g)' % xlab_prefix)
    plt.ylabel('Probability Density (%)')

    # get axis settings based on data
    xMajorLoc, xMinorLoc, axlims2, yt, xt = get_axis_settings_xyz(xvalues, yvalues, zvalues, axlims)
    plt.axis(axlims2)
    plt.yticks(yt)
    plt.xticks(xt)

    # branch based on returned ax limits
    if axlims2[3] < 2:
        yMajorFormatter = FormatStrFormatter('%0.1f')
        yMajorLoc = MultipleLocator(0.1)
        yMinorLoc = MultipleLocator(0.05)
    else:
        yMajorFormatter = FormatStrFormatter('%d')
        yMajorLoc = MultipleLocator(1)
        yMinorLoc = MultipleLocator(0.5)
    plt.minorticks_on

    # now add num_pts text box top/center
    xspan = axlims2[1] - axlims2[0]
    xtxt = axlims2[0] + (0.5 * xspan)
    yspan = axlims2[3] - axlims2[2]
    ytxt = axlims2[2] + 0.98 * yspan
    plt.text(xtxt, ytxt, num_pts_str, {'ha': 'center', 'va': 'center', 'bbox': bbox}, rotation=0, fontproperties=font)

    # set xaxis major tick
    plt.gca().xaxis.set_major_locator(xMajorLoc)
    plt.gca().xaxis.set_major_formatter(majorFormatter)

    # set yaxis major tick
    plt.gca().yaxis.set_major_locator(yMajorLoc)
    plt.gca().yaxis.set_major_formatter(yMajorFormatter)

    # for the minor ticks, use no labels; default NullFormatter
    plt.gca().xaxis.set_minor_locator(xMinorLoc)
    plt.gca().yaxis.set_minor_locator(yMinorLoc)
    plt.gca().grid(True, which='both', linestyle='dashed')

    plt.legend((hLineX, hLineY, hLineZ), ('X-Axis', 'Y-Axis', 'Z-Axis'))

    outpdf = outmat.replace('.mat', '_xyzp.pdf')  # xyzp
    plt.savefig(outpdf)
    print "evince", outpdf, "&"


def plotnsave_histmatfiles(files, sensor, tag):

    # load bins and vecmag_bins    
    if sensor.endswith('006'):
        bname_bins_matfile = 'dailyhistpad_bins_006.mat'            
    elif sensor.endswith('020'):
        bname_bins_matfile = 'dailyhistpad_bins_020.mat'
    else:
        bname_bins_matfile = 'dailyhistpad_bins_200.mat'

    # load bins and vecmag_bins
    a = sio.loadmat(os.path.join(DEFAULT_HISTDIR, bname_bins_matfile))
    vecmag_bins = a['vecmag_bins'][0][:-1]
    bins = a['bins'][0][:-1]    

    hv = np.zeros_like(vecmag_bins)
    hx = np.zeros_like(bins)
    hy = np.zeros_like(bins)
    hz = np.zeros_like(bins)
    
    for f in files:
        if f is not None and os.path.exists(f):
            data = sio.loadmat(f)
            hv += data['Nv'][0]
            hx += data['Nx'][0]
            hy += data['Ny'][0]
            hz += data['Nz'][0]
            num_pts = np.sum(hv)
            d = ymd_pathstr_to_date(f)
            #print '%s %d %s' % (d.date(), np.sum(hv), f)
            print "{} {:20,.0f} {}".format(str(d), num_pts, f)
    print ''
    
    # output filename relative to common path
    outdir = os.path.join(DEFAULT_HISTDIR, 'plots')
    outname = '%s_%s' % (tag, sensor)
    outstub = os.path.join(outdir, outname)
    
    # save to output mat file
    outmat = outstub + '.mat'
    sio.savemat(outstub + '.mat', {'vecmag_bins': vecmag_bins, 'bins': bins, 'hx': hx, 'hy': hy, 'hz': hz, 'hv': hv, 'files': files})
    print outmat

    font = {'family' : 'DejaVu Sans',
            'weight' : 'normal',
            'size'   : 18}
    
    rc('font', **font)

    hFig = plt.figure();
    hFig.set_size_inches(11, 8.5)  # landscape

    majorFormatter = FormatStrFormatter('%d')
    yMajorLoc = MultipleLocator(10)
    yMinorLoc = MultipleLocator(5)
    plt.minorticks_on

    my_units = 'milli-g'
    x_units = 'mg'
    title_hz = '200 Hz'
    sf = 1e-3
    if sensor.endswith('006'):
        my_units = 'micro-g'
        x_units = 'ug'
        title_hz = '6 Hz'
        sf = 1e-6
    elif sensor.endswith('020'):
        my_units = 'micro-g'
        x_units = 'ug'
        title_hz = '20 Hz'
        sf = 1e-6
        
    # title
    ht = plt.title('SAMS %s Vibratory Data (Mean Subtracted) for\nSensor %s (%s)' % (title_hz, sensor, tag))
    #ht.set_fontsize(16)
    
    xbins = vecmag_bins / sf
    pctiles = 100*np.cumsum(hv)/np.sum(hv)
    hLine, = plt.plot(xbins, pctiles, linewidth=3, color='k')  # note comma for tuple unpacking on LHS gets hLine out of list returned
    plt.xlabel('Acceleration Vector Magnitude (%s)' % my_units)
    num_pts_str = "{:,.0f} data pts".format(num_pts)
    bbox = {'fc': '0.8', 'pad': 4}
    font0 = FontProperties()
    font = font0.copy()
    font.set_size(9)
    #plt.text(-2.2, 108.5, num_pts_str, {'ha': 'center', 'va': 'center', 'bbox': bbox}, rotation=45, fontproperties=font)
    
    # FIXME can we get text annotation with num_pts_str to find its own location somehow
    #an2 = ax.annotate("Test 2", xy=(1, 0.5), xycoords=an1.get_window_extent, xytext=(30,0), textcoords="offset points")    
    
    plt.ylabel('Cumulative Distribution (%)')

    # draw typical plumb lines with annotation
    yvals = [50, 95, ]  # one set of annotations for each of these values
    reddots, horlines, verlines, anns, xvals = plumblines(hLine, yvals, x_units=x_units)

    # get axis settings based on data
    xMajorLoc, xMinorLoc, axlims, yt, xt = get_axis_settings(xvals)
    plt.axis(axlims)
    plt.yticks(yt)
    plt.xticks(xt)
    
    plt.text(axlims[1], 50, num_pts_str, {'ha': 'center', 'va': 'center', 'bbox': bbox}, rotation=90, fontproperties=font)    
    
    # set xaxis major tick
    plt.gca().xaxis.set_major_locator(xMajorLoc)
    plt.gca().xaxis.set_major_formatter(majorFormatter)
    
    # set yaxis major tick
    plt.gca().yaxis.set_major_locator(yMajorLoc)
    plt.gca().yaxis.set_major_formatter(majorFormatter)    
    
    # for the minor ticks, use no labels; default NullFormatter
    plt.gca().xaxis.set_minor_locator(xMinorLoc)    
    plt.gca().yaxis.set_minor_locator(yMinorLoc)    
    plt.gca().grid(True, which='both', linestyle='dashed')

    outpdf = outmat.replace('.mat', '.pdf')    
    plt.savefig(outpdf)
    print "evince", outpdf, "&"


def plotnsave_monthrange_histpad(start, stop, sensor='121f03'):

    # "floor" start date to begin of month
    start = start.replace(day=1)
    
    # "ceil" stop date to end of month
    stop = (stop.replace(day=1) + datetime.timedelta(days=32) - datetime.timedelta(days=1)).replace(day=1)
    stop -= datetime.timedelta(days=1)
    
    # FIXME we could tap into monthly saved files instead of stepping day-by-day (DIFFERENT VAR NAMES IN MONTHLY THOUGH)
    plotnsave_daterange_histpad(start, stop, sensor='121f03')


def save_range_of_months(year, moStart, moStop, sensor='121f03'):
    for mo in range(moStart, moStop+1):
        print '######### MONTH%02d ################' % mo
        save_monthlyhistpad(year, mo, sensor=sensor)


class CreateMatFile(object):
    """
    It's easy to write code that does the right thing when everything is going
    well. It's much harder to write code that does a good job when things go
    wrong. Properly manipulating exceptions can help you troubleshoot problems.
    
    A problem could arise with the traceback for an exception that shows the
    problem starting in e.g. get_matfile. When debugging problems, it's
    enormously helpful to know the real origin, which might be in e.g. do_run.
    
    To solve that problem, we'll store more than the exception, we'll also store
    the traceback at the time of the original problem, e.g. in get_matfile, we
    use the full three-argument form of the raise statement to use the original
    traceback too!!!
    
    Now when we run it, the traceback points to dailyhistpad_matsave, called
    from e.g. do_run, which is the real culprit (not from e.g. get_matfile).
    
    The three-argument raise statement is a little odd, owing to
    its legacy from the old days of Python when exceptions could be things
    other than instances of subclasses of Exception. This accounts for the odd
    tuple-dance we do on the saved exc_info.
    
    """
    
    def __init__(self, day, sensor, where=None):
        self.day = day
        self.sensor = sensor
        self.where = where
        self.exc_info = None
        self.mat_file = None
         
    def do_run(self):
        try:
            self.mat_file = self.dailyhistpad_matsave()
        except Exception, e:
            self.exc_info = sys.exc_info()
     
    def dailyhistpad_matsave(self):
        """do_something_dangerous"""
        
        if self.where is None:
            self.where = get_where_clause(self.sensor)

        if self.sensor.endswith('006'):
            #bins = np.arange(-0.2, 0.2-5e-5, 5e-5) / 1e3
            #vecmag_bins = np.arange(0, 0.5, 5e-5) / 1e3
            bname_bins_matfile = 'dailyhistpad_bins_006.mat'            
        elif self.sensor.endswith('020'):
            #bins = np.arange(-0.2, 0.2-5e-5, 5e-5) / 1e1
            #vecmag_bins = np.arange(0, 0.5, 5e-5) / 1e1
            bname_bins_matfile = 'dailyhistpad_bins_020.mat'
        elif 199 < self.where['CutoffFreq'] < 205:
            #bins = np.arange(-0.2, 0.2-5e-5, 5e-5)
            #vecmag_bins = np.arange(0, 0.5, 5e-5)
            bname_bins_matfile = 'dailyhistpad_bins_200.mat'
        else:
            raise Exception('unhandled use case for CutoffFreq or sample rate implied by 006 sensor suffix')

        # load bins and vecmag_bins
        a = sio.loadmat(os.path.join(DEFAULT_HISTDIR, bname_bins_matfile))
        vecmag_bins = a['vecmag_bins'][0]
        bins = a['bins'][0]

        #save_dailyhistpad(self.day, self.day, self.sensor, self.where)            
        save_dailyhistpad(self.day, self.day, sensor=self.sensor, where=self.where, bins=bins, vecmag_bins=vecmag_bins)
    
    def get_matfile(self):
        """get_result"""
        
        # this is that odd python legacy tuple dance here
        if self.exc_info: raise self.exc_info[1], None, self.exc_info[2]
        return self.mat_file
    

def process_date_list_from_file(fname, sensor):
    files = []
    where = get_where_clause(sensor)
    with open(fname, 'r') as infile:
        for line in infile:
            ymd_path = line.rstrip('\n')
            mat_file = os.path.join(ymd_path, sensor2subdir(sensor), 'dailyhistpad.mat')
            if os.path.exists(mat_file):
                print 'padrunhist mat file exists {}'.format(mat_file)
            else:
                print 'padrunhist mat file create {}'.format(mat_file)
                day = ymd_pathstr_to_date(mat_file)
                cmf = CreateMatFile(day, sensor, where=where)
                print 'doing histogram processing for our running mat file result'
                cmf.do_run()
                print 'now we have mat file for', day
                mat_file = cmf.get_matfile()
            files.append(mat_file)
    return files



def pad_percentiles_from_date_list_file(fname, sensor):

    files = []
    where = get_where_clause(sensor)
    with open(fname, 'r') as infile:
        for line in infile:
            ymd_path = line.rstrip('\n')
            d = ymd_pathstr_to_date(ymd_path)

            # get list of PAD data files for particular day and sensor
            pth = os.path.join( datetime_to_ymd_path(d), sensor2subdir(sensor) )
            if os.path.exists(pth):
                tmp = os.listdir(pth)
                files = [ os.path.join(pth, f) for f in tmp ]
    
                # now filter files
                my_files = get_pad_day_sensor_files_minbytes(files, d.strftime('%Y-%m-%d'), sensor, min_bytes=2*1024*1024)            
                summary = '%s %s gives %d files' % (pth, d.strftime('%Y-%m-%d'), len(my_files))

                #for pad_file in my_files:
                #    p = pad_file_percentiles(pad_file)
                #    print ' > {:9.4f} ug    {:9.4f} ug'.format(p[0]/1e-6, p[1]/1e-6)            

                n = np.empty((0, 1))
                sum50 = np.empty((0, 1))
                sum95 = np.empty((0, 1))
                arr = np.empty((0, 4))
                for fname in my_files:
                    # read data from file (not using double type here like MATLAB would, so we get courser demeaning)
                    b = padread(fname)
                    a = b - b.mean(axis=0)       # demean each column
                    #a = np.delete(a, 0, 1)       # delete first (time) column
                    a[:,0] = np.sqrt(a[:,1]**2 + a[:,2]**2 + a[:,3]**2)  # replace 1st column with vecmag
                    #print '{:e}  {:e}  {:e}  {:e}'.format(*p)
                    arr = np.append(arr, a, axis=0)
                p = np.percentile(np.abs(arr[:, 0]), [50, 95], axis=0)
                s = ' > {:6.2f} ug  {:6.2f} ug'.format(p[0]/1e-6, p[1]/1e-6)
                
                n = np.append(n, arr.shape[0], axis=0)
                sum50 = np.append(sum50, p[0]/1e-6, axis=0)
                sum95 = np.append(sum95, p[1]/1e-6, axis=0)
                
                print s, arr.shape, summary
                print n
                print sum50
                print sum95


#import sys
#sensor = 'es05006' # sys.argv[1]
#fname = '/home/pims/Documents/CIR_PaRIS_Based_on_es05_spgs_below_20Hz_QUIETER.txt' # sys.argv[2] # 
#pad_percentiles_from_date_list_file(fname, sensor)
#sys.exit('bye')


if __name__ == '__main__':

    import sys
    
    # PROCESS/SAVE example (e.g. playing catch-up for a sensor)
    # ./main.py -s SENSOR -d STARTDATE  -e STOPDATE
    # ./main.py -s 121f05 -d 2017-01-01 -e 2017-09-30
    
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
    #print args
    
    # handle the case when we get ad hoc dates from file (not typical date range)
    if args.fromfile is not None:
        
        # for each date in list, verify padrunhist.mat exists along typical path (if not, then try to create it)
        hist_mat_files = process_date_list_from_file(args.fromfile, args.sensor)

        # parse tag out of fromfile name
        bname_noext = os.path.splitext(args.fromfile)[0]
        tag = bname_noext.split('_')[-1]

        if args.plot:
            # create plot for this ad hoc list of dates
            plotnsave_histmatfiles(hist_mat_files, args.sensor, tag)
        
    else:    
        if args.plot:
            plotnsave_daterange_histpad(args.start, args.stop, sensor=args.sensor)
        else:
            save_dailyhistpad(args.start, args.stop, sensor=args.sensor, indir=args.paddir, outdir=args.histdir)
