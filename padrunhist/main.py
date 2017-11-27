#!/usr/bin/env python

"""Running histogram(s) of acceleration vector magnitude.

This module provides classes for plotting running histograms of SAMS (PAD file) data.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

"""

import os
import re
import datetime
import numpy as np
from dateutil import parser
from matplotlib import pyplot as plt

from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.utils.datetime_ranger import DateRange, next_day
from pims.files.filter_pipeline import FileFilterPipeline, BigFile
from histpad.pad_filter_pipeline import PadDataDaySensorWhere


def get_pad_day_sensor_files_minbytes(files, day, sensor):

    # Initialize callable classes that act as filters for our pipeline
    file_filter1 = PadDataDaySensorWhere(day, sensor)  # fc = 200 Hz
    file_filter2 = BigFile(min_bytes=2*1024*1024)  # at least 2 MB
    
    # Initialize processing pipeline with callable classes, but not using file list as input yet
    ffp = FileFilterPipeline(file_filter1, file_filter2)
    #print ffp

    # Now apply processing pipeline to file list; at this point, ffp is callable
    return list( ffp(files) )


def get_padhist_files(start, stop, sensor='121f03', file_getter=get_pad_day_sensor_files_minbytes):
    
    nd = next_day(start)
    d = start
    while d < stop:
        d = nd.next()
        day = d.strftime('%Y-%m-%d')

        # Get list of PAD data files for particular day and sensor
        pth = os.path.join( datetime_to_ymd_path(d), 'sams2_accel_' + sensor )
        if os.path.exists(pth):
            tmp = os.listdir(pth)
            files = [ os.path.join(pth, f) for f in tmp ]    
                    
            # Run routine to filter files
            my_files = file_getter(files, day, sensor)
            print '%s gives %d files' % (day, len(my_files))
            
            # run routine to get histograms (x,y,z,v) and add to running tally for the day/sensor
            for f in my_files:
                print f
            
        else:
            print '%s gives NO FILES' % day


if __name__ == '__main__':


    start = datetime.date(2017, 6, 1)
    stop = datetime.date(2017, 6, 2)
    files = get_padhist_files(start, stop)
