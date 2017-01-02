#!/usr/bin/env python

import sys
import datetime

from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop, format_datetime_as_pad_underscores    

def pad_start_stop(fname):
    start, stop = pad_fullfilestr_to_start_stop(fname)
    return start, stop

def pad_stop(fname):
    start, stop = pad_start_stop(fname)
    return stop

def remedy_start(fname):
    start, stop = pad_start_stop(fname)   
    rem_start = stop + datetime.timedelta(seconds=1)
    return rem_start

def remedy(fname):
    #                                                                           LESS_THAN_DATETME
    #python /home/pims/dev/programs/python/packet/resample.py fcNew=6 dateStart=2015_08_07_00_00_00.000 dateStop=2015_08_08_00_00_00.000 sensor=121f02
    date_start = remedy_start(fname)
    date_stop = datetime.datetime(*date_start.timetuple()[:3]) + datetime.timedelta(days=1)
    if (date_start.hour < 23):
        cmd = 'python /home/pims/dev/programs/python/packet/resample.py fcNew=6'
    else:
        cmd = 'echo SKIP python /home/pims/dev/programs/python/packet/resample.py fcNew=6'
    cmd += ' dateStart=' + format_datetime_as_pad_underscores(date_start)
    cmd += ' dateStop=' + format_datetime_as_pad_underscores(date_stop)
    cmd += ' sensor='
    return cmd
    
if __name__ == "__main__":
    if len(sys.argv) == 3:
        action = sys.argv[1]
        fname = sys.argv[2]
        if action == 'remedy':
            cmd = eval( action + "('" + fname + "')" )
            print cmd
        else:
            gmt = eval( action + "('" + fname + "')" )
            print format_datetime_as_pad_underscores(gmt)
