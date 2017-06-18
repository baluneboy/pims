#!/usr/bin/env python

import os
import re
import sys
import datetime
import subprocess
import shutil
from dateutil import parser
from collections import OrderedDict
from interval import Interval, IntervalSet
import numpy as np

from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop, format_datetime_as_pad_underscores
from pims.pad.loose_pad_intervalset import LoosePadIntervalSet, CompareOverlapInterval
from pims.utils.pimsdateutil import datetime_to_doytimestr, floor_minute, ceil_minute
from pims.files.utils import extract_sensor_from_headers_list, tuplify_headers, mkdir_original_for_trim, move_pad_pair
from pims.utils.iterabletools import pairwise
from ugaudio.load import padread

# find header files for given year/month/day
def find_headers_without006(ymd_dir):
    """find header files for given year/month/day

    Returns list of header files like:
    ['/misc/yoda/pub/pad/year2015/month03/day21/iss_rad_radgse/2015_03_21_00_30_24.488+2015_03_21_02_30_21.367.radgse.header', ...]

    >>> ymd_dir = '/misc/yoda/test/pad/year2015/month04/day29'
    >>> L = find_headers_without006(ymd_dir)
    >>> L[0:2]
    ['/misc/yoda/test/pad/year2015/month03/day21/iss_rad_radgse/2015_03_21_00_30_24.488+2015_03_21_02_30_21.367.radgse.header', '/misc/yoda/test/pad/year2015/month03/day21/iss_rad_radgse/2015_03_21_02_30_37.343+2015_03_21_04_30_34.253.radgse.header']
    >>> len(L)
    987
    
    """    
    if not os.path.exists(ymd_dir):
        print('NOTE: %s does not exist' % ymd_dir)
    #cmd = 'find ' + ymd_dir + ' -maxdepth 2 -type f -name "*header" -exec basename {} \; | grep -v 006'
    cmd = 'find ' + ymd_dir + ' -maxdepth 2 -type f -name "*header" | grep -v 006.header'
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p.communicate()
    splitout = out.split('\n')[:-1] # split on newlines & get rid of very last trailing newline
    return splitout


# get loose pad interval set from header filenames
def get_loose_interval_set_from_header_filenames(header_files, maxgapsec):
    """get loose pad interval set from header filenames

    Returns LoosePadIntervalSet "loosely built" from list of header_files where
    gaps < maxgapsec are not treated as gaps.

    >>> ymd_dir = '/misc/yoda/test/pad/year2015/month03/day21'
    >>> L = find_headers_without006(ymd_dir)
    >>> header_files = [ i for i in L if i.endswith('121f03.header') ]
    >>> maxgapsec = 17
    >>> interval_set = get_loose_interval_set_from_header_filenames(header_files, maxgapsec)
    >>> len(interval_set)
    5
    >>> [ interval_set[0].lower_bound, interval_set[-1].upper_bound ]
    [datetime.datetime(2015, 3, 21, 0, 4, 45, 628000), datetime.datetime(2015, 3, 22, 0, 5, 41, 967000)]
    
    """
    interval_set = LoosePadIntervalSet(maxgapsec=maxgapsec)
    for header_file in header_files:
        dtStartFilename, dtStopFilename = pad_fullfilestr_to_start_stop(header_file)
        interval_set.add( Interval( dtStartFilename, dtStopFilename ) )
    return interval_set


# headers, intervals, and gaps per sensor-day combination
class LooseSensorDayIntervals(object):
    """headers, intervals, and gaps per sensor-day combination
    
    >>> start = parser.parse('2015-03-22')
    >>> stop  = parser.parse('2015-03-22')
    >>> maxgapsec = 17    
    >>> hig = LooseSensorDayIntervals(start, stop, maxgapsec, base_dir='/misc/yoda/test/pad')
    >>> sensday = ( '121f03', start.date() )
    >>> len(hig.headers[sensday])
    137
    >>> len(hig.intervals[sensday])
    8
    >>> hig.gaps[sensday][0].lower_bound
    datetime.datetime(2015, 3, 22, 0, 0)
    >>> hig.gaps[sensday][-1].upper_bound
    datetime.datetime(2015, 3, 22, 18, 50, 1, 15000)
    
    """
    
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
            headers_all = find_headers_without006(ymd_dir)
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
                    
        prev_day = None
        gap_count = 0
        for g in master_gaps:
            gap_count += 1
            this_day = int( g.lower_bound.date().strftime('%j') )
            g1str = datetime_to_doytimestr(g.lower_bound)[0:-7]
            g2str = datetime_to_doytimestr(g.upper_bound)[0:-7]
            if prev_day is None:
                prev_day = this_day
            if prev_day != this_day:
                print ''
            print 'day{0:0>3}part{1:03d}  {2:<18s} {3:<18s}'.format(this_day, gap_count, g1str, g2str)
            prev_day = this_day

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


# FIXME is this obsolete?
def compare_yoda_jimmy_files(tup1, tup2, ok_path_parts=['/data/pad/', '/misc/yoda/pub/pad/']):
    """
    
    INPUTS:
    each tup is either like ('year2015/month03...', '/data/pad')      # JIMMY HEADER FILE
                    or like ('year2015/month04...', '/misc/yoda/pad') # YODA  HEADER FILE
                       
    """
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


# FIXME keep this in case of emergency
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


# FIXME keep this in case of emergency
def rough_kpi_for_march2015():
    dstart = parser.parse('2015-03-01')
    dstop =  parser.parse('2015-03-31')
    maxgapsec = 0.001
    higJimmy = LooseSensorDayIntervals(dstart, dstop, maxgapsec, base_dir='/data/pad')
    higYoda = LooseSensorDayIntervals(dstart, dstop, maxgapsec, base_dir='/misc/yoda/pub/pad')
    s = rough_kpi_merge_for_march2015(higJimmy, higYoda)
    print s


# demonstrate LooseSensorDayIntervals
def demo_intervals():
    dstart = parser.parse('2016-02-11')
    dstop =  parser.parse('2016-02-12')
    maxgapsec = 17.0

    hig = LooseSensorDayIntervals(dstart, dstop, maxgapsec, base_dir='/misc/yoda/pub/pad')
    #print 'YODA GAPS'
    #hig.show('headers')
    hig.show('gaps')
    #hig.show('intervals')
    
    #print 'JIMMY INTERVALS'
    #jig = LooseSensorDayIntervals(dstart, dstop, maxgapsec, base_dir='/data/pad')
    #jig.show('intervals')

    #hig.show('headers')
    #hig.show('intervals')
    #hig.show_dsm(['121f02','121f03', '121f04', '121f05', '121f08', 'es05', 'es06'])

#demo_intervals()
#raise SystemExit


# prepare for trim: remove header_file from yoda_headers list & move PAD pair to new_path
def preprocess_trim(yoda_headers, header_file, new_path):
    """prepare for trim: remove header_file from yoda_headers list & move PAD pair to new_path"""
    yoda_headers.remove(header_file)
    old_header = move_pad_pair(header_file, new_path)
    return old_header


# get SampleRate and string contents from PAD header file
def get_samplerate_contents(hdr_file):
    """get SampleRate and string contents from PAD header file
    
    Returns tuple (fs, contents) where fs is float and contents is string with header file contents.
    
    >>> hdr_file = '/misc/yoda/test/pad/year2015/month03/day22/sams2_accel_121f08/2015_03_22_23_55_23.946+2015_03_23_00_05_23.960.121f08.header'
    >>> fs, contents = get_samplerate_contents(hdr_file)
    >>> fs
    500.0
    >>> len(contents)
    817
    
    """
    with open(hdr_file, 'r') as f:
        contents = f.read()
        m = re.match('.*\<SampleRate\>(.*)\</SampleRate\>.*', contents.replace('\n', ''))
        if m:
            fs = float( m.group(1) )
        else:
            fs = None
    return fs, contents


