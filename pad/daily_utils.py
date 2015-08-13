#!/usr/bin/env python

import os
import sys

from pims.utils.pimsdateutil import datestr_to_datetime, datetime_to_ymd_path
from pims.pad.padquarantine import grep_sample_rate, file_rate_tuples

SENSOR_SUBDIRS = [
    'sams2_accel_121f02',
    'sams2_accel_121f03',
    'sams2_accel_121f04',
    'sams2_accel_121f05',
    'sams2_accel_121f08',
    'mams_accel_hirap',
    'sams2_accel_121f02006',
    'sams2_accel_121f03006',
    'sams2_accel_121f04006',
    'sams2_accel_121f05006',
    'sams2_accel_121f08006',
    'mams_accel_hirap006' ]  

# return number of samples (16 bytes = [t,x,y,z] record is "one sample") in PAD data file
def get_num_samples(dat_file):
    """return number of samples (16 bytes = [t,x,y,z] record is "one sample") in PAD data file"""    
    return os.path.getsize(dat_file) / 16.0
    
# return total seconds from sensor subdir; get sample rate from each header & derive seconds from companion data file
def get_total_seconds(subdir):
    """return total seconds from sensor subdir; get sample rate from each header & derive seconds from companion data file"""
    
    # get list of (file, rate) tuples sorted by rate
    r = grep_sample_rate(subdir)
    hdr_list = file_rate_tuples(r)
    #print hdr_list

    # get total seconds from sum of T (= N / fs ) for each dat file
    dat_files_seconds = [ get_num_samples(t[0].replace('.header','')) / t[1] for t in hdr_list ]
    total_seconds = sum(dat_files_seconds)
    return total_seconds

# show total pad hours for core sensors for yoda ymd path given by date_str
def show_pad_hours_for_day(date_str, subdirs):
    """show total pad hours for core sensors for yoda ymd path given by date_str"""
    pth = datetime_to_ymd_path(datestr_to_datetime(date_str))   
    for sensor_subdir in subdirs:
        subdir = os.path.join(pth, sensor_subdir)           
        try:
            total_sec = get_total_seconds(subdir)
        except Exception, e:
            total_sec = 0
        print '{0:>5.1f} {1:s}'.format(total_sec / 3600.0, subdir)

if __name__ == "__main__":
    
    day_range = DayRange(one,two)
    
    date_str = sys.argv[1]
    
    if len(sys.argv) == 3:
        my_set = sys.argv[2]
    else:
        my_set = 'all'
        
    if my_set == 'all':
        my_subdirs = SENSOR_SUBDIRS
    elif my_set == '006':
        my_subdirs = [ sd for sd in SENSOR_SUBDIRS if sd.endswith('006') ]
    elif my_set == 'cut':
        my_subdirs = [ sd for sd in SENSOR_SUBDIRS if not sd.endswith('006') ]
    
    #show_pad_hours_for_day('2015-07-02', SENSOR_SUBDIRS)
    show_pad_hours_for_day(date_str, my_subdirs)