#!/usr/bin/env python

import os
import sys
import datetime
import subprocess
from dateutil import parser
from interval import Interval, IntervalSet
from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop
from pims.pad.loose_pad_intervalset import LoosePadIntervalSet
from pims.utils.pimsdateutil import datetime_to_doytimestr, floor_minute, ceil_minute

# find header files for given year/month/day
def find_headers(ymd_dir):
    """find header files for given year/month/day"""
    if not os.path.exists(ymd_dir):
        raise OSError('%s does not exist' % ymd_dir)
    cmd = 'find ' + ymd_dir + ' -maxdepth 2 -type f -name "*header" -exec basename {} \; | grep -v 006'
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p.communicate()
    splitout = out.split('\n')[:-1] # split on newlines & get rid of very last trailing newline
    return splitout

# get loose pad interval set from header filenames
def get_loose_interval_set_from_header_filenames(header_files, maxgapsec):
    """get loose pad interval set from header filenames"""
    interval_set = LoosePadIntervalSet(maxgapsec=maxgapsec)
    for header_file in header_files:
        dtStartFilename, dtStopFilename = pad_fullfilestr_to_start_stop(header_file)
        interval_set.add( Interval( dtStartFilename, dtStopFilename ) )
    return interval_set

# process headers over range of days
def process_header_files(dstart, dstop, maxgapsec, sensor_list):
    """process headers over range of days"""
    d = dstart
    while d <= dstop:
        print '\n%s' % d
        print '=' * 99
        this_day_interval = Interval( d, d + datetime.timedelta(days=1) )
        this_day_interval_set = IntervalSet( (this_day_interval,) )
        sensor_list_gaps = IntervalSet()
        ymd_dir = datetime_to_ymd_path(d)
        header_files_all_sensors = find_headers(ymd_dir)
        sensors = list( set([ x[48:].rstrip('header')[:-1] for x in header_files_all_sensors ]) )
        sensors.sort()
        for sensor in sensors:
            if sensor in sensor_list:
                header_files = [ x for x in header_files_all_sensors if x.endswith(sensor + '.header') ]
                header_files.sort()
                sensor_day_interval_set = get_loose_interval_set_from_header_filenames(header_files, maxgapsec)
                #print '-' * 55
                #print d.date(), 'maxgapsec =', maxgapsec, sensor, len(header_files), len(sensor_day_interval_set)
                #for i in sensor_day_interval_set:
                #    print i.lower_bound, i.upper_bound
                # now set of gaps are these
                sensor_gaps_interval_set = this_day_interval_set - sensor_day_interval_set
                #print '-' * 55
                sensor_day_total_gap_minutes = 0
                for gap in sensor_gaps_interval_set:
                    sensor_day_total_gap_minutes += (gap.upper_bound - gap.lower_bound).total_seconds() / 60.0
                    #print '%s, %.1f minutes, %s, %s' % (sensor, sensor_day_total_gap_minutes, gap.lower_bound, gap.upper_bound)
                    sensor_list_gaps.add(gap)

        for g in sensor_list_gaps:
            gap_minutes = (g.upper_bound - g.lower_bound).total_seconds() / 60.0
            if gap_minutes > 2:
                t1 = datetime_to_doytimestr( floor_minute( g.lower_bound ))
                t2 = datetime_to_doytimestr(  ceil_minute( g.upper_bound ))
                print '{0:>6.1f} minutes, from {1:<24s} to {2:>24s}'.format(gap_minutes, t1, t2)
        d += datetime.timedelta(days=1)

def demo1():
    print ''
    dstart = parser.parse('2015-03-24')
    dstop =  parser.parse('2015-03-28')
    maxgapsec = 20 #0.000001
    sensor_list = ['121f02', '121f03', '121f04', '121f05', '121f08']
    process_header_files(dstart, dstop, maxgapsec, sensor_list)

#demo1()
#raise SystemExit

# iterate over day directory (only sams2 subdirs for now)
def main(daydir):
    """iterate over day directory (only sams2 subdirs for now)"""
    # get sams2 directories
    subdirs = [ i for i in os.listdir(daydir) if os.path.isdir(os.path.join(daydir, i)) ]
    sams2_subdirs = [ i for i in subdirs if i.startswith('sams2_accel_') ]
    check_dirs = [ os.path.join(daydir, sd) for sd in sams2_subdirs ]
    for sams2dir in check_dirs:
        count1 = process_header_files(sams2dir)
        count2 = process_amplitudes(sams2dir)
        print 'length of quarantined list is %d + %d = %d for %s' % (count1, count2, count1 + count2, sams2dir)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        d2 = datetime.datetime.now().date() - datetime.timedelta(days=2)
        daydir = datetime_to_ymd_path(d2)
    else:
        daydir = sys.argv[1]
    main(daydir)
