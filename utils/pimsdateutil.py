#!/usr/bin/env python
"""
Date/time functions mostly for PIMS/PAD utility.
"""

import os
import re
import datetime
import time
from dateutil import parser
from warnings import warn


MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)

(JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE,
 JULY, AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER) = range(1, 13)

_DAY = datetime.timedelta(1)
        
def timedelta_hours(td):
    """Return timedelta in hours.
    
    >>> d1 = datetime.datetime(1991,9,12,12,0,0,0)
    >>> d2 = datetime.datetime(2014,9,12,12,0,0,0)
    >>> timedelta_hours( d2 - d1  )
    201624.0
    """
    return td.days * 24 + td.seconds/3600.0

def days_hours_minutes(td):
    """Return timedelta in days, hours, minutes.
    
    >>> d1 = datetime.datetime(1991,9,12,12,0,0,0)
    >>> d2 = datetime.datetime(2014,9,12,12,0,0,0)
    >>> days_hours_minutes( d2 - d1  )
    (8401, 0, 0)
    """
    return td.days, td.seconds//3600, (td.seconds//60)%60

def ceil_minute(t):
    """Return datetime rounded down (floored) to nearest 1-minute mark.
    
    >>> ceil_minute( datetime.datetime(2012,12,31,23,39,00,000001) )
    datetime.datetime(2012, 12, 31, 23, 40)
    """
    return floor_minute(t) + datetime.timedelta(minutes=1)

def floor_minute(t):
    """Return datetime rounded down (floored) to nearest 1-minute mark.
    
    >>> floor_minute( datetime.datetime(2012,12,31,23,39,00,000001) )
    datetime.datetime(2012, 12, 31, 23, 39)
    """
    return t - datetime.timedelta( minutes=t.minute % 1,
                                    seconds=t.second,
                                    microseconds=t.microsecond)

def floor_ten_minutes(t):
    """Return datetime rounded down (floored) to nearest 10-minute mark.
    
    >>> floor_ten_minutes( datetime.datetime(2012,12,31,23,39,59,999000) )
    datetime.datetime(2012, 12, 31, 23, 30)
    """
    return t - datetime.timedelta( minutes=t.minute % 10,
                                    seconds=t.second,
                                    microseconds=t.microsecond)

def floor_hour(t):
    """Return datetime rounded down (floored) to nearest hour mark.
    
    >>> floor_hour( datetime.datetime(2012,12,31,23,39,59,999000) )
    datetime.datetime(2012, 12, 31, 23, 0)
    >>> floor_hour( datetime.datetime(2012,12,31,23,00,00,000001) )
    datetime.datetime(2012, 12, 31, 23, 0)
    >>> floor_hour( datetime.datetime(2012,12,31,23,00,00,000000) )
    datetime.datetime(2012, 12, 31, 23, 0)
    """
    return t - datetime.timedelta( minutes=t.minute,
                                    seconds=t.second,
                                    microseconds=t.microsecond)

def datetime_to_ymd_path(d, base_dir='/misc/yoda/pub/pad'):
    """
    Return PAD path for datetime, d, like /misc/yoda/pub/pad/yearYYYY/monthMM/dayDD
    
    Examples
    --------
    
    >>> datetime_to_ymd_path(datetime.date(2002, 12, 28))
    '/misc/yoda/pub/pad/year2002/month12/day28'
    
    >>> datetime_to_ymd_path(datetime.datetime(2009, 12, 31, 23, 59, 59, 999000))
    '/misc/yoda/pub/pad/year2009/month12/day31'
    
    """
    return os.path.join( base_dir, d.strftime('year%Y/month%m/day%d') )


def datetime_to_roadmap_ymd_path(d):
    """
    Return roadmap PDF path for datetime, d, like /misc/yoda/www/plots/batch/year2016/month04/day29
    
    Examples
    --------
    
    >>> datetime_to_roadmap_ymd_path(datetime.date(2002, 12, 28))
    '/misc/yoda/www/plots/batch/year2002/month12/day28'
    
    >>> datetime_to_roadmap_ymd_path(datetime.datetime(2009, 12, 31, 23, 59, 59, 999000))
    '/misc/yoda/www/plots/batch/year2009/month12/day31'
    
    """
    return datetime_to_ymd_path(d, base_dir='/misc/yoda/www/plots/batch')


