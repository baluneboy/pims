#! /usr/bin/env python

import datetime
from interval import Interval, IntervalSet

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
    suffix = sensor + '.header'
    header_files = [ x for x in filter_filenames(dirpath, re.compile(fullfile_pattern).match) if x.endswith(suffix)]
    
#dirpath = '/misc/yoda/pub/pad/year2015/month03/day17'
#sensor = '121f03'
#big_list = demo_big_list(dirpath, sensor)
#for f in big_list[0:9]: #filter_filenames(dirpath, re.compile(fullfile_pattern).match):
#    print f
#raise SystemExit

def demo():
    from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop
    f1 = '/misc/yoda/pub/pad/2015_03_14_00_05_47.252+2015_03_14_00_15_47.267.121f05.header'
    f2 = '/misc/yoda/pub/pad/2015_03_14_00_15_48.867+2015_03_14_00_25_00.000.121f05.header'
    t1, t2 = pad_fullfilestr_to_start_stop(f1)
    t3, t4 = pad_fullfilestr_to_start_stop(f2)
    r = LoosePadIntervalSet(maxgapsec=1) # try 1 to see "not close enough" or 2 for "close enough"
    r.add(Interval(t1,t2))
    #print r
    r.add(Interval(t3,t4))
    #print r
    ss = Interval(datetime.datetime(2015, 3, 14, 0, 0, 0), datetime.datetime(2015, 3, 15, 0, 0, 0))
    iss = IntervalSet( (ss,) )
    # now set of gaps are these
    print iss - r
    
#demo()
#raise SystemExit
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
