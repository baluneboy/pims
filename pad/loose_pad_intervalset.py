#! /usr/bin/env python

import datetime
from interval import Interval, IntervalSet
from pims.utils.pimsdateutil import datetime_to_ymd_path, pad_fullfilestr_to_start_stop


class CompareOverlapInterval(Interval):
    
    def overlaps_left(self, other):
        """Tells whether the given interval overlaps other AND overhangs to its left.
        
        Returns True if the one Interval overlaps other and overhangs on its left.
        If they are immediately adjacent, then this returns False.  Use the adjacent_to
        function for testing for adjacent Intervals.

        >>> r1  = CompareOverlapInterval.less_than(-100)
        >>> r2  = CompareOverlapInterval.less_than_or_equal_to(-100)
        >>> r3  = CompareOverlapInterval.less_than(100)
        >>> r4  = CompareOverlapInterval.less_than_or_equal_to(100)
        >>> r5  = CompareOverlapInterval.all()
        >>> r6  = CompareOverlapInterval.between(-100, 100, False)
        >>> r7  = CompareOverlapInterval(-100, 100, lower_closed=False)
        >>> r8  = CompareOverlapInterval.greater_than(-100)
        >>> r9  = CompareOverlapInterval.equal_to(-100)
        >>> r10 = CompareOverlapInterval(-100, 100, upper_closed=False)
        >>> r11 = CompareOverlapInterval.between(-100, 100)
        >>> r12 = CompareOverlapInterval.greater_than_or_equal_to(-100)
        >>> r13 = CompareOverlapInterval.greater_than(100)
        >>> r14 = CompareOverlapInterval.equal_to(100)
        >>> r15 = CompareOverlapInterval.greater_than_or_equal_to(100)
        >>> r16 = CompareOverlapInterval.between(-10, 10, False)
        >>> r17 = CompareOverlapInterval.between( -1,  1, False)
        >>> r18 = CompareOverlapInterval.between( -8,  1, False)
        >>> r16.overlaps_left(r18)
        True
        >>> r18.overlaps_left(r16)
        False
        >>> r16.overlaps_left(r17)
        True
        >>> r17.overlaps_left(r16)
        False
        >>> r8.overlaps(r9)
        False
        >>> r12.overlaps(r6)
        True
        >>> r7.overlaps(r8)
        True
        >>> r8.overlaps(r4)
        True
        >>> r14.overlaps(r11)
        True
        >>> r10.overlaps(r13)
        False
        >>> r5.overlaps(r1)
        True
        >>> r5.overlaps(r2)
        True
        >>> r15.overlaps(r6)
        False
        >>> r3.overlaps(r1)
        True
        """
        if not self.overlaps(other):
            return False
        if self.lower_bound < other.lower_bound:
            result = True
        else:
            result = False
        return result    

    def overlaps_right(self, other):
        """Tells whether the given interval overlaps other AND overhangs to its right.
        
        Returns True if the one Interval overlaps other and overhangs on its right.
        If they are immediately adjacent, then this returns False.  Use the adjacent_to
        function for testing for adjacent Intervals.

        >>> r16 = CompareOverlapInterval.between(-10, 10, False)
        >>> r17 = CompareOverlapInterval.between(-11,  1, False)
        >>> r18 = CompareOverlapInterval.between( -8,  1, False)
        >>> r19 = CompareOverlapInterval.between( -8, 12, False)       
        >>> r20 = CompareOverlapInterval.between(-10, 12, False)               
        >>> r17.overlaps_right(r16)
        False
        >>> r18.overlaps_right(r16)
        False
        >>> r19.overlaps_right(r16)
        True
        >>> r20.overlaps_right(r16)
        True
        """
        if not self.overlaps(other):
            return False
        if self.upper_bound > other.upper_bound:
            result = True
        else:
            result = False
        return result

class LoosePadIntervalSet(IntervalSet):

    def __init__(self, items=[], maxgapsec=1.5):
        "Initializes the LoosePadIntervalSet"
        if items:
            if not all(isinstance(x, datetime.datetime) for x in items):
                raise TypeError('items must all be datetime type')
        super(LoosePadIntervalSet, self).__init__(items)
        self.maxgapsec = maxgapsec

    def close_enough(self, i1, i2):
        """Tells whether 2 pad intervals are close enough to each other

        Returns True if i1 is close enough to (within maxgapsec seconds of) i2
        meaning if they were joined, then there would be no discontinuity.

        >>> d1 = datetime.datetime(2015,1,1,0,0,0)
        >>> d2 = d1 + datetime.timedelta(seconds=12.345)
        >>> d3 = d2 + datetime.timedelta(seconds=1.6)           # 1.6 sec
        >>> d4 = d3 + datetime.timedelta(seconds=0.5)
        >>> d5 = d4 + datetime.timedelta(seconds=1.5)           # 1.5 sec
        >>> d6 = d5 + datetime.timedelta(seconds=86400.123456)  # over a day
        >>> r1 = Interval(d1, d2)
        >>> r2 = Interval(d3, d4)
        >>> r3 = Interval(d5, d6)
        >>> s = LoosePadIntervalSet()
        >>> s.close_enough(r1, r2) # False
        False
        >>> s.close_enough(r2, r3) # True
        True
        >>> s.close_enough(r1, r3) # False
        False
        >>> s.close_enough(r3, r1) # False
        False
        >>> s.close_enough(r3, r2) # True
        True

        """
        if self.maxgapsec <= 0:
            return False
        if i1.comes_before(i2):
            if (i2.lower_bound - i1.upper_bound).total_seconds() <= self.maxgapsec:
                result = True
            else:
                result = False
        elif i1 == i2:
            result = True
        else:
            result = self.close_enough(i2, i1)
        return result

    def _get_fill(self, i1, i2):
        """Returns an interval from earlier interval's upper_bound to later interval's lower_bound

        >>> d1 = datetime.datetime(2015,1,1,0,0,0)
        >>> d2 = d1 + datetime.timedelta(seconds=12.345)
        >>> d3 = d2 + datetime.timedelta(seconds=1.6)
        >>> d4 = d3 + datetime.timedelta(seconds=0.5)
        >>> d5 = d4 + datetime.timedelta(seconds=60.0)
        >>> d6 = d5 + datetime.timedelta(seconds=86400.123456)
        >>> r1 = Interval(d1, d2)
        >>> r2 = Interval(d3, d4)
        >>> r3 = Interval(d5, d6)        
        >>> s = LoosePadIntervalSet()
        >>> print s._get_fill(r1, r2)
        [datetime.datetime(2015, 1, 1, 0, 0, 12, 345000)..datetime.datetime(2015, 1, 1, 0, 0, 13, 945000)]
        >>> print s._get_fill(r2, r3)
        [datetime.datetime(2015, 1, 1, 0, 0, 14, 445000)..datetime.datetime(2015, 1, 1, 0, 1, 14, 445000)]
        >>> print s._get_fill(r3, r2)
        [datetime.datetime(2015, 1, 1, 0, 0, 14, 445000)..datetime.datetime(2015, 1, 1, 0, 1, 14, 445000)]
        
        """
        
        if i1.comes_before(i2):
            result = Interval(i1.upper_bound, i2.lower_bound)
        else:
            result = Interval(i2.upper_bound, i1.lower_bound)
        return result        

    def add(self, obj):
        """Adds an Interval or discrete value to the object

        >>> d0 = datetime.datetime(2014,12,31,23,59,58)
        >>> d1 = datetime.datetime(2015,1,1,0,0,0)
        >>> d2 = d1 + datetime.timedelta(seconds=12.345)
        >>> d3 = d2 + datetime.timedelta(seconds=1.6)
        >>> d4 = d3 + datetime.timedelta(seconds=0.5)
        >>> d5 = d4 + datetime.timedelta(seconds=60.0)
        >>> d6 = d5 + datetime.timedelta(seconds=86400.123456)
        >>> r1 = Interval(d1, d2)
        >>> r2 = Interval(d3, d4)
        >>> r3 = Interval(d5, d6)        
        >>> r = LoosePadIntervalSet()
        >>> r.add(d0)
        >>> print r
        datetime.datetime(2014, 12, 31, 23, 59, 58)
        >>> r.add(r1)
        >>> print r
        datetime.datetime(2014, 12, 31, 23, 59, 58),[datetime.datetime(2015, 1, 1, 0, 0)..datetime.datetime(2015, 1, 1, 0, 0, 12, 345000)]
        >>> r.add(r2)
        >>> print r
        datetime.datetime(2014, 12, 31, 23, 59, 58),[datetime.datetime(2015, 1, 1, 0, 0)..datetime.datetime(2015, 1, 1, 0, 0, 12, 345000)],[datetime.datetime(2015, 1, 1, 0, 0, 13, 945000)..datetime.datetime(2015, 1, 1, 0, 0, 14, 445000)]
        >>> r.add(r3)
        >>> print r
        datetime.datetime(2014, 12, 31, 23, 59, 58),[datetime.datetime(2015, 1, 1, 0, 0)..datetime.datetime(2015, 1, 1, 0, 0, 12, 345000)],[datetime.datetime(2015, 1, 1, 0, 0, 13, 945000)..datetime.datetime(2015, 1, 1, 0, 0, 14, 445000)],[datetime.datetime(2015, 1, 1, 0, 1, 14, 445000)..datetime.datetime(2015, 1, 2, 0, 1, 14, 568456)]
        
        >>> r = LoosePadIntervalSet()
        >>> r.add(d0)
        >>> print r
        datetime.datetime(2014, 12, 31, 23, 59, 58)
        >>> print r2
        [datetime.datetime(2015, 1, 1, 0, 0, 13, 945000)..datetime.datetime(2015, 1, 1, 0, 0, 14, 445000)]
        >>> r.add(r2)
        >>> print r
        datetime.datetime(2014, 12, 31, 23, 59, 58),[datetime.datetime(2015, 1, 1, 0, 0, 13, 945000)..datetime.datetime(2015, 1, 1, 0, 0, 14, 445000)]
        >>> print r1
        [datetime.datetime(2015, 1, 1, 0, 0)..datetime.datetime(2015, 1, 1, 0, 0, 12, 345000)]
        >>> r.add(r1)
        >>> print r
        datetime.datetime(2014, 12, 31, 23, 59, 58),[datetime.datetime(2015, 1, 1, 0, 0)..datetime.datetime(2015, 1, 1, 0, 0, 12, 345000)],[datetime.datetime(2015, 1, 1, 0, 0, 13, 945000)..datetime.datetime(2015, 1, 1, 0, 0, 14, 445000)]
        >>> print r3
        [datetime.datetime(2015, 1, 1, 0, 1, 14, 445000)..datetime.datetime(2015, 1, 2, 0, 1, 14, 568456)]
        >>> r.add(r3)
        >>> print r
        datetime.datetime(2014, 12, 31, 23, 59, 58),[datetime.datetime(2015, 1, 1, 0, 0)..datetime.datetime(2015, 1, 1, 0, 0, 12, 345000)],[datetime.datetime(2015, 1, 1, 0, 0, 13, 945000)..datetime.datetime(2015, 1, 1, 0, 0, 14, 445000)],[datetime.datetime(2015, 1, 1, 0, 1, 14, 445000)..datetime.datetime(2015, 1, 2, 0, 1, 14, 568456)]

        """
        if isinstance(obj, Interval):
            r = obj
        else:
            r = Interval.equal_to(obj)
        
        if r:   # Don't bother appending an empty Interval
            # If r continuously joins with any of the other
            if not (isinstance(r.lower_bound, datetime.datetime) and isinstance(r.upper_bound, datetime.datetime)):
                raise TypeError('cannot add non-datetime interval or object')
                
            newIntervals = []
            for i in self.intervals:
                if i.overlaps(r) or i.adjacent_to(r):
                    r = r.join(i)
                elif self.close_enough(i, r):
                    gap_int = self._get_fill(i, r)
                    r = r.join(gap_int) # spackle the gap!
                    r = r.join(i)
                else:
                    newIntervals.append(i)
            newIntervals.append(r)
            self.intervals = newIntervals
            self.intervals.sort()

def demo_big_list(dirpath, sensor):
    import re
    from pims.files.utils import filter_filenames
    fullfile_pattern = '(?P<ymdpath>/misc/yoda/pub/pad/year\d{4}/month\d{2}/day\d{2}/)(?P<subdir>.*_(?P<sensor>.*))/(?P<start>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})(?P<pm>[\+\-])(?P<stop>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})\.(?P=sensor)\.header\Z'
    print fullfile_pattern
    suffix = sensor + '.header'
    header_files = [ x for x in filter_filenames(dirpath, re.compile(fullfile_pattern).match) if x.endswith(suffix)]
    return header_files
    
#dirpath = '/misc/yoda/pub/pad/year2015/month03/day17'
#sensor = '121f03'
#big_list = demo_big_list(dirpath, sensor)
#for f in big_list[0:9]: #filter_filenames(dirpath, re.compile(fullfile_pattern).match):
#    print f
#raise SystemExit


def get_pad_data_files(dirpath, sensor):
    import re
    from pims.files.utils import filter_filenames
    fullfile_pattern = '(?P<ymdpath>/misc/yoda/pub/pad/year\d{4}/month\d{2}/day\d{2}/)(?P<subdir>.*_(?P<sensor>.*))/(?P<start>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})(?P<pm>[\+\-])(?P<stop>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})\.(?P=sensor)\Z'
    suffix = sensor # + '.header'
    header_files = [ x for x in filter_filenames(dirpath, re.compile(fullfile_pattern).match) if x.endswith(suffix)]
    return header_files


def demo_show_loose_pad_gaps():
    f1 = '/misc/yoda/pub/pad/2015_03_14_00_05_47.252+2015_03_14_00_15_47.267.121f05.header'
    f2 = '/misc/yoda/pub/pad/2015_03_14_00_15_48.867+2015_03_14_00_25_00.000.121f05.header'
    #t1, t2 = pad_fullfilestr_to_start_stop(f1)
    #t3, t4 = pad_fullfilestr_to_start_stop(f2)
    r = LoosePadIntervalSet(maxgapsec=1) # try 1 to see "not close enough" or 2 for "close enough"
    r.add(padfilename2interval(f1))
    r.add(padfilename2interval(f2))
    
    day_interval = Interval(datetime.datetime(2015, 3, 14, 0, 0, 0), datetime.datetime(2015, 3, 15, 0, 0, 0))
    whole_day_intervalset = IntervalSet( (day_interval,) )
    
    # now set of gaps are thes
    for gap in (whole_day_intervalset - r):
        print gap


def padfilename2interval(fname):
    t1, t2 = pad_fullfilestr_to_start_stop(fname)
    return Interval(t1,t2)

def get_loose_pad_intervalset(day, sensor='121f04', maxgapsec=2, basedir='/misc/yoda/pub/pad'):
    
    # get day interval and "day" PAD ymd path
    tomorrow = day + datetime.timedelta(days=1)
    t1 = datetime.datetime.combine(day, datetime.datetime.min.time())
    t2 = datetime.datetime.combine(tomorrow, datetime.datetime.min.time())
    ymdpath = datetime_to_ymd_path(day, base_dir=basedir)
    
    # initialize loose pad interval set
    s = LoosePadIntervalSet(maxgapsec=maxgapsec)
    
    # build interval set with pad filenames for "yesterday" and "day"
    yesterday = day - datetime.timedelta(days=1)
    file_list = get_pad_data_files(datetime_to_ymd_path(yesterday, base_dir=basedir), sensor) # "yesterday" files
    file_list.extend(get_pad_data_files(ymdpath, sensor)) # extend list with "day" files
    for f in file_list:
        s.add(padfilename2interval(f))
    
    return s

def OLDget_loose_pad_gaps(day, sensor='121f04', maxgapsec=2, basedir='/misc/yoda/pub/pad'):
    
    # get day interval and "day" PAD ymd path
    tomorrow = day + datetime.timedelta(days=1)
    t1 = datetime.datetime.combine(day, datetime.datetime.min.time())
    t2 = datetime.datetime.combine(tomorrow, datetime.datetime.min.time())
    ymdpath = datetime_to_ymd_path(day, base_dir=basedir)
    
    # initialize loose pad interval set
    s = LoosePadIntervalSet(maxgapsec=maxgapsec)
    
    # build interval set with pad filenames for "yesterday" and "day"
    yesterday = day - datetime.timedelta(days=1)
    file_list = get_pad_data_files(datetime_to_ymd_path(yesterday, base_dir=basedir), sensor) # "yesterday" files
    file_list.extend(get_pad_data_files(ymdpath, sensor)) # extend list with "day" files
    for f in file_list:
        s.add(padfilename2interval(f))  
    
    # build interval for day of interest (the whole day)
    day_interval = Interval(t1, t2)
    whole_day_intervalset = IntervalSet( (day_interval,) )
    
    # difference to get set of gaps for day of interest
    gaps = whole_day_intervalset - s
    
    return gaps   

def get_whole_day_intervalset(day):
    
    # get day interval and "day" PAD ymd path
    tomorrow = day + datetime.timedelta(days=1)
    t1 = datetime.datetime.combine(day, datetime.datetime.min.time())
    t2 = datetime.datetime.combine(tomorrow, datetime.datetime.min.time())

    # build interval for day of interest (the whole day)
    day_interval = Interval(t1, t2)
    whole_day_intervalset = IntervalSet( (day_interval,) )
    return whole_day_intervalset

def get_loose_pad_gaps(day, sensor='121f04', maxgapsec=2, basedir='/misc/yoda/pub/pad'):
    
    # get loose pad interval set
    s = get_loose_pad_intervalset(day, sensor=sensor, maxgapsec=maxgapsec, basedir=basedir)
    
    # get whole day interval set
    whole_day_intervalset =  get_whole_day_intervalset(day)
    
    # difference to get set of gaps for day of interest
    gaps = whole_day_intervalset - s
    
    return gaps   

def get_loose_pad_nongaps(day, sensor='121f04', maxgapsec=2, basedir='/misc/yoda/pub/pad'):
    
    # get loose pad interval set
    nongaps = get_loose_pad_intervalset(day, sensor=sensor, maxgapsec=maxgapsec, basedir=basedir)
    
    return nongaps   

def get_strata_gaps(days_ago=2, sensor='121f04', maxgapsec=59, basedir='/misc/yoda/pub/pad'):
    #print days_ago, sensor, maxgapsec, basedir
    day = datetime.date.today() - datetime.timedelta(days=days_ago)
    gaps = get_loose_pad_gaps(day, sensor=sensor, maxgapsec=maxgapsec, basedir=basedir)
    return gaps

    
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    