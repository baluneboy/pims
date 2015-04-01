#!/usr/bin/env python

import os
import sys
import datetime
import subprocess
from dateutil import parser
from collections import OrderedDict
from interval import Interval, IntervalSet

from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop
from pims.pad.loose_pad_intervalset import LoosePadIntervalSet
from pims.utils.pimsdateutil import datetime_to_doytimestr, floor_minute, ceil_minute
from pims.files.utils import extract_sensor_from_headers_list

# find header files for given year/month/day
def find_headers(ymd_dir):
    """find header files for given year/month/day"""
    if not os.path.exists(ymd_dir):
        raise OSError('%s does not exist' % ymd_dir)
    #cmd = 'find ' + ymd_dir + ' -maxdepth 2 -type f -name "*header" -exec basename {} \; | grep -v 006'
    cmd = 'find ' + ymd_dir + ' -maxdepth 2 -type f -name "*header" | grep -v 006'
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
def OBSOLETEprocess_header_files(dstart, dstop, maxgapsec, sensor_list):
    """process headers over range of days"""
    d = dstart
    while d <= dstop:
        print '\n%s' % d
        print '=' * 99
        thisday_interval = Interval( d, d + datetime.timedelta(days=1) )
        thisday_intervalset = IntervalSet( (thisday_interval,) )
        sensor_list_gaps = IntervalSet()
        ymd_dir = datetime_to_ymd_path(d)
        headers_all = find_headers(ymd_dir)
        sensors = list( set( extract_sensor_from_headers_list(headers_all) ) )
        #sensors.sort()

        for sensor in sensors:
            if sensor in sensor_list:

                header_files = [ x for x in headers_all if x.endswith(sensor + '.header') ]
                #header_files.sort()
                sensor_day_interval_set = get_loose_interval_set_from_header_filenames(header_files, maxgapsec)

                #print '-' * 55
                #print d.date(), 'maxgapsec =', maxgapsec, sensor, len(header_files), len(sensor_day_interval_set)
                #for i in sensor_day_interval_set:
                #    print i.lower_bound, i.upper_bound

                # now set of gaps are these
                sensor_gaps_interval_set = thisday_intervalset - sensor_day_interval_set
                sensor_day_total_gap_minutes = 0
                for gap in sensor_gaps_interval_set:
                    sensor_day_total_gap_minutes += (gap.upper_bound - gap.lower_bound).total_seconds() / 60.0
                    #print '%s, %.1f minutes, %s, %s' % (sensor, sensor_day_total_gap_minutes, gap.lower_bound, gap.upper_bound)
                    sensor_list_gaps.add(gap)

        # FIXME explain what is being shown (gaps, intervals, DSM convenient output or wtf?)
        #
        # THIS IS WHAT DSM OUTPUT LOOKS LIKE (WIDER RANGES):
        # day084_part1 2015:084:06:30:00 to 2015:084:06:49:00
        # day084_part2 2015:084:07:37:00 to 2015:084:08:19:00
        # day084_part3 2015:084:14:26:00 to 2015:084:15:17:00
        # day084_part4 2015:084:18:44:00 to 2015:084:18:55:00
        # day084_part5 2015:084:19:15:00 to 2015:084:19:54:00
        # 
        # day085_part1 2015:085:08:01:00 to 2015:085:08:12:00
        # day085_part2 2015:085:15:28:00 to 2015:085:16:10:00
        # day085_part3 2015:085:16:44:00 to 2015:085:17:24:00
        # 
        # day086_part1 2015:086:06:06:00 to 2015:086:06:17:00
        # day086_part2 2015:086:12:57:00 to 2015:086:13:53:00
        # day086_part3 2015:086:14:34:00 to 2015:086:15:08:00
        # day086_part4 2015:086:16:17:00 to 2015:086:16:40:00
        # day086_part5 2015:086:17:38:00 to 2015:086:18:10:00
        # day086_part6 2015:086:19:46:00 to 2015:086:19:52:00
        # day086_part7 2015:086:21:18:00 to 2015:086:21:25:00
        # day086_part8 2015:086:22:41:00 to 2015:086:23:09:00
        # 
        # day087_part1 2015:087:06:40:00 to 2015:087:07:14:00
        # day087_part2 2015:087:15:15:00 to 2015:087:16:03:00
        # day087_part3 2015:087:16:27:00 to 2015:087:17:03:00
        # day087_part4 2015:087:18:06:00 to 2015:087:18:55:00
        # day087_part5 2015:087:19:53:00 to 2015:087:20:24:00
        # day087_part6 2015:087:21:43:00 to 2015:087:22:44:00
        #
        # THIS IS WHAT GAPS OUTPUT LOOKS LIKE (PRECISE RANGES):
        # maxgapsec = 1.5 seconds
        # -----------------------
        # gap 2015:084:06:30:00.123456 to 2015:084:06:49:00.123456
        #
        # THIS IS WHAT INTERVALS OUTPUT LOOKS LIKE (PRECISE RANGES)
        # start = START
        # stop  = STOP
        # -----------------------
        # interval 2015:084:06:30:00.123456 to 2015:084:06:49:00.123456        
        
        for g in sensor_list_gaps:
            gap_minutes = (g.upper_bound - g.lower_bound).total_seconds() / 60.0
            if gap_minutes > 2:
                t1 = datetime_to_doytimestr( floor_minute( g.lower_bound ))
                t2 = datetime_to_doytimestr(  ceil_minute( g.upper_bound ))
                print '{0:>6.1f} minutes, from {1:<24s} to {2:>24s}'.format(gap_minutes, t1, t2)
        d += datetime.timedelta(days=1)

class LooseSensorDayIntervals(object):
    
    def __init__(self, start, stop, maxgapsec):
        self.start = start
        self.stop = stop
        self.maxgapsec = maxgapsec
        self.headers, self.intervals = self.get_headers_intervals()
        self.gaps = self.get_gaps()

    # get header files and intervals per sensor/day from start to stop
    def get_headers_intervals(self):
        """get header files and intervals per sensor/day from start to stop"""       
        d = self.start
        headers = {}
        intervals = {}
        while d <= self.stop:
            ymd_dir = datetime_to_ymd_path(d)
            headers_all = find_headers(ymd_dir)
            sensors = list( set( extract_sensor_from_headers_list(headers_all) ) )
            for sensor in sensors:
                header_files = [ x for x in headers_all if x.endswith(sensor + '.header') ]
                sensor_day_interval_set = get_loose_interval_set_from_header_filenames(header_files, self.maxgapsec)
                headers[(sensor,d.date())] = header_files
                intervals[(sensor,d.date())] = sensor_day_interval_set
            d += datetime.timedelta(days=1)
        ordered_headers = OrderedDict( sorted(headers.items()) )            
        ordered_intervals = OrderedDict( sorted(intervals.items()) )
        return ordered_headers, ordered_intervals

    # get gaps (the opposite of intervals) per sensor/day from start to stop
    def get_gaps(self):
        """get gaps (the opposite of intervals) per sensor/day from start to stop"""
        gaps = {}
        for k, interval_set in self.intervals.iteritems():
            sensor, day = k[0], k[1]
            sensor_gaps = IntervalSet()
            this_datetime = datetime.datetime.combine(day, datetime.datetime.min.time())
            thisday_interval = Interval( this_datetime, this_datetime + datetime.timedelta(days=1) )
            thisday_intervalset = IntervalSet( (thisday_interval,) )
            sensor_gaps_interval_set = thisday_intervalset - interval_set
            sensor_day_total_gap_minutes = 0
            for gap in sensor_gaps_interval_set:
                sensor_day_total_gap_minutes += (gap.upper_bound - gap.lower_bound).total_seconds() / 60.0
                sensor_gaps.add(gap)
            gaps[(sensor,this_datetime.date())] = sensor_gaps
        ordered_gaps = OrderedDict( sorted(gaps.items()) )
        return ordered_gaps

    # show per sensor from start through stop
    def show(self, what='intervals'):
        """show intervals per sensor from start to stop"""
        startstr = self.start.strftime('%Y-%m-%d')
        stopstr  = max([self.stop, self.start + datetime.timedelta(days=1)]).strftime('%Y-%m-%d')
        if what in ['intervals', 'gaps']:
            s = 'START = {0:<24s}\nSTOP  = {1:<24s}\nmaxgapsec = {2:<.3f} seconds'.format(startstr, stopstr, self.maxgapsec)
            s += self._get_intervalstr(what)
        else:
            # must just want to see header files
            s = 'START = {0:<24s}\nSTOP  = {1:<24s}'.format(startstr, stopstr)
            s += self._get_headerstr()
        print s
        return

    def _get_countstr(self, sensor, day):
        num_headers = len( self.headers[(sensor, day)] )
        num_intervals = len( self.intervals[(sensor, day)] )
        num_gaps = len( self.gaps[(sensor, day)] )
        s = '%s %s has %d headers, %d intervals, and %d gaps with maxgapsec = %.3f' % (
            day.strftime('%Y-%m-%d'), sensor, num_headers, num_intervals, num_gaps, self.maxgapsec)        
        return s

    # get headers as string, per sensor from start through stop
    def _get_headerstr(self):
        """get headers as string, per sensor from start through stop"""
        s = ''
        for k, header_files in self.headers.iteritems():
            sensor, day = k[0], k[1]
            s += '\n\n%s' % self._get_countstr(sensor, day)
            i = 0
            for h in header_files:
                i += 1
                s += '\n%d %s' % (i, h)
        return s

    # get intervals (or gaps) as string, per sensor from start through stop
    def _get_intervalstr(self, what):
        """get intervals (or gaps) as string, per sensor from start through stop"""
        s = ''
        if 'intervals' == what:
            items = self.intervals
        elif 'gaps' == what:
            items = self.gaps
        else:
            raise Exception('unhandled exception for "what = %s"' % what)
            return s
        for k, intervals in items.iteritems():
            sensor, day = k[0], k[1]
            s += '\n\n%s' % self._get_countstr(sensor, day)
            c = 0
            total_sec = 0
            for i in intervals:
                c += 1
                t1 = datetime_to_doytimestr(i.lower_bound)[0:-3]
                t2 = datetime_to_doytimestr(i.upper_bound)[0:-3]
                dursec = (i.upper_bound - i.lower_bound).total_seconds()
                total_sec += dursec
                if dursec < 60.0:
                    durstr = '{0:>8.2f} seconds'.format(dursec)
                else:
                    durstr = '{0:>8.2f} minutes'.format(dursec / 60.0)                    
                s += '\n{0:<22s} {1:>22s} {2:>16s} {3:<9s} {4:3s} {5:<5d}'.format(t1, t2, durstr, sensor, what[0:3], c)
            s += '\nTOTAL HOURS = {0:<4.1f} for {1:s} on {2:s}'.format(total_sec / 3600.0, sensor, str(day))
        return s

        # FIXME explain what is being shown (gaps, headers/intervals, DSM convenient output or wtf?)
        #
        # THIS IS WHAT DSM OUTPUT LOOKS LIKE (WIDER RANGES):
        # day084_part1 2015:084:06:30:00 to 2015:084:06:49:00
        # day084_part2 2015:084:07:37:00 to 2015:084:08:19:00
        # day084_part3 2015:084:14:26:00 to 2015:084:15:17:00
        # day084_part4 2015:084:18:44:00 to 2015:084:18:55:00
        # day084_part5 2015:084:19:15:00 to 2015:084:19:54:00
        # 
        # day085_part1 2015:085:08:01:00 to 2015:085:08:12:00
        # day085_part2 2015:085:15:28:00 to 2015:085:16:10:00
        # day085_part3 2015:085:16:44:00 to 2015:085:17:24:00
        # 
        # day086_part1 2015:086:06:06:00 to 2015:086:06:17:00
        # day086_part2 2015:086:12:57:00 to 2015:086:13:53:00
        # day086_part3 2015:086:14:34:00 to 2015:086:15:08:00
        # day086_part4 2015:086:16:17:00 to 2015:086:16:40:00
        # day086_part5 2015:086:17:38:00 to 2015:086:18:10:00
        # day086_part6 2015:086:19:46:00 to 2015:086:19:52:00
        # day086_part7 2015:086:21:18:00 to 2015:086:21:25:00
        # day086_part8 2015:086:22:41:00 to 2015:086:23:09:00
        # 
        # day087_part1 2015:087:06:40:00 to 2015:087:07:14:00
        # day087_part2 2015:087:15:15:00 to 2015:087:16:03:00
        # day087_part3 2015:087:16:27:00 to 2015:087:17:03:00
        # day087_part4 2015:087:18:06:00 to 2015:087:18:55:00
        # day087_part5 2015:087:19:53:00 to 2015:087:20:24:00
        # day087_part6 2015:087:21:43:00 to 2015:087:22:44:00

def demo_intervals():
    dstart = parser.parse('2015-03-25')
    dstop =  parser.parse('2015-03-30')
    maxgapsec = 17.0 #3.0 * 1/500.0 # 3 data pts at 500 sa/sec
    hig = LooseSensorDayIntervals(dstart, dstop, maxgapsec)
    hig.show('gaps')
    hig.show('intervals')
    
demo_intervals()
raise SystemExit

def demo_gaps():
    dstart = parser.parse('2015-03-29')
    dstop =  parser.parse('2015-03-29')
    maxgapsec = 3.0 * 1/500.0 # 3 data pts at 500 sa/sec
    sensorday_intervals, str_intervals = get_intervals(dstart, dstop, maxgapsec)
    for k, v in sensorday_intervals.iteritems():
        sensor, day = k[0], k[1]
        print sensor, day, v

demo_gaps()
raise SystemExit

def demo1():
    print ''
    dstart = parser.parse('2015-03-29')
    dstop =  parser.parse('2015-03-29')
    maxgapsec = 20 #0.000001
    sensor_list = ['121f02', '121f03', '121f04', '121f05', '121f08']
    process_header_files(dstart, dstop, maxgapsec, sensor_list)

demo1()
raise SystemExit

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
