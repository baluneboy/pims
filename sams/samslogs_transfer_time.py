#! /usr/bin/env python

"""A command line utility for converting ATL readme.txt to MATLAB script."""

__author__ = "Ken Hrovat"
__date__   = "$12 January, 2016 08:38:00 AM$"

import os
import re
import sys
import datetime
from dateutil import parser, relativedelta
from pims.files.utils import filter_dirnames, grep_r

_TODAY = datetime.datetime.now()
_ONE_WEEK_AGO = _TODAY.date() - datetime.timedelta(days=7)


# return directory name for samslogs subdir matching input year and day of year
def get_samslogs_dir(year, doy):
    """return directory name for samslogs subdir matching input year and day of year"""
    dirname = None
    subdirPattern = '.*samslogs%d%03d' % (year, doy)
    dirpath = r'/misc/yoda/secure/%d_downlink' % year
    predicate = re.compile(os.path.join(dirpath, subdirPattern)).match
    # FIXME better handling of generator to get one and only one item (check/error on multiple items)
    for dirname in filter_dirnames(dirpath, predicate):
        return dirname # short-circuit the generator and return first item only!?


# return first match from routine that behaves like recursive grep
def grep_recursive(patstr, samslogs_dir):
    """return first match from routine that behaves like recursive grep"""
    matchstr = None
    for matchstr in grep_r(patstr, samslogs_dir):
        return matchstr.rstrip('\n')


# return seconds needed for last week's samslogs downlink
def get_downlink_duration(samslogs_date):
    """return seconds needed for last week's samslogs downlink"""
    fname, sec = None, None
    
    # get directory, which has year and doy from one week after samslogs_date
    nextweek_date = samslogs_date + relativedelta.relativedelta(days=7)
    nextweek_year = nextweek_date.timetuple().tm_year
    nextweek_doy = nextweek_date.timetuple().tm_yday
    my_dir = get_samslogs_dir(nextweek_year, nextweek_doy)
    
    if my_dir:
        # find string for beginning of transfer from one week ago
        samslogs_year = samslogs_date.timetuple().tm_year
        samslogs_doy = samslogs_date.timetuple().tm_yday
        patstr = '.*icu-f01 Telem.*Beginning transfer.*samslogs%d%03d.tgz.*' % (samslogs_year, samslogs_doy)
        beginstr = grep_recursive(patstr, my_dir)
        if beginstr:
            #print beginstr
            m1 = re.match('^(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d{2}:\d{2}:\d{2}).*(?P<fname>samslogs.*\.tgz).*', beginstr)
            if m1:
                fname = m1.group('fname')
                start_dtm = parser.parse( m1.group('date') + ' ' + m1.group('time') )
                # find string for transfer complete from one week ago    
                patstr = '.*icu-f01 Telem.*Downlink of file.*samslogs%d%03d.tgz.*complete.*' % (samslogs_year, samslogs_doy)
                endstr = grep_recursive(patstr, my_dir)
                m2 = re.match('^(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d{2}:\d{2}:\d{2}).*', endstr)
                if m2:
                    end_dtm = parser.parse( m2.group('date') + ' ' + m2.group('time') )
                    sec = int( (end_dtm - start_dtm).total_seconds() )
                    
    return fname, sec


# return seconds needed for last week's samslogs downlink
def get_last_week_downlink_duration():
    """return seconds needed for last week's samslogs downlink"""
    samslogs_date = _ONE_WEEK_AGO
    fname, sec = get_downlink_duration(samslogs_date)
    return fname, sec


if __name__ == "__main__":
    
    fname, sec = get_last_week_downlink_duration()
    print fname, sec

    samslogs_date = datetime.date(2015, 12, 21)
    fname, sec = get_downlink_duration(samslogs_date)
    print fname, sec
