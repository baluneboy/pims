"""Mend more, that is, help with fix, repair or fill a SAMS data gap using PIMS db tables & PAD files.

This module gives support to mend.py in order to surgically fill, repair or otherwise
fix a SAMS acceleration data gap in the PAD file structure.

Examples:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

TODO:
    * put todos here

"""

import re
import datetime
from dateutil import parser

HMSREGEX = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')


def parse_timedelta(time_str):
    parts = HMSREGEX.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in list(parts.items()):
        if param:
            time_params[name] = int(param)
    return datetime.timedelta(**time_params)


def to_dtm(s):
    """return datetime object given a parseable string or a datetime object"""
    if isinstance(s, datetime.datetime):
        return s
    else:
        return parser.parse(s)


class CountEndtime(object):

    """A class to track count of samples (pts) to also track end time."""

    def __init__(self, start, rate):
        # get tzero wrangled in terms of counts (not indices)
        t1 = start if isinstance(start, datetime.date) else to_dtm(start)
        self._rate = float(rate)
        self._start = t1 - datetime.timedelta(seconds=1/self._rate)  # this for count pts (not index)
        self._count = 0
        self._end = self._start

    def __str__(self):
        return 'count = {}, end = {}'.format(self._count, self._end.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

    @property
    def count(self):
        """return count for this object"""
        return self._count

    @property
    def end(self):
        """return end time for this object"""
        return self._end

    @property
    def start(self):
        """return start time for this object"""
        return self._start

    @property
    def rate(self):
        """return rate this object"""
        return self._rate

    def __add__(self, other):
        if isinstance(other, float):
            other = int(other)
        if not isinstance(other, int):
            raise TypeError('can only add integer number of points to keep track of counts and end time')
        self._count += other
        self._end += datetime.timedelta(seconds=other/self.rate)
        return self


class SpanCalc(object):

    def __init__(self, rate, start=None, stop=None, duration='1h'):
        self._rate = float(rate)
        self._start = None
        self._stop = None
        self._duration = None
        self._pts = None

        # need exactly one None in list of [start, stop, span]
        if [start, stop, duration].count(None) != 1:
            raise RuntimeError('need to define exactly 2 of 3 inputs (start, stop, span) & leave exactly 1 as None')

        # get the other two inputs from among (start, stop, duration)
        if stop is None:
            self._start = start if isinstance(start, datetime.datetime) else to_dtm(start)
            self._set_duration(duration)
            self._stop = self._calc_stop()
        elif start is None:
            self._stop = stop if isinstance(stop, datetime.datetime) else to_dtm(stop)
            self._set_duration(duration)
            self._start = self._calc_start()
        elif duration is None:
            self._start = start if isinstance(start, datetime.datetime) else to_dtm(start)
            self._stop = stop if isinstance(stop, datetime.datetime) else to_dtm(stop)
            self._duration = self._stop - self._start
            self._pts = self._dur_to_pts(self._duration)
        else:
            raise RuntimeError('some kind of logic error, how did we ever get here???')

    def _pts_to_dur(self, num_pts):
        """return timedelta object for given num_pts using rate"""
        return datetime.timedelta(seconds=(num_pts-1)/self._rate)

    def _dur_to_pts(self, dur):
        """return integer num_pts from timedelta object, dur, using rate"""
        return dur.total_seconds() * self._rate

    def _set_duration(self, d):
        """set duration as a timedelta object"""
        if isinstance(d, datetime.timedelta):
            self._duration = d
        elif isinstance(d, str):
            if d.endswith('pts'):
                self._pts = int(d.rstrip('pts'))
                self._duration = self._pts_to_dur(self._pts)
                return
            else:
                self._duration = parse_timedelta(d)
        else:
            raise TypeError('trying to set duration with unhandled type')

        self._pts = self._dur_to_pts(self._duration)

    def _calc_start(self):
        """compute start time from stop and duration"""
        return self.stop - self._duration

    def _calc_stop(self):
        """compute stop time from start and duration"""
        return self.start + self._duration

    def __str__(self):
        start_str = self._start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        stop_str = self._stop.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        dur_str = '%.3f seconds (%g pts)' % (self._duration.total_seconds(), self._pts)
        return '%s\n%s\n%s' % (start_str, stop_str, dur_str)

    @property
    def start(self):
        """return start time"""
        return self._start

    @property
    def stop(self):
        """return stop time"""
        return self._stop

    @property
    def duration(self):
        """return duration as timedelta object"""
        return self._duration

    @property
    def pts(self):
        """return number of points (samples)"""
        return self._pts

    @property
    def rate(self):
        """return rate as float"""
        return self._rate


def demo_span_calc_class():
    rate = 500.0
    du = datetime.timedelta(seconds=2)
    sc = SpanCalc(rate, start=datetime.datetime(2020,1,2,3,4,5), stop=None, duration=du); print(sc)
    sc = SpanCalc(rate, start=datetime.datetime(2020,1,2,3,4,5), stop=None, duration='1s'); print(sc)
    sc = SpanCalc(rate, stop=datetime.datetime(2020,1,2,3,4,5), start=None, duration='1m'); print(sc)
    sc = SpanCalc(rate, start=datetime.datetime(2020,1,2,3,4,5), stop=datetime.datetime(2020,1,2,4,4,5), duration=None); print(sc)
    # 004 2020-04-06 00:06:03.211 to 2020-04-06 00:06:03.247 (00d 00h 00m 00s 036000us,        19 pts,    3 files)
    sc = SpanCalc(rate,
                  start=parser.parse('2020-04-06 00:06:03.211'),
                  stop=parser.parse('2020-04-06 00:06:03.247'),
                  duration=None)
    print(sc)
    # 001 2020-04-06 00:06:00.205 to 2020-04-06 00:06:00.205 (00d 00h 00m 00s 000000us,         0 pts) <-- gap -->
    sc = SpanCalc(rate,
                  start=parser.parse('2020-04-06 00:06:00.205'),
                  stop=parser.parse('2020-04-06 00:06:00.205'),
                  duration=None)
    print(sc)
    # 011 2020-04-06 00:06:00.205 to 2020-04-06 00:06:00.207 (00d 00h 00m 00s 002000us,         1 pts) <-- gap -->
    sc = SpanCalc(rate,
                  start=parser.parse('2020-04-06 00:06:00.205'),
                  stop=parser.parse('2020-04-06 00:06:00.207'),
                  duration=None)
    print(sc)
    # 022 2020-04-06 00:06:00.205 to 2020-04-06 00:06:00.206 (00d 00h 00m 00s 001000us,        0.5 pts) <-- gap -->
    sc = SpanCalc(rate,
                  start=parser.parse('2020-04-06 00:06:00.205'),
                  stop=parser.parse('2020-04-06 00:06:00.206'),
                  duration=None)
    print(sc)
    print('num_pts', sc.pts)


if __name__ == '__main__':

    rate = 500.0
    start = '2020-04-06 00:06:00.211'

    ct = CountEndtime(start, rate)
    print(ct)
    ct += 1.0; print(ct)
    ct += 2; print(ct)
    ct = ct + 1.0; print(ct)

    demo_span_calc_class()