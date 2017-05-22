#! /usr/bin/env python

import datetime
from pyinter import Interval, IntervalSet
from pims.utils.pimsdateutil import datetime_to_ymd_path, pad_fullfilestr_to_start_stop

class PadInterval(Interval):

    def __init__(self, lower, lower_value, upper_value, upper, maxgapsec=1.5):
        "Initializes the PadInterval"
        items = [lower_value, upper_value]
        if not all(isinstance(x, datetime.datetime) for x in items):
            raise TypeError('lower_value & upper_value must be datetime type')
        super(PadInterval, self).__init__(lower, lower_value, upper_value, upper)
        self.maxgapsec = maxgapsec

    def close_enough(self, other):
        """Tells whether 2 pad intervals are close enough to each other

        Returns True if self is close enough to (within maxgapsec seconds of) other
        meaning if they were joined, then there would be no discontinuity.

        >>> d1 = datetime.datetime(2015,1,1,0,0,0)
        >>> d2 = d1 + datetime.timedelta(seconds=12.345)
        >>> d3 = d2 + datetime.timedelta(seconds=1.6)           # 1.6 sec
        >>> d4 = d3 + datetime.timedelta(seconds=0.5)
        >>> d5 = d4 + datetime.timedelta(seconds=1.5)           # 1.5 sec
        >>> d6 = d5 + datetime.timedelta(seconds=86400.123456)  # over a day
        >>> d7 = d6 - datetime.timedelta(seconds=1.5)           # minus 1.5 sec
        >>> d8 = d7 + datetime.timedelta(seconds=123.5)         # 123.5 sec
        >>> r1 = PadInterval(PadInterval.CLOSED, d1, d2, PadInterval.OPEN)
        >>> r2 = PadInterval(PadInterval.CLOSED, d3, d4, PadInterval.OPEN)
        >>> r3 = PadInterval(PadInterval.CLOSED, d5, d6, PadInterval.OPEN)
        >>> r4 = PadInterval(PadInterval.CLOSED, d5, d6, PadInterval.OPEN)
        >>> r5 = PadInterval(PadInterval.CLOSED, d7, d8, PadInterval.OPEN)
        >>> r5.overlaps(r4) # True
        True
        >>> r1.close_enough(r2) # False
        False
        >>> r2.close_enough(r3) # True
        True
        >>> r1.close_enough(r3) # False
        False
        >>> r3.close_enough(r1) # False
        False
        >>> r3.close_enough(r2) # True
        True

        """
        if self.maxgapsec <= 0:
            return False
        if self.upper_value < other.lower_value:
            if (other.lower_value - self.upper_value).total_seconds() <= self.maxgapsec:
                result = True
            else:
                result = False
        elif self == other:
            result = True
        else:
            result = other.close_enough(self)
        return result

    def middle(self):
        return self.lower_value + (self.upper_value - self.lower_value) / 2

class PadIntervalSet(IntervalSet):

    def __init__(self, items=[], maxgapsec=1.5):
        "Initializes the PadIntervalSet"
        if items:
            if not all(isinstance(x, datetime.datetime) for x in items):
                raise TypeError('items must all be datetime type')
        super(PadIntervalSet, self).__init__(items)
        self.maxgapsec = maxgapsec
        
    def _get_fill(self, i1, i2):
        """Returns an interval from earlier interval's upper_value (closed) to later interval's lower_value (open)

        >>> d1 = datetime.datetime(2015,1,1,0,0,0)
        >>> d2 = d1 + datetime.timedelta(seconds=12.345)
        >>> d3 = d2 + datetime.timedelta(seconds=1.6)
        >>> d4 = d3 + datetime.timedelta(seconds=0.5)
        >>> d5 = d4 + datetime.timedelta(seconds=60.0)
        >>> d6 = d5 + datetime.timedelta(seconds=86400.123456)
        >>> r1 = PadInterval(PadInterval.CLOSED, d1, d2, PadInterval.OPEN)
        >>> r2 = PadInterval(PadInterval.CLOSED, d3, d4, PadInterval.OPEN)
        >>> r3 = PadInterval(PadInterval.CLOSED, d5, d6, PadInterval.OPEN)     
        >>> s = PadIntervalSet()
        >>> print s._get_fill(r1, r2)
        [2015-01-01 00:00:12.345000, 2015-01-01 00:00:13.945000)
        >>> print s._get_fill(r2, r3)
        [2015-01-01 00:00:14.445000, 2015-01-01 00:01:14.445000)
        >>> print s._get_fill(r3, r2)
        [2015-01-01 00:00:14.445000, 2015-01-01 00:01:14.445000)
        
        """
        
        if i1.upper_value < i2.lower_value:
            result = PadInterval(PadInterval.CLOSED, i1.upper_value, i2.lower_value, PadInterval.OPEN)
        else:
            result = PadInterval(PadInterval.CLOSED, i2.upper_value, i1.lower_value, PadInterval.OPEN)
        return result        

    def add(self, other):
        """
        Add a PadInterval to the PadIntervalSet by taking the union of the given PadInterval object with the existing
        PadInterval object(s) in self.

        This has no effect if the PadInterval is already represented [already in the set].
        :param other: an PadInterval to add to this IntervalSet.

        >>> d0 = datetime.datetime(2014,12,31,23,59,58)
        >>> d1 = datetime.datetime(2015,1,1,0,0,0)
        >>> d2 = d1 + datetime.timedelta(seconds=12.345)
        >>> d3 = d2 + datetime.timedelta(seconds=1.6)
        >>> d4 = d3 + datetime.timedelta(seconds=0.5)
        >>> d5 = d4 + datetime.timedelta(seconds=60.0)
        >>> d6 = d5 + datetime.timedelta(seconds=86400.123456)
        >>> r1 = PadInterval(PadInterval.CLOSED, d1, d2, PadInterval.OPEN)
        >>> mid_r1 = r1.middle()
        >>> r2 = PadInterval(PadInterval.CLOSED, mid_r1, d4, PadInterval.OPEN)
        >>> r3 = PadInterval(PadInterval.CLOSED, d5, d6, PadInterval.OPEN)
        >>> r = PadIntervalSet()
        >>> r.add(r1)
        >>> print r
        PadIntervalSet([2015-01-01 00:00:00, 2015-01-01 00:00:12.345000),)
        >>> r.add(r2)
        >>> print r
        PadIntervalSet([2015-01-01 00:00:00, 2015-01-01 00:00:14.445000),)
        >>> r.add(r3)
        >>> print r
        PadIntervalSet([2015-01-01 00:00:00, 2015-01-01 00:00:12.345000), [2015-01-01 00:00:13.945000, 2015-01-01 00:00:14.445000), [2015-01-01 00:01:14.445000, 2015-01-02 00:01:14.568456))
    
        """

        if not isinstance(other, PadInterval):
            raise Exception("cannot add object that is not PadInterval instance")
        
        to_add = set()
        for inter in self:
            if inter.overlaps(other):  # if it overlaps with this interval then the union will be a single interval
                to_add.add(inter.union(other))
            elif inter.close_enough(other): # also allow for this interval to be close enough to other so unions ok
                inter_mid = inter.middle()
                other_mid = other.middle()
                if inter_mid < other_mid:
                    other.lower_value = inter_mid
                else:
                    other.upper_value = inter_mid
                to_add.add(inter.union(other))
        if len(to_add) == 0:  # other must not overlap with any interval in self (self could be empty!)
            to_add.add(other)
        # Now add the intervals found to self
        if len(to_add) > 1:
            set_to_add = IntervalSet(to_add)  # creating an interval set unions any overlapping intervals
            for el in set_to_add:
                self._add(el)
        elif len(to_add) == 1:
            self._add(to_add.pop())

def demo_add():
    d0 = datetime.datetime(2014,12,31,23,59,58)
    d1 = datetime.datetime(2015,1,1,0,0,0)
    d2 = d1 + datetime.timedelta(seconds=12.345)
    d3 = d2 + datetime.timedelta(seconds=1.6)
    d4 = d3 + datetime.timedelta(seconds=0.5)
    d5 = d4 + datetime.timedelta(seconds=60.0)
    d6 = d5 + datetime.timedelta(seconds=86400.123456)
    #print d0
    #print d1
    #print d2
    #print d3
    #print d4
    #print d5
    #print d6
    r1 = PadInterval(PadInterval.CLOSED, d1, d2, PadInterval.OPEN)
    mid_r1 = r1.middle()
    r2 = PadInterval(PadInterval.CLOSED, mid_r1, d4, PadInterval.OPEN)
    r3 = PadInterval(PadInterval.CLOSED, d5, d6, PadInterval.OPEN)
    r = PadIntervalSet()
    print r
    r.add(r1)
    print r
    r.add(r2)
    print r
    r.add(r3)
    print r
    #r.add(r3)
    #print r
    
demo_add()
raise SystemExit

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
    r = PadIntervalSet(maxgapsec=1) # try 1 to see "not close enough" or 2 for "close enough"
    r.add(padfilename2interval(f1))
    r.add(padfilename2interval(f2))
    
    day_interval = PadInterval(datetime.datetime(2015, 3, 14, 0, 0, 0), datetime.datetime(2015, 3, 15, 0, 0, 0))
    whole_day_intervalset = IntervalSet( (day_interval,) )
    
    # now set of gaps are thes
    for gap in (whole_day_intervalset - r):
        print gap


def padfilename2interval(fname):
    t1, t2 = pad_fullfilestr_to_start_stop(fname)
    return PadInterval(PadInterval.CLOSED, t1, t2, PadInterval.OPEN)

def get_loose_pad_intervalset(day, sensor='121f04', maxgapsec=2, basedir='/misc/yoda/pub/pad'):
    
    # get day interval and "day" PAD ymd path
    tomorrow = day + datetime.timedelta(days=1)
    t1 = datetime.datetime.combine(day, datetime.datetime.min.time())
    t2 = datetime.datetime.combine(tomorrow, datetime.datetime.min.time())
    ymdpath = datetime_to_ymd_path(day, base_dir=basedir)
    
    # initialize loose pad interval set
    s = PadIntervalSet(maxgapsec=maxgapsec)
    
    # build interval set with pad filenames for "yesterday" and "day"
    yesterday = day - datetime.timedelta(days=1)
    file_list = get_pad_data_files(datetime_to_ymd_path(yesterday, base_dir=basedir), sensor) # "yesterday" files
    file_list.extend(get_pad_data_files(ymdpath, sensor)) # extend list with "day" files
    for f in file_list:
        s.add(padfilename2interval(f))
    
    return s

def get_whole_day_intervalset(day):
    
    # get day interval and "day" PAD ymd path
    tomorrow = day + datetime.timedelta(days=1)
    t1 = datetime.datetime.combine(day, datetime.datetime.min.time())
    t2 = datetime.datetime.combine(tomorrow, datetime.datetime.min.time())

    # build interval for day of interest (the whole day)
    day_interval = PadInterval(t1, t2)
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
    
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    