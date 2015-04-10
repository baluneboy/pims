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
from pims.pad.loose_pad_intervalset import LoosePadIntervalSet, CompareOverlapInterval
from pims.utils.pimsdateutil import datetime_to_doytimestr, floor_minute, ceil_minute
from pims.files.utils import extract_sensor_from_headers_list, tuplify_headers
from pims.utils.iterabletools import pairwise

# find header files for given year/month/day
def find_headers(ymd_dir):
    """find header files for given year/month/day"""
    if not os.path.exists(ymd_dir):
        print('NOTE: %s does not exist' % ymd_dir)
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

class LooseSensorDayIntervals(object):
    
    def __init__(self, start, stop, maxgapsec, base_dir='/misc/yoda/pub/pad'):
        self.start = start
        self.stop = stop
        self.maxgapsec = maxgapsec
        self.base_dir = base_dir
        self.headers, self.intervals = self.get_headers_intervals()
        self.gaps = self.get_gaps()

    # get header files and intervals per sensor/day from start to stop
    def get_headers_intervals(self):
        """get header files and intervals per sensor/day from start to stop"""       
        d = self.start
        headers = {}
        intervals = {}
        while d <= self.stop:
            ymd_dir = datetime_to_ymd_path(d, base_dir=self.base_dir)
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

    def show_dsm(self, keep_sensors):
        master_gaps = LoosePadIntervalSet(maxgapsec=15.0*60.0)
        for k, gaps in self.gaps.iteritems():
            sensor, day = k[0], k[1]
            if sensor in keep_sensors:
                for g in gaps:
                    t1 = floor_minute(g.lower_bound)
                    t2 = ceil_minute( g.upper_bound)
                    master_gaps.add( Interval(t1, t2) )
        for g in master_gaps:
            day = int( g.lower_bound.date().strftime('%j') )
            g1str = datetime_to_doytimestr(g.lower_bound)[0:-7]
            g2str = datetime_to_doytimestr(g.upper_bound)[0:-7]
            print 'day{0:0>3}_partX  {1:<18s} {2:<18s}'.format(day, g1str, g2str)

    def _get_countstr(self, sensor, day):
        num_headers = len( self.headers[(sensor, day)] )
        num_intervals = len( self.intervals[(sensor, day)] )
        num_gaps = len( self.gaps[(sensor, day)] )
        s = '%s %s has %d headers, %d intervals, and %d gaps when maxgapsec = %.3f' % (
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

def compare_yoda_jimmy_files(tup1, tup2):
    """
    
    INPUTS:
    each tup is either like ('year2015/month03...', '/data/pad')      # JIMMY HEADER FILE
                    or like ('year2015/month04...', '/misc/yoda/pad') # YODA  HEADER FILE
                       
    """
    ok_path_parts = ['/data/pad/', '/misc/yoda/pub/pad/']
    if (tup1[1] not in ok_path_parts) or (tup2[1] not in ok_path_parts):
        print 'path part 1st arg is: %s' % tup1[1]
        print 'path part 2nd arg is: %s' % tup2[1]
        print 'okay path parts:', ok_path_parts
        raise Exception('unhandled path part')
    hdr_file1 = os.path.join(tup1[1],tup1[0])
    start1, stop1 = pad_fullfilestr_to_start_stop(hdr_file1)
    cmp_interval1 = CompareOverlapInterval(start1, stop1)
    hdr_file2 = os.path.join(tup2[1],tup2[0])
    start2, stop2 = pad_fullfilestr_to_start_stop(hdr_file2)
    cmp_interval2 = CompareOverlapInterval(start2, stop2)
    if tup1[1] == '/misc/yoda/pub/pad/':
        yoda_tup = (hdr_file1, cmp_interval1)
        jimmy_tup = (hdr_file2, cmp_interval2)
    else:
        yoda_tup = (hdr_file2, cmp_interval2)
        jimmy_tup = (hdr_file1, cmp_interval1)
    return yoda_tup, jimmy_tup

def rough_kpi_merge_for_march2015(higJimmy, higYoda):
    """merge played back intervals (for SAMS) with PAD on yoda to improve estimate of PAD hours"""
    s = ''
    for k, intervals in higJimmy.intervals.iteritems():
        sensor, day = k[0], k[1]
        y = higYoda.intervals[k]
        for j in intervals:
            y.add(j)
        c = 0
        total_sec = 0
        for i in y.intervals:
            c += 1
            t1 = datetime_to_doytimestr(i.lower_bound)[0:-3]
            t2 = datetime_to_doytimestr(i.upper_bound)[0:-3]
            dursec = (i.upper_bound - i.lower_bound).total_seconds()
            total_sec += dursec
        s += '\n{2:s},{1:s},{0:.1f}'.format(total_sec / 3600.0, sensor, str(day))
    return s

def rough_kpi_for_march2015():
    dstart = parser.parse('2015-03-01')
    dstop =  parser.parse('2015-03-31')
    maxgapsec = 0.001
    higJimmy = LooseSensorDayIntervals(dstart, dstop, maxgapsec, base_dir='/data/pad')
    higYoda = LooseSensorDayIntervals(dstart, dstop, maxgapsec, base_dir='/misc/yoda/pub/pad')
    s = rough_kpi_merge_for_march2015(higJimmy, higYoda)
    print s
    
#rough_kpi_for_march2015()
#raise SystemExit

def demo_intervals():
    dstart = parser.parse('2015-03-08')
    dstop =  parser.parse('2015-04-08')
    maxgapsec = 17.0 #3.0 * 1/500.0 # 3 data pts at 500 sa/sec
    hig = LooseSensorDayIntervals(dstart, dstop, maxgapsec, base_dir='/misc/yoda/pub/pad')
    #hig.show('headers')
    #hig.show('intervals')
    hig.show('gaps')
    #hig.show_dsm(['121f02','121f03', '121f04', '121f05', '121f08'])

#demo_intervals()
#raise SystemExit

def do_trim(session, hdr, side, overlap_sec):
    cmd = "C = padtrim('%s', '%s', %f);" % (hdr, side, overlap_sec)
    print cmd
    #session.run(cmd)
    #count = session.getvalue('C');
    #print count, hdr

def demo_trim_pad_via_headers():
    #import pymatlab
    session = None #pymatlab.session_factory()

    dstart = parser.parse('2015-03-12')
    dstop =  parser.parse('2015-03-31')
    maxgapsec = 17.0 #3.0 * 1/500.0 # 3 data pts at 500 sa/sec
    hig_jimmy = LooseSensorDayIntervals(dstart, dstop, maxgapsec, base_dir='/data/pad')
    hig_yoda = LooseSensorDayIntervals(dstart, dstop, maxgapsec, base_dir='/misc/yoda/pub/pad')
    for sensday, hdrs in hig_jimmy.headers.iteritems():
        headers = tuplify_headers(hdrs) # jimmy headers
        headers += tuplify_headers(hig_yoda.headers[sensday]) # and yoda headers
        sensor, day = sensday
        print 'Working on %s for %s' % (sensor, day)
        hdr_list = sorted(headers, key = lambda x: x[0])
        for f1, f2 in pairwise(hdr_list):
            if f1[1] != f2[1]:
                print '-' * 11
                yoda_tup, jimmy_tup = compare_yoda_jimmy_files(f1, f2)
                if jimmy_tup[1] in yoda_tup[1]:
                    #print 'jimmy file TOTALLY WITHIN yoda file'
                    #print yoda_tup[1].lower_bound, 'YODA START'
                    #print jimmy_tup[1].lower_bound, 'JIMM START'
                    #print jimmy_tup[1].upper_bound, 'JIMM STOP'
                    #print yoda_tup[1].upper_bound, 'YODA STOP'
                    pass
                elif jimmy_tup[1].overlaps_left( yoda_tup[1] ):
                    print 'jimmy file LEFT OVERLAPS yoda file'
                    print jimmy_tup[1].lower_bound, 'JIMM START'
                    print yoda_tup[1].lower_bound, 'YODA START'
                    print jimmy_tup[1].upper_bound, 'JIMM STOP'
                    print yoda_tup[1].upper_bound, 'YODA STOP'
                    hdr = jimmy_tup[0]
                    side = 'left'
                    overlap_sec = (yoda_tup[1].lower_bound - jimmy_tup[1].lower_bound).total_seconds()
                    do_trim(session, hdr, side, overlap_sec)
                elif jimmy_tup[1].overlaps_right( yoda_tup[1] ):
                    print 'jimmy file RIGHT OVERLAPS yoda file'
                    print yoda_tup[1].lower_bound, 'YODA START'
                    print jimmy_tup[1].lower_bound, 'JIMM START'
                    print yoda_tup[1].upper_bound, 'YODA STOP'                    
                    print jimmy_tup[1].upper_bound, 'JIMM STOP'
                    hdr = jimmy_tup[0]
                    side = 'right'
                    overlap_sec = (jimmy_tup[1].upper_bound - yoda_tup[1].upper_bound).total_seconds()
                    do_trim(session, hdr, side, overlap_sec)                    
                else:
                    print 'jimmy file DOES NOT OVERLAP yoda file'
                    hdr = jimmy_tup[0]
                    side = 'neither'
                    overlap_sec = 0.0
                    do_trim(session, hdr, side, overlap_sec)                    
                    #print yoda_tup[1].lower_bound, 'YODA START'
                    #print yoda_tup[1].upper_bound, 'YODA STOP'                    
                    #print jimmy_tup[1].lower_bound, 'JIMM START'
                    #print jimmy_tup[1].upper_bound, 'JIMM STOP'
    
    #del session
    
demo_trim_pad_via_headers()
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
