#!/usr/bin/env python

"""Running histogram(s) of acceleration vector magnitude.

This module provides classes for computing/plotting running histograms of SAMS (PAD file) data.

"""

import os
import glob
import datetime
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
from pims.utils.pimsdateutil import datetime_to_ymd_path, datetime_to_dailyhist_path, year_month_to_dtm_start_stop
from pims.files.filter_pipeline import FileFilterPipeline, BigFile
from histpad.pad_filter_pipeline import PadDataDaySensorWhere, sensor2subdir
from histpad.file_disposal import DailyHistFileDisposal, DailyMinMaxFileDisposal

DEFAULT_PADDIR = argparser.DEFAULT_PADDIR
DEFAULT_HISTDIR = argparser.DEFAULT_HISTDIR


def list_mat_files(glob_pat):
    """print length of filenames list that matches input glob pattern"""
    fnames = glob.glob(glob_pat)
    print len(fnames)

#list_mat_files('/misc/yoda/www/plots/batch/results/dailyhistpad/year2017/month*/day*/*_accel_121f03/dailyhistpad.mat')
#list_mat_files('/misc/yoda/pub/pad/year2017/month*/day*/*_accel_121f03006/*header')
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


def get_pad_day_sensor_files_minbytes(files, day, sensor, min_bytes=2*1024*1024):

    # initialize callable classes that act as filters for our pipeline
    if sensor.endswith('006'):
        dwhere = {'CutoffFreq': 6.0}
    elif sensor.startswith('es0'):
        dwhere = {'CutoffFreq': 204.2}
    else:
        dwhere = {'CutoffFreq': 200}
    file_filter1 = PadDataDaySensorWhere(day, sensor, where=dwhere)  # fc = 200 Hz (or 204.2 Hz)
    file_filter2 = BigFile(min_bytes=min_bytes)                      # at least 2 MB
    
    # initialize processing pipeline with callable classes, but not using file list as input yet
    ffp = FileFilterPipeline(file_filter1, file_filter2)
    #print ffp

    # now apply processing pipeline to file list; at this point, ffp is callable
    return list( ffp(files) )


def demo_pad_pct99(sensor, y, m, d):
    from ugaudio.load import padread
    ymd_dir = datetime_to_ymd_path(datetime.date(y, m, d))
    glob_pat = '%s/*_accel_%s/*%s' % (ymd_dir, sensor, sensor)
    fnames = glob.glob(glob_pat)
    fnames_filt = get_pad_day_sensor_files_minbytes(fnames, '%4d-%02d-%02d' % (y, m, d), sensor, min_bytes=2*1024*1024)
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


def demo_99pct_vecmag_array(drange, sensor):
    pcts = np.empty((0, 4), np.float)
    for d in drange:
        pct = demo_pad_pct99(sensor, d.year, d.month, d.day)
        pcts = np.append(pcts, pct, axis=0)
        print '{:9}  {:4}  {:02}  {:02}'.format(pcts.shape[0], d.year, d.month, d.day)

    plt.plot(pcts[:,0] * 1e3)
    plt.ylabel('99th Pctile of Accel. Mag. (mg)')
    plt.title(sensor)
    plt.show()
    
dr = pd.date_range('2017-09-01', '2017-12-01')
sensor = '121f03006'
demo_99pct_vecmag_array(dr, sensor)
raise SystemExit


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
    save_dailyhistpad(start, stop, sensor='121f03', where={'CutoffFreq': 200}, bins=np.arange(-0.2, 0.2, 5e-5), vecmag_bins=np.arange(0, 0.5, 5e-5), min_bytes=2*1024*1024)


def save_monthlyhistpad(year, month, sensor='121f03'):

    # load bins and vecmag_bins
    a = sio.loadmat(os.path.join(DEFAULT_HISTDIR, 'dailyhistpad_bins.mat'))
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
    if xvals_max > 15:
        mult = 25
        xMajorLoc = MultipleLocator(2)
        xMinorLoc = MultipleLocator(1)
    xmax = round_up(max(xvals), mult)
    axlims = [-1, xmax, -5, 105]
    yticks = np.arange(0, 104, 5)
    xticks = np.arange(xmax)
    return xMajorLoc, xMinorLoc, axlims, yticks, xticks


def plotnsave_daterange_histpad(start, stop, sensor='121f03'):

    # load bins and vecmag_bins
    a = sio.loadmat(os.path.join(DEFAULT_HISTDIR, 'dailyhistpad_bins.mat'))
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

    # note the comma for tuple unpacking on LHS to get hLine out of list that gets returned
    bins_mg = vecmag_bins/1e-3
    pctiles = 100*np.cumsum(hv)/np.sum(hv)
    hLine, = plt.plot(bins_mg, pctiles, linewidth=3, color='k')
    plt.xlabel('Acceleration Vector Magnitude (milli-g)')
    num_pts_str = "{:,.0f} data pts".format(num_pts)
    bbox = {'fc': '0.8', 'pad': 4}
    font0 = FontProperties()
    font = font0.copy()
    font.set_size(9)
    plt.text(-2.2, 108.5, num_pts_str, {'ha': 'center', 'va': 'center', 'bbox': bbox}, rotation=45, fontproperties=font)
    
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
        
        
if __name__ == '__main__':

    # PROCESS/SAVE example (e.g. playing catch-up for a sensor)
    # ./main.py -s SENSOR -d STARTDATE  -e STOPDATE
    # ./main.py -s 121f05 -d 2017-01-01 -e 2017-09-30
    
    # PLOT example for daterange
    # ./main.py -s SENSOR -d STARTDATE  -e STOPDATE --plot
    # ./main.py -s 121f03 -d 2017-01-01 -e 2017-03-30 --plot

    args = argparser.parse_inputs()
    print args
    
    if args.plot:
        plotnsave_daterange_histpad(args.start, args.stop, sensor=args.sensor)
    else:
        save_dailyhistpad(args.start, args.stop, sensor=args.sensor, indir=args.paddir, outdir=args.histdir)
