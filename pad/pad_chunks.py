# -*- coding: utf-8 -*-
"""PAD chunks are either groups of contiguous PAD files or gaps.

This module defines what PAD chunks are via class definitions.

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

import math
import numpy as np
import datetime


def strfdelta(tdelta, fmt):
    """format timedelta object"""
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    d["microseconds"] = tdelta.microseconds
    return fmt.format(**d)


class PadChunk(object):

    def __init__(self, start, rate, samples, df=None):
        self._df = df
        self._start = start
        self._rate = rate
        self._samples = self._verify_samples(samples)
        self._duration = self._get_duration()
        self._stop = self._start + self._duration
        self._was_nudged = False
        self._nudge_sec = 0.0

    def __str__(self):
        startstr = self._start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        stopstr = self._stop.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        durstr = strfdelta(self.duration, '{days:02d}d {hours:02d}h {minutes:02d}m {seconds:02d}s {microseconds:06d}us')
        s = '%s to %s (%s, %9d pts, %4d files)' % (startstr, stopstr, durstr, self.samples, len(self.df))
        if self._was_nudged:
            s += ' nudged %.3fs' % self._nudge_sec
        return s

    @property
    def was_nudged(self):
        """return boolean True if this group was nudged"""
        return self._was_nudged

    @property
    def nudge_sec(self):
        """return float for number of seconds this group was nudged (negative is left)"""
        return self._nudge_sec

    @property
    def df(self):
        """return dataframe for this group"""
        return self._df

    @property
    def rate(self):
        """return float for sample rate of this group"""
        return self._rate

    @property
    def samples(self):
        """return number of samples (pts) for this group"""
        return self._samples

    def _verify_samples(self, value):
        """verify number of samples is integer"""
        if not isinstance(value, int):
            raise TypeError('number of samples must be an integer')
        return value

    @property
    def duration(self):
        """return datetime.timedelta as duration for this group"""
        return self._duration

    def _get_duration(self):
        """get duration as timedelta object"""
        if self._samples <= 0:
            raise ValueError('cannot have zero or negative number of samples, that is just crazy')
        return datetime.timedelta(seconds=(self._samples-1)/self._rate)

    @property
    def stop(self):
        """return stop time for this group"""
        return self._stop

    @property
    def start(self):
        """return start time for this group"""
        return self._start

    @start.setter
    def start(self, t):
        """setter used to nudge entirety of this chunk, set start time to t then stop time to t + duration"""
        if self._was_nudged:
            raise Exception('cannot nudge more than once')
        nudge_sec = (t - self.start).total_seconds()
        if np.abs(nudge_sec) < 1.0e-4:
            # nudge too small, round to zero (i.e. no nudge)
            return
        self._nudge_sec = nudge_sec
        self._was_nudged = True
        self._start = t
        self._stop = t + self._duration


class PadGroup(PadChunk):

    def __init__(self, start, rate, samples, df):
        PadChunk.__init__(self, start, rate, samples, df=df)

    def trim(self, t1, t2):
        """trim entries that do not fall within t1 <= t <= t2"""
        df = self._df[self._df.Stop >= t1]
        self._df = df[df.Start <= t2]
        self._start = self._df.iloc[0].Start
        self._samples = self._verify_samples(sum(self._df.Samples))
        self._duration = self._get_duration()
        self._stop = self._start + self._duration


class PadGap(PadChunk):

    def __init__(self, start, rate, samples):
        PadChunk.__init__(self, start, rate, samples)

    def __str__(self):
        # if self.samples == 0:
        #     dur_str = '00h 00m 00s 000000us'
        # else:
        dur_str = strfdelta(self._duration,
                            '{days:02d}d {hours:02d}h {minutes:02d}m {seconds:02d}s {microseconds:06d}us')
        start_str = self._start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        stop_str = self._stop.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        s = '%s to %s (%s, %9d pts)' % (start_str, stop_str, dur_str, self.samples)
        s += ' <-- gap -->'
        return s

    def _verify_samples(self, value):
        if isinstance(value, int):
            return value
        if float(value).is_integer():
            return int(value)
        else:
            new_value = int(math.floor(value))
            # warnings.warn('number of samples, %s, was not an integer, so took integer part %s' % (value, new_value))
            return new_value


if __name__ == '__main__':
    pass