def datetime_to_roadmap_fullstub(dtm):
    """
    Return roadmap PDF path for datetime, dtm, like /misc/yoda/www/plots/batch/year2016/month04/day29/2016_04_29_00_00_00.000
    
    Examples
    --------
    
    >>> datetime_to_roadmap_fullstub(datetime.date(2002, 12, 28,  0, 0, 0))
    '/misc/yoda/www/plots/batch/year2002/month12/day28'
    
    >>> datetime_to_roadmap_fullstub(datetime.date(2002, 12, 28, 16, 0, 0))
    '/misc/yoda/www/plots/batch/year2009/month12/day31'
    
    """
    pth = datetime_to_roadmap_ymd_path(dtm)
    prefix = format_datetime_as_pad_underscores(dtm)
    return os.path.join(pth, prefix)
    

# return string for "yesterday's" year/month/day PAD path
def yesterday_pad_ymd_path(base_dir='/misc/yoda/pub/pad'):
    """return string for "yesterday's" year/month/day PAD path"""
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    return datetime_to_ymd_path(yesterday, base_dir=base_dir)


def timestr_to_datetime(timestr):
    """
    Return datetime representation of a time string.
    
    Examples
    --------
    
    >>> timestr_to_datetime('2013_01_02_00_01_02.210')
    datetime.datetime(2013, 1, 2, 0, 1, 2, 210000)

    >>> timestr_to_datetime('2014_06_12_08')
    datetime.datetime(2014, 6, 12, 8, 0)
    
    """
    if len(timestr) == 13:
        timestr += '_00_00.000'
    try:
        d = datetime.datetime.strptime(timestr,'%Y_%m_%d_%H_%M_%S.%f')
    except ValueError, e:
        raise ValueError('%s is a bad timestr' % timestr)
    return d

def samsops_timestamp_to_datetime(timestr):
    """
    Return datetime representation of a timestamp string from samsops schemas.
    
    Examples
    --------
    
    >>> samsops_timestamp_to_datetime('2015-06-02 11:50:35')
    datetime.datetime(2015, 6, 2, 11, 50, 35)
    
    """
    try:
        d = datetime.datetime.strptime(timestr,'%Y-%m-%d %H:%M:%S')
    except ValueError, e:
        raise ValueError('%s is a bad timestr' % timestr)
    return d

# convert string like 2014:077:00:02:00 to datetime object
def doytimestr_to_datetime(timestr):
    """convert string like 2014:077:00:02:00 to datetime object
    
    >>> doytimestr_to_datetime('2014:077:00:02:00')
    datetime.datetime(2014, 3, 18, 0, 2)
    """
    if not timestr: return None
    if not re.match('^\d{4}:\d{3}:\d{2}:\d{2}:(\d{2}\.\d{1,6}|\d{2})$', timestr):
        raise ValueError('string does not match expected pattern')
    if '.' in timestr:
        fmt = '%Y:%j:%H:%M:%S.%f'
    else:
        fmt = '%Y:%j:%H:%M:%S'
    return datetime.datetime.strptime(timestr, fmt)

# convert datetime object to string like 2014:077:00:02:00
def datetime_to_doytimestr(dtm):
    """convert datetime object to string like 2014:077:00:02:00
    
    >>> datetime_to_doytimestr(datetime.datetime(2014, 6, 12, 8, 11, 10, 123456))
    '2014:163:08:11:10.123456'
    """
    if not dtm: return None
    return dtm.strftime('%Y:%j:%H:%M:%S.%f')

# convert datetime object to string like 2016-11-27,332/00:02:00.000
def datetime_to_longtimestr(dtm):
    """convert datetime object to string like 2016-11-27,332/01:02:03.456
    
    >>> datetime_to_longtimestr(datetime.datetime(2016, 11, 27, 1, 2, 3, 456543))
    '2016-11-27,332/01:02:03.457'
    """
    if not dtm: return None
    s = dtm.strftime('%Y-%m-%d,%j/%H:%M:%S.%f')
    f = round(float(s[-7:]), 3)
    temp = "%.3f" % f
    return "%s%s"% (s[:-7], temp[1:])

# convert string like 2014-05-02 to datetime object
def datestr_to_datetime(timestr):
    """convert string like 2014-05-02 to datetime object"""
    if not re.match('^\d{4}\-\d{2}\-\d{2}$', timestr):
        raise ValueError('string does not match expected pattern')
    fmt = '%Y-%m-%d'
    return datetime.datetime.strptime(timestr, fmt)


# convert northfield html filename to date (from like 072616.htm)
def northfield_fullfilestr_to_date(fullfilestr):
    """convert northfield html filename to date object   
    >>> fstr = '/tmp/raw/072616.htm'
    >>> northfield_fullfilestr_to_date(fstr)
    datetime.date(2016, 7, 26)
    """    
    # get rid of header ext if there is one, and just work with basename
    fstr = os.path.basename(fullfilestr.replace('.htm', ''))
    if not re.match('^\d{6}$', fstr):
        raise ValueError('basename str %s does not match expected pattern' % fstr)
    try:
        yr = int('20' + fstr[-2:])
        mo = int(fstr[0:2])
        da = int(fstr[2:4])
        d = datetime.date(yr, mo, da)
    except ValueError, e:
        warn( 'fstr %s did not nicely convert to date' % fstr )
        d = None
    return d


# convert string like YODA_YMD_PATH/.../2014_05_31_20_49_60.000-2014_05_31_21_00_00.001.SENSOR to datetime object
def pad_fullfilestr_to_start_stop(fullfilestr):
    """convert pad fullfile string to datetime object"""
    # get rid of header ext if there is one, and just work with basename
    fstr = os.path.basename(fullfilestr.replace('.header', ''))
    if not re.match('^\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3}.\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3}\..*$', fstr):
        raise ValueError('basename str %s does not match expected pattern' % fstr)
    [startstr, bigstr] = fstr.split(fstr[23])
    stopstr = '.'.join(bigstr.split('.')[:-1])
    try:
        d1 = timestr_to_datetime(startstr)
    except ValueError, e:
        warn( 'startstr %s did not nicely convert to datetime in timestr_to_datetime' % startstr )
        d1 = None
    try:
        d2 = timestr_to_datetime(stopstr)
    except ValueError, e:
        warn( 'stopstr %s did not nicely convert to datetime in timestr_to_datetime' % stopstr )
        d2 = None
    return d1, d2

def foscam_fullfilestr_to_datetime(fullfilestr):
    """convert foscam timestamped jpg fullfile string to datetime object"""
    bname_pattern = r'^(?P<day>\d{4}-\d{2}-\d{2})_(?P<hour>\d{2})_(?P<minute>\d{2})_(open|close)\.jpg$'
    bname = os.path.basename(fullfilestr)
    if not re.match(bname_pattern, bname):
        return None
    p = re.compile(bname_pattern)
    m = p.search(bname)
    daystr = m.group('day')
    hh = m.group('hour')
    mm = m.group('minute')
    try:
        d1 = parser.parse(daystr + ' ' + hh + ':' + mm)
    except ValueError, e:
        d1 = None
    return d1

# convert start string like 2015_01_02_03_04_05.678_blah to datetime object for start GMT
def handbook_pdf_startstr_to_datetime(startstr):
    """convert start string to datetime object for start GMT"""
    # get rid of header ext if there is one, and just work with basename
    ymdhms = [1970, 1, 1, 0, 0, 0, 0]
    pattern = '(?:\d*\.)?\d+_'
    i = 0
    for x in re.findall(pattern, startstr):
        if i > 4 and ('.' in x):
            xx = x.rstrip('_').split('.')
            v1 = int(xx[0])
            v2 = int(xx[1]) * 1000
            ymdhms[i] = v1
            ymdhms[i+1] = v2
            i += 2
        else:
            v = int(x.rstrip('_'))
            ymdhms[i] = v
            i += 1
    args = tuple(ymdhms)
    return datetime.datetime( *args )

def format_datetime_as_pad_underscores(dtm):
    """
    Format datetime as underscore-delimited PAD string.
    
    >>> format_datetime_as_pad_underscores( datetime.datetime(2013,10,25,1,2,3,456789) ) # NO ROUNDING!
    '2013_10_25_01_02_03.456'
    
    """
    return dtm.strftime('%Y_%m_%d_%H_%M_%S.%f')[:-3] # remove 3 trailing zeros

# convert datetime start/stop to PAD header fullfile string
def start_stop_to_pad_fullfilestr(start, stop, pad_path='/misc/yoda/pub/pad', subdir_prefix='sams2_accel_', sensor='121f0x', joiner='-'):
    """Convert datetime start/stop to PAD header fullfile string
    
    >>> start = datetime.datetime(2013,10,25,1,2,3,456789)
    >>> stop = datetime.datetime(2013,10,25,1,2,13,123456)
    >>> start_stop_to_pad_fullfilestr(start, stop)
    '/misc/yoda/pub/pad/year2013/month10/day25/sams2_accel_121f0x/2013_10_25_01_02_03.456-2013_10_25_01_02_13.123.121f0x.header'

    >>> start_stop_to_pad_fullfilestr(start, stop, pad_path='/tmp', subdir_prefix='hey_now_', sensor='abcd', joiner='#')
    '/tmp/year2013/month10/day25/hey_now_abcd/2013_10_25_01_02_03.456#2013_10_25_01_02_13.123.abcd.header'
    
    """    
    s1 = format_datetime_as_pad_underscores(start)
    s2 = format_datetime_as_pad_underscores(stop)
    fname = s1 + joiner + s2 + '.' + sensor
    ymd_path = datetime_to_ymd_path(start, base_dir=pad_path)
    return os.path.join(ymd_path, subdir_prefix + sensor, fname + '.header')

def days_ago_string(n):
    """Return n days ago as YYYY_mm_dd string."""
    n_days_ago = datetime.date.today()-datetime.timedelta(n)
    return n_days_ago.strftime('%Y_%m_%d')    

_2DAYSAGO = days_ago_string(2).replace('_', '-')
_5DAYSAGO = days_ago_string(5).replace('_', '-')

def days_ago_path_path(base_dir,n):
    """Return PAD path for n days ago like PADPATH/yearYYYY/monthMM/dayDD"""
    date_n_days_ago = datetime.date.today()-datetime.timedelta(n)
    return os.path.join( base_dir, date_n_days_ago.strftime('year%Y/month%m/day%d') )

def days_ago_to_date(n): 
    """Convert daysAgo integer to date object."""
    return datetime.date.today()-datetime.timedelta(n)
    
def days_ago_to_datetime(n):
    """Convert daysAgo integer to date object."""
    d = days_ago_to_date(n)
    return datetime.datetime.combine(d, datetime.time(0))

# Return seconds since midnight.
def sec_since_midnight(hms=None):
    """Return seconds since midnight.
    
    >>> print sec_since_midnight(hms='23:59:59')
    86399
    
    """
    utcnow = datetime.datetime.utcnow()
    midnight_utc = datetime.datetime.combine(utcnow.date(), datetime.time(0))
    if hms:
        if isinstance(hms, str):
            hms = tuple( [ int(i) for i in hms.split(':') ] )
        if not isinstance(hms, tuple):
            raise Exception('this function needs either HH:MM:SS string or (H,M,S) tuple input')
        utc = datetime.datetime.combine(utcnow.date(), datetime.time(hms[0], hms[1], hms[2]))
    else:
        utc = utcnow
    delta = utc - midnight_utc
    return int( delta.total_seconds() )

def is_leap_year(dt):
    """True if date in a leap year, False if not.

    >>> for year in 1900, 2000, 2100, 2001, 2002, 2003, 2004:
    ...     print year, is_leap_year(datetime.date(year, 1, 1))
    1900 False
    2000 True
    2100 False
    2001 False
    2002 False
    2003 False
    2004 True
    """
    return (datetime.date(dt.year, 2, 28) + _DAY).month == 2

def days_in_month(dt):
    """Total number of days in date's month.

    >>> for y in 2000, 2001:
    ...     print y,
    ...     for m in range(1, 13):
    ...         print "%d:%d" % (m, days_in_month(datetime.date(y, m, 1))),
    ...     print
    2000 1:31 2:29 3:31 4:30 5:31 6:30 7:31 8:31 9:30 10:31 11:30 12:31
    2001 1:31 2:28 3:31 4:30 5:31 6:30 7:31 8:31 9:30 10:31 11:30 12:31
    """
    if dt.month == 12:
        return 31
    else:
        next = datetime.date(dt.year, dt.month+1, 1)
        return next.toordinal() - dt.replace(day=1).toordinal()
    
def hours_in_month(dt):
    """Total number of hours in date's month.

    >>> for y in 1999, 2000, 2001:
    ...     print y,
    ...     for m in range(1, 13):
    ...         dt = datetime.date(y, m, 1)
    ...         print "%d:%d:%d" % (m, days_in_month(dt), hours_in_month(dt)),    
    ...     print
    1999 1:31:744 2:28:672 3:31:744 4:30:720 5:31:744 6:30:720 7:31:744 8:31:744 9:30:720 10:31:744 11:30:720 12:31:744
    2000 1:31:744 2:29:696 3:31:744 4:30:720 5:31:744 6:30:720 7:31:744 8:31:744 9:30:720 10:31:744 11:30:720 12:31:744
    2001 1:31:744 2:28:672 3:31:744 4:30:720 5:31:744 6:30:720 7:31:744 8:31:744 9:30:720 10:31:744 11:30:720 12:31:744
    """
    days = days_in_month(dt)
    return days * 24
   
def first_day_of_previous_month(d):
    """First day of previous month, where current month is given by input date, d.

    >>> d = datetime.date(2016, 4, 6)
    >>> first_day_of_previous_month(d)
    datetime.date(2016, 3, 1)
    """
    d = datetime.date(d.year, d.month, 1)
    d -= datetime.timedelta(days=1)
    return datetime.date(d.year, d.month, 1)

def first_weekday_on_or_after(weekday, dt):
    """First day of kind MONDAY .. SUNDAY on or after date.

    The time and tzinfo members (if any) aren't changed.

    >>> base = datetime.date(2002, 12, 28)  # a Saturday
    >>> base.ctime()
    'Sat Dec 28 00:00:00 2002'
    >>> first_weekday_on_or_after(SATURDAY, base).ctime()
    'Sat Dec 28 00:00:00 2002'
    >>> first_weekday_on_or_after(SUNDAY, base).ctime()
    'Sun Dec 29 00:00:00 2002'
    >>> first_weekday_on_or_after(TUESDAY, base).ctime()
    'Tue Dec 31 00:00:00 2002'
    >>> first_weekday_on_or_after(FRIDAY, base).ctime()
    'Fri Jan  3 00:00:00 2003'
    """
    days_to_go = (weekday - dt.weekday()) % 7
    if days_to_go:
        dt += datetime.timedelta(days_to_go)
    return dt

def first_weekday_on_or_before(weekday, dt):
    """First day of kind MONDAY .. SUNDAY on or before date.

    The time and tzinfo members (if any) aren't changed.

    >>> base = datetime.date(2003, 1, 3)  # a Friday
    >>> base.ctime()
    'Fri Jan  3 00:00:00 2003'
    >>> first_weekday_on_or_before(FRIDAY, base).ctime()
    'Fri Jan  3 00:00:00 2003'
    >>> first_weekday_on_or_before(TUESDAY, base).ctime()
    'Tue Dec 31 00:00:00 2002'
    >>> first_weekday_on_or_before(SUNDAY, base).ctime()
    'Sun Dec 29 00:00:00 2002'
    >>> first_weekday_on_or_before(SATURDAY, base).ctime()
    'Sat Dec 28 00:00:00 2002'
    """

    days_to_go = (dt.weekday() - weekday) % 7
    if days_to_go:
        dt -= datetime.timedelta(days_to_go)
    return dt

def weekday_of_month(weekday, dt, index):
    """Return the index'th day of kind weekday in date's month.

    All the days of kind weekday (MONDAY .. SUNDAY) are viewed as if a
    Python list, where index 0 is the first day of that kind in dt's month,
    and index -1 is the last day of that kind in dt's month.  Everything
    follows from that.  The time and tzinfo members (if any) aren't changed.

    Example:  Sundays in November.  The day part of the date is irrelevant.
    Note that a "too large" index simply spills over to the next month.

    >>> base = datetime.datetime(2002, 11, 25, 13, 22, 44)
    >>> for index in range(5):
    ...     print index, weekday_of_month(SUNDAY, base, index).ctime()
    0 Sun Nov  3 13:22:44 2002
    1 Sun Nov 10 13:22:44 2002
    2 Sun Nov 17 13:22:44 2002
    3 Sun Nov 24 13:22:44 2002
    4 Sun Dec  1 13:22:44 2002

    Start from the end of the month instead:
    >>> for index in range(-1, -6, -1):
    ...     print index, weekday_of_month(SUNDAY, base, index).ctime()
    -1 Sun Nov 24 13:22:44 2002
    -2 Sun Nov 17 13:22:44 2002
    -3 Sun Nov 10 13:22:44 2002
    -4 Sun Nov  3 13:22:44 2002
    -5 Sun Oct 27 13:22:44 2002
    """
    if index >= 0:
        base = first_weekday_on_or_after(weekday, dt.replace(day=1))
        return base + datetime.timedelta(weeks=index)
    else:
        base = first_weekday_on_or_before(weekday,
                                          dt.replace(day=days_in_month(dt)))
        return base + datetime.timedelta(weeks=1+index)

def days_ago_to_date(n): 
    """Convert days_ago integer, n, to date object."""
    return datetime.date.today()-datetime.timedelta(n)
    
def days_ago_to_date_time(n):
    """Convert days_ago integer, n, to date object."""
    d = days_ago_to_date(n)
    return datetime.datetime.combine(d, datetime.time(0))

def datetime_to_days_ago(d):
    """Convert datetime object to number of days ago."""
    today = datetime.datetime.now().date()
    days_ago = (today - d.date()).days
    if days_ago < 0:
        raise Exception('you want DAYSAGO, BUT input argument is in the future')
    return days_ago
    
def unix2dtm(u):
    """convert a unix time u to a datetime object"""
    return datetime.datetime.utcfromtimestamp(u)

# FIXME this does not give milli-second resolution [maybe total_seconds fault?]
def dtm2unix(d):
    """convert a datetime object to unix time (seconds since 01-Jan-1970)"""
    return (d - datetime.datetime(1970,1,1)).total_seconds()

# FIXME this is UNTESTED
def dtm2sdn(dt):
    """convert a datetime object to matlab serial date number"""
    mdn = dt + datetime.timedelta(days=366)
    frac_sec = (dt-datetime.datetime(dt.year, dt.month, dt.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
    frac_usec = dt.microsecond / (24.0 * 60.0 * 60.0 * 1.0e6)
    return mdn.toordinal() + frac_sec + frac_usec

# convert input time from string to unixtime float
def parse_packetfeeder_input_time(s, sec_plot_span):
    """
    convert string input for packetfeeder.py
    SUBTRACT sec_plot_span if input is zero float string
    """
    try:
        f = float(s)
        if f > 0.0:
            return f
        elif f == 0:
            # convenient end time
            dtm = parser.parse('2064-12-02 23:59:59')
            return dtm2unix(dtm)
        else:
            raise Exception('no negative unixtime floats accepted')
    except ValueError:
        dtm = parser.parse(s)
        return dtm2unix(dtm)


def datetime_dtm2sdn(dtm):
    """return matlab serial datenum converted from python datetime
    Input
        d   Date as an instance of type datetime.datetime
    Output
        The fractional day count since 0-Jan-0000 (proleptic ISO calendar)
        This is the 'datenum' datatype in matlab
    Notes on day counting
        matlab: day one is 1 Jan 0000
        python: day one is 1 Jan 0001
        hence an increase of 366 days, for year 0 AD was a leap year
    """
    d = dtm.date()
    t = dtm.time()
    dd = d.toordinal() + 366
    tt = datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    tt = datetime.timedelta.total_seconds(tt) / 86400
    return dd + tt


def datetime_sdn2dtm(datenum):
    """return python datetime converted from matlab serial datenum
    Input
        The fractional day count according to datenum datatype in matlab
    Output
        The date and time as a instance of type datetime in python
    Notes on day counting
        matlab: day one is 1 Jan 0000 
        python: day one is 1 Jan 0001
        hence a reduction of 366 days, for year 0 AD was a leap year
    """
    ii = datetime.datetime.fromordinal(int(datenum) - 366)
    ff = datetime.timedelta(days=datenum%1)
    return ii + ff

def testdoc(verbose=True):
    import doctest
    return doctest.testmod(verbose=verbose)

if __name__ == "__main__":
    testdoc(verbose=True)
