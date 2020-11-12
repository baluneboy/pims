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

import datetime
from dateutil import parser


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
        self._start = t1 - datetime.timedelta(seconds=1/self._rate)  # this for count pts (not index...COUNT)
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


def show_head(d):
    print(d)


if __name__ == '__main__':

    rate = 500.0
    start = '2020-04-06 00:06:00.211'

    ct = CountEndtime(start, rate)
    print(ct)
    ct += 1.0; print(ct)
    ct += 2; print(ct)
    ct = ct + 1.0; print(ct)
