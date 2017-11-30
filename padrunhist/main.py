#!/usr/bin/env python

"""Running histogram(s) of acceleration vector magnitude.

This module provides classes for computing/plotting running histograms of SAMS (PAD file) data.

"""

import os
import datetime
import numpy as np
import pandas as pd
import scipy.io as sio
from pathlib import Path
from dateutil import parser
from matplotlib import pyplot as plt

import phargparser
from pims.utils.pimsdateutil import datetime_to_ymd_path, datetime_to_dailyhist_path, year_month_to_dtm_start_stop
from pims.files.filter_pipeline import FileFilterPipeline, BigFile
from histpad.pad_filter_pipeline import PadDataDaySensorWhere, sensor2subdir
from histpad.file_disposal import DailyHistFileDisposal, DailyMinMaxFileDisposal

DEFAULT_PADDIR = phargparser.DEFAULT_PADDIR
DEFAULT_HISTDIR = phargparser.DEFAULT_HISTDIR


class DateRangeException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def get_date_range(value):
    if value is None:
        # is None, so set to most recent week's range
        dr = pd.date_range(DAYONE, periods=7, normalize=True)
    elif isinstance(value, list) and len(value) == 2:
        # a list of 2 objects, we will try to shoehorn into a pandas date_range
        try:
            dr = pd.date_range(value[0], value[1])
        except Exception as exc:
            raise DateRangeException(str(exc))
    elif isinstance(value, pd.DatetimeIndex):
        # ftw, we have pandas date_range
        dr = value
    else:
        # not None, not pd.DatetimeIndex and not len=2 list that nicely converted
        raise TypeError('see pandas for date_range info')
    return dr


def get_pad_day_sensor_files_minbytes(files, day, sensor, min_bytes=2*1024*1024):

    # Initialize callable classes that act as filters for our pipeline
    file_filter1 = PadDataDaySensorWhere(day, sensor)  # fc = 200 Hz
    file_filter2 = BigFile(min_bytes=min_bytes)  # at least 2 MB
    
    # Initialize processing pipeline with callable classes, but not using file list as input yet
    ffp = FileFilterPipeline(file_filter1, file_filter2)
    #print ffp

    # Now apply processing pipeline to file list; at this point, ffp is callable
    return list( ffp(files) )


def save_dailyhistpad(start, stop, sensor='121f03', where={'CutoffFreq': 200}, bins=np.arange(-0.2, 0.2, 5e-5), vecmag_bins=np.arange(0, 0.5, 5e-5), min_bytes=2*1024*1024, indir=DEFAULT_PADDIR, outdir=DEFAULT_HISTDIR):

    dr = get_date_range([start, stop])
    for d in dr:
    
        day = d.strftime('%Y-%m-%d')

        # Get list of PAD data files for particular day and sensor
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
        f = os.path.join(datetime_to_dailyhist_path(d), 'dailyhistpad.mat')
        if os.path.exists(f):
            files.append(f)
            data = sio.loadmat(f)
            hv += data['Nv'][0]
            hx += data['Nx'][0]
            hy += data['Ny'][0]
            hz += data['Nz'][0]
            print '%s %d' % (d.date(), np.sum(hv))
    print ''
    
    # output filename relative to common path
    outdir = os.path.join(DEFAULT_HISTDIR, 'plots')
    outname = '%s_to_%s_%s' % (start, stop, sensor)
    outstub = os.path.join(outdir, outname)
    
    # save to output mat file
    outmat = outstub + '.mat'
    sio.savemat(outstub + '.mat', {'vecmag_bins': vecmag_bins, 'bins': bins, 'hx': hx, 'hy': hy, 'hz': hz, 'hv': hv, 'files': files})
    print outmat

    outpng = outmat.replace('.mat', '.png')
    plt.plot(vecmag_bins, hv)
    plt.savefig(outpng)
    print outpng


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
    
    args = phargparser.parse_inputs()
    print args
    
    save_dailyhistpad(args.start, args.stop, sensor=args.sensor, indir=args.paddir, outdir=args.histdir)

    # Example of playing catch-up for one sensor
    # ./main.py -s SENSOR -d STARTDATE  -e STOPDATE
    # ./main.py -s 121f05 -d 2017-01-01 -e 2017-09-30
    