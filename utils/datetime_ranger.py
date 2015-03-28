#!/usr/bin/env python

import os
import re
import datetime
from pims.utils.pimsdateutil import days_ago_to_date, days_ago_to_date_time
from dateutil import parser

class BaseRange(object):
    """ A class to handle date/time range(s). """
    def __init__(self, start=None, stop=None):
        self._get_config()
        self.start, self.stop = self._parse_inputs(start, stop)
        self._verify_order()
    
    def _get_config(self):
        " get _days_ago_func and _objType "
        raise NotImplementedError('this is responsibility of subclass')
    
    def __str__(self):
        s = '%s from %s to %s' % (self.__class__.__name__, self.start, self.stop)
        return s
    
    def _convert_pad_filename_to_start_stop(self, fname):
        " subclass has to convert PAD filename and return proper start and stop as tuple "
        raise NotImplementedError('this is responsibility of subclass')
        
    def _parse_inputs(self, start, stop):
        days_ago_conv_func = self._days_ago_func
        if start == None and stop == None:
            return days_ago_conv_func(2), days_ago_conv_func(2)
        elif isinstance(start, int) and stop == None:
            return days_ago_conv_func(start), days_ago_conv_func(start)
        elif isinstance(start, int) and isinstance(stop, int):
            return days_ago_conv_func(start), days_ago_conv_func(stop)
        elif isinstance(start, self._objType) and stop == None:
            return start, start  
        elif isinstance(start, self._objType) and isinstance(stop, self._objType):
            return start, stop
        elif isinstance(start, basestring) and stop == None:
            return self._convert_pad_filename_to_start_stop(start)
        elif isinstance(start, basestring) and isinstance(stop, basestring):
            try:
                start = parser.parse(start)
                stop = parser.parse(stop)
                return start, stop
            except:
                raise TypeError('start & stop both strings, but could not parse')
        else:
            raise TypeError('input start/stop signature is unexpected')

    def _verify_order(self):
        " verify we have start before stop "
        if self.start > self.stop:
            raise ValueError('start is after stop')

class TimeRange(BaseRange):
    """ A class to handle datetime range(s).
    
        >>> import datetime
        >>> dtm1 = datetime.datetime(2012, 12, 31, 1, 1, 1)
        >>> dtm2 = datetime.datetime(2013, 01, 02, 2, 2, 2)
        >>> dtm3 = datetime.datetime(2013, 01, 03, 3, 3, 3)
        >>> dtm7 = datetime.datetime(2013, 01, 07, 7, 7, 7)
        >>> print TimeRange(dtm1)
        TimeRange from 2012-12-31 01:01:01 to 2012-12-31 01:01:01
        >>> print TimeRange(dtm1, dtm2)
        TimeRange from 2012-12-31 01:01:01 to 2013-01-02 02:02:02
        >>> tr = TimeRange(7, 1)
        >>> daypartStart = (datetime.date.today() - datetime.timedelta(days=7))
        >>> daypartStop  = (datetime.date.today() - datetime.timedelta(days=1))
        >>> tr.start == datetime.datetime.combine(daypartStart,datetime.time(0,0,0))
        True
        >>> tr.stop  == datetime.datetime.combine(daypartStop, datetime.time(0,0,0))
        True
        
        >>> print TimeRange('/misc/yoda/pub/pad/year2013/month09/day22/sams2_accel_121f03/2012_12_31_23_59_59.999+2013_01_01_00_00_56.851.121f03')
        TimeRange from 2012-12-31 23:59:59.999000 to 2013-01-01 00:00:56.851000
        
        >>> print TimeRange('/misc/yoda/pub/pad/year2013/month09/day22/sams2_accel_121f03/2012_12_31_23_59_59.999+2013_01_01_02_03_45.678.121f03.header')
        TimeRange from 2012-12-31 23:59:59.999000 to 2013-01-01 02:03:45.678000
        
    """
    
    def _get_config(self):
        " get _days_ago_func and _objType "
        self._days_ago_func = days_ago_to_date_time
        self._objType = datetime.datetime

    def _convert_pad_filename_to_start_stop(self, filename):
        " convert PAD filename to start datetime obj and stop datetime obj as tuple "
        pname, fname = os.path.split(filename)
        fname = fname.split('.header')[0] # throw away '.header' suffix
        m = re.search('.*/(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})[\+-](\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3}).*', filename)
        # FIXME error handling goes here
        startstr, stopstr = m.group(1), m.group(2)
        start = datetime.datetime.strptime(startstr, '%Y_%m_%d_%H_%M_%S.%f')
        stop = datetime.datetime.strptime(stopstr, '%Y_%m_%d_%H_%M_%S.%f')        
        return start, stop

class DateRange(BaseRange):
    """ A class to handle date range(s).
    
        >>> import datetime
        >>> d1 = datetime.date(2012, 12, 31)
        >>> d2 = datetime.date(2013, 01, 02)
        >>> d3 = datetime.date(2013, 01, 03)
        >>> d7 = datetime.date(2013, 01, 07)
        >>> print DateRange(d1)
        DateRange from 2012-12-31 to 2012-12-31
        >>> print DateRange(d1, d2)
        DateRange from 2012-12-31 to 2013-01-02
        >>> dr = DateRange(7, 1)
        >>> dr.start == (datetime.date.today() - datetime.timedelta(days=7))
        True
        >>> dr.stop == (datetime.date.today() - datetime.timedelta(days=1))
        True
        
    """
    
    def __str__(self):
        s = '%s from %s to %s' % (self.__class__.__name__, self.start, self.stop)
        return s    
    
    def _get_config(self):
        " get _days_ago_func and _objType "
        self._days_ago_func = days_ago_to_date
        self._objType = datetime.date

def testdoc(verbose=True):
    import doctest
    return doctest.testmod(verbose=verbose)

if __name__ == "__main__":
    testdoc(verbose=True)