# write new, trimmed PAD files (both header and data are changed)
def trim_pad(old_hdr_file, side, sec):
    """write new, trimmed PAD files (both header and data get changed) where
       old_hdr_file is along an elsewhere-created 'original' subdir
    
    >>> old_hdr_file = '/data/test/pad/year2015/month03/day22/sams2_accel_121f08/original/2015_03_22_16_09_59.266+2015_03_22_16_19_59.280.121f08.header'
    >>> side = 'left'
    >>> sec = 15
    >>> trim_pad(old_hdr_file, side, sec)
    >>> old_hdr_file = '/data/test/pad/year2015/month03/day22/sams2_accel_121f08/original/2015_03_22_16_19_59.282+2015_03_22_16_29_59.295.121f08.header'
    >>> side = 'right'
    >>> sec = 30
    >>> trim_pad(old_hdr_file, side, sec)

    """
    # cannot trim zero or less seconds
    if sec <= 0:
        # FIXME weird case of zero trim, just move file pair up one directory and issue warning
        if '/original' not in old_hdr_file:
            raise Exception('cannot trim zero or less seconds from %s' % old_hdr_file)
        new_hdr_file = old_hdr_file.replace('/original', '')
        old_dat_file = old_hdr_file.replace('.header', '')
        new_dat_file = new_hdr_file.replace('.header', '')
        shutil.move(old_hdr_file, new_hdr_file)
        shutil.move(old_dat_file, new_dat_file)
        return
        
    
    # get sample rate and file contents from old_hdr_file file
    fs, contents = get_samplerate_contents(old_hdr_file)
    
    # get data, header, file times and compute new begin/end GMTs for filename
    old_dat_file = old_hdr_file.replace('.header', '')
    start_file, stop_file = pad_fullfilestr_to_start_stop(old_hdr_file)
    data = padread(old_dat_file)
    Nfile = len(data)
    Ntrim = np.ceil(fs * sec)
    if Ntrim >= Nfile:
        raise Exception('cannot trim %d data points, because file only has %d points' % (Ntrim, Nfile))

    # trim side sec
    side = side.lower()
    if side == 'left':
        data = data[Ntrim:, :]
        start_file = start_file + datetime.timedelta(seconds=sec)
    elif side == 'right':
        data = data[:-Ntrim, :]
    else:
        raise Exception('unhandled side to trim %s', side)
    trimstr = ' and %s TRIM %.3f SECONDS' % (side.upper(), sec)
    Nnew = len(data)
    num_sec = (Nnew-1) / fs
    stop_file = start_file + datetime.timedelta( seconds=num_sec )   

    # new time vector from len(new_data)
    N = float(len(data))
    T = float(N/fs)
    data[:,0] = np.linspace(0, T, N, endpoint=False)

    # get new (start,stop) for filenames for use in old file's parent dir (old now in "original" subdir)
    yoda_path = os.path.dirname( os.path.dirname(old_hdr_file) )
    sensor = os.path.basename(old_dat_file).split('.')[-1]
    startstr = format_datetime_as_pad_underscores(start_file)
    stopstr  = format_datetime_as_pad_underscores(stop_file)
    name_stub =  startstr + '-' + stopstr + '.' + sensor
    new_dat_file = os.path.join(yoda_path, name_stub)
    new_hdr_file = new_dat_file + '.header'
    
    # change 2 fields: TimeZero and GData
    contents = re.sub(r'\<TimeZero\>(.*)\</TimeZero\>', r'<TimeZero>%s</TimeZero>' % startstr, contents)    
    newdatfilestr = os.path.basename(new_dat_file)
    contents = re.sub(r'\<GData format="binary 32 bit IEEE float little endian" file="(.*)...', r'<GData format="binary 32 bit IEEE float little endian" file="%s"/>' % newdatfilestr, contents)
    
    # write new PAD header file
    with open(new_hdr_file, 'w') as f:
        f.write(contents)

    # write new PAD data file
    data.astype('float32').tofile(new_dat_file)


# for given (sensor, day) combination with associated yoda header files and jimmy intervals, trim PAD files
def process_yoda_header_files(yoda_headers, jimmy_intervals, new_path):
    """for given (sensor, day) combination with associated yoda header files and jimmy intervals, trim PAD files"""
    print 'we start with %d yoda headers' % len(yoda_headers)
    for i in jimmy_intervals:
        interval_start = i.lower_bound
        interval_stop = i.upper_bound
        for hdr in yoda_headers:
            file_start, file_stop = pad_fullfilestr_to_start_stop(hdr)
            if file_start >= interval_start and file_stop <= interval_stop:
                print 'move to original %s' % hdr
                old_header = preprocess_trim(yoda_headers, hdr, new_path)
            elif file_start <= interval_stop and file_stop >= interval_stop:
                print 'left trim AFTER move to original %s' % hdr
                old_header = preprocess_trim(yoda_headers, hdr, new_path)
                overlap_sec = (interval_stop - file_start).total_seconds()
                trim_pad(old_header, 'left', overlap_sec)
            elif file_stop >= interval_start and file_start <= interval_start:
                print 'right trim AFTER move to original %s' % hdr
                old_header = preprocess_trim(yoda_headers, hdr, new_path)
                overlap_sec = (file_stop - interval_start).total_seconds()                
                trim_pad(old_header, 'right', overlap_sec)               
            else:
                #print 'ignore %s' % hdr
                pass
        print 'now have %d yoda headers' % len(yoda_headers)
        print '-' * 11


# do PAD trim from start to stop with results going into YODA_DIR based on gap fill from JIMMY_DIR
def trim_span(start, stop, maxgapsec=17, JIMMY_DIR='/data/pad', YODA_DIR='/misc/yoda/pub/pad'):
    """do PAD trim from start to stop with results going into YODA_DIR based on gap fill from JIMMY_DIR"""
    hig_jimmy = LooseSensorDayIntervals(start, stop, maxgapsec, base_dir=JIMMY_DIR)
    hig_yoda = LooseSensorDayIntervals(start, stop, maxgapsec, base_dir=YODA_DIR)
    for sensday, intervals in hig_jimmy.intervals.iteritems():
        sensor, day = sensday
        print 'Working on %s for %s' % (sensor, day)
        
        #print hig_yoda.headers[sensday][0]
        
        # make "original" subdir on yoda for this sensday
        new_path = mkdir_original_for_trim(hig_yoda.headers[sensday][0])

        # classify & process yoda headers for this sensor/day combo
        process_yoda_header_files(hig_yoda.headers[sensday], intervals, new_path)

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


def do_main():
    if len(sys.argv) < 2:
        d2 = datetime.datetime.now().date() - datetime.timedelta(days=2)
        daydir = datetime_to_ymd_path(d2)
    else:
        daydir = sys.argv[1]
    main(daydir)

    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
