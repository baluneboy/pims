"""Mend, that is, fix, repair or fill a SAMS data gap using PIMS db tables & PAD files.

This module queries PIMS db tables and reads PAD files in order to surgically fill,
repair or otherwise fix a SAMS acceleration data gap in the PAD file structure.

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
import pandas as pd
import portion as po
import datetime
from itertools import groupby, tee
from pathlib import Path
from pims.pad.sams_sensor_map import sensor_map
# import warnings
#from pims.pad.walkpad import PadFileIntRms
from pandas_ods_reader import read_ods
# from ugaudio.load import padread
# from ugaudio.create import demo_write_read_pad_file


def read_sample_rate(hdr):
    """return sample rate (sa/sec) from header file object"""
    with open(hdr, mode='r') as fid:
        fs_str = [line.rstrip('\n') for line in fid if 'SampleRate' in line]
        fs = float(fs_str[0].split('>')[1].split('<')[0])
    return fs


def strfdelta(tdelta, fmt):
    """format timedelta object"""
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    d["microseconds"] = tdelta.microseconds
    return fmt.format(**d)


def get_data_file(hdr):
    """return companion data file object"""
    parts = list(hdr.parts)
    parts[-1] = parts[-1].replace('.header', '')
    return Path(*parts)


def value_from_str(v):
    """return either a float or an int from a string depending on if it contains a decimal pt or not"""
    if '.' in v:
        return float(v)
    return int(v)


def datetime_from_list(time_parts):
    """return datetime object from list of parts"""
    frac, sec = math.modf(time_parts[-1])
    time_parts = time_parts[:-1]
    time_parts.extend([int(sec), round(1e3 * frac) * 1000])
    return datetime.datetime(*time_parts)


def encode_list(s_list):
    """return list of lists, each with 2 elements [run_length, value]
    [ '+', '+', '+', '-', '-', ...] -> [ [3, '+'], [2, '-'], ...] """
    return [[len(list(group)), key] for key, group in groupby(s_list)]


def pairwise(iterable):
    """return iterable that is pairings of input iterable
    s -> (s0,s1), (s2,s3), (s4, s5), ..."""
    a = iter(iterable)
    return zip(a, a)


def pairwise_overlap(iterable):
    """return iterable that is pairings of input iterable with overlap
    s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def demo_show_df(df):
    """show dataframe"""
    pd.set_option('display.max_columns', None)
    print(df)


class DataFrameIterator(object):
    """Iterator for dataframe object."""

    def __init__(self, df, inds):
        self.df = df
        self.inds = inds
        self.zip_inds = zip(inds, inds[1:])

    def __iter__(self):
        return self

    def __next__(self):
        i1, i2 = next(self.zip_inds)
        return self.df.iloc[i1:i2]


class PadFileDayGroups(object):

    def __init__(self, sensor, day, pth='/misc/yoda/pub/pad', rate=500.0):
        self.sensor = sensor
        self.day = day
        self.pth = pth
        self.rate = rate
        self.df = self._get_files_dataframe()
        self.inds = self._get_group_inds()
        self._zip_inds = zip(self.inds, self.inds[1:])

    def __iter__(self):
        return self

    def __next__(self):
        i1, i2 = next(self._zip_inds)
        df_group = self.df.iloc[i1:i2]
        start = df_group.iloc[0].Start
        rate = df_group.iloc[0].SampleRate
        samples = sum(df_group.Samples)
        return PadGroup(start, rate, samples, df=df_group)

    def _get_files_dataframe(self):
        """return dataframe of file info for given sensor, day, pad_path"""
        ymd_parts = (int(x) for x in self.day.split('-'))
        ymd = datetime.datetime(*ymd_parts).date()
        ymd_str = 'year%04d/month%02d/day%02d' % (ymd.year, ymd.month, ymd.day)
        sensor_prefix, bytes_per_rec = sensor_map[self.sensor]
        sensor_subdir = sensor_prefix + self.sensor
        p = Path(self.pth) / Path(ymd_str) / sensor_subdir
        if not p.exists():
            #print('no such path %s', p)
            return pd.DataFrame()
        all_files = []
        for hdr in p.rglob('*.header'):
            if 'quarantine' in hdr.parent.name:
                continue
            fs = read_sample_rate(hdr)
            dat = get_data_file(hdr)
            num_bytes = dat.stat().st_size
            num_pts = int(num_bytes / bytes_per_rec)
            start_str = dat.name.split("+", 1)[0].split('-', 1)[0]
            t_parts = [value_from_str(v) for v in start_str.split('_')]
            start = datetime_from_list(t_parts)
            stop = start + datetime.timedelta(seconds=(num_pts - 1) / fs)
            all_files.append((dat.name, dat.parent, num_pts, fs, start, stop))
        all_files.sort()  # this gets us into ascending time order for sure
        columns = ["Filename", "Parent", "Samples", "SampleRate", "Start", "Stop"]
        df = pd.DataFrame.from_records(all_files, columns=columns)
        # only keep rows with desired sample rate (and sort on start time)
        df_filtered = df[df['SampleRate'] == self.rate]
        return df_filtered

    def _get_plusminus_list(self):
        """return list of plus/minus signs extracted from each Filename in dataframe"""
        pm_list = list(self.df.apply(lambda row: '+' if '+' in row.Filename else '-', axis=1))
        return pm_list

    def _get_encoded_run_lengths(self):
        """return run-length-encoded contiguous files from plus/minus list"""
        # get plus/minus characters to use for grouping contiguous files
        pm_list = self._get_plusminus_list()
        if not pm_list:
            return []
        pm_list[0] = '-'  # 1st element is effectively a minus for grouping purposes
        encoded_pm_list = encode_list(pm_list)
        # add a trailing "zero plus" element if we have an odd number
        if len(encoded_pm_list) % 2 != 0:
            encoded_pm_list.append([0, '+'])
        return encoded_pm_list

    def get_file_group_runs(self):
        """return a list of run length integers based on plus/minus indicators in filenames"""
        runs = []
        encoded_pm_list = self._get_encoded_run_lengths()
        for one, two in pairwise(encoded_pm_list):
            num_minus = one[0]
            if num_minus == 1:
                runs.append(one[0] + two[0])
            else:
                for i in range(0, num_minus - 1):
                    runs.append(1)
                runs.append(1 + two[0])
        return runs

    def _get_group_inds(self):
        """return iterable over groups of files in form of dataframe"""
        runs = self.get_file_group_runs()
        inds = np.cumsum(np.array([0] + runs))
        inds[-1] = inds[-1] + 1
        return inds

    # def dataframe_groups(self):
    #     """return iterable over groups of files in form of dataframe"""
    #     inds = self._get_group_inds()
    #     dfi = DataFrameIterator(self.df, inds)
    #     return dfi


class PadChunk(object):

    def __init__(self, start, rate, samples, df=None):
        self._df = df
        self._start = start
        self._rate = rate
        self._samples = self._set_samples(samples)
        self._duration = self._set_duration()
        self._stop = self._start + self._duration

    def __str__(self):
        dur_str = strfdelta(self.duration, '{hours:02d}h {minutes:02d}m {seconds:02d}s {microseconds:06d}us')
        s = '%s to %s (%s, %9d pts)' % (self.start, self.stop, dur_str, self.samples)
        return s

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

    def _set_samples(self, value):
        if not isinstance(value, int):
            raise TypeError('number of samples must be an integer')
        return value

    @property
    def duration(self):
        """return datetime.timedelta as duration for this group"""
        return self._duration

    def _set_duration(self):
        if self._samples == 0:
            return datetime.timedelta(seconds=0)
        else:
            return datetime.timedelta(seconds=(self._samples-1)/self._rate)

    @property
    def stop(self):
        """return stop time for this group"""
        return self._stop

    @property
    def start(self):
        """return start time for this group"""
        return self._start


class PadGroup(PadChunk):

    def __init__(self, start, rate, samples, df):
        PadChunk.__init__(self, start, rate, samples, df=df)


class PadGap(PadChunk):

    def __init__(self, start, rate, samples):
        PadChunk.__init__(self, start, rate, samples)

    def __str__(self):
        if self.samples == 0:
            dur_str = '00h 00m 00s 000000us'
        else:
            dur_str = strfdelta(self.duration, '{hours:02d}h {minutes:02d}m {seconds:02d}s {microseconds:06d}us')
        s = '%s to %s (%s, %9d pts)' % (self.start, self.stop, dur_str, self.samples)
        return s

    def _set_samples(self, value):
        if isinstance(value, int):
            return value
        if float(value).is_integer():
            return int(value)
        else:
            new_value = int(math.floor(value))
            # warnings.warn('number of samples, %s, was not an integer, so took integer part %s' % (value, new_value))
            return new_value


class OldPadGroup(object):

    def __init__(self, df):
        self._df = df
        self._start = df.iloc[0].Start
        self._rate = df.iloc[0].SampleRate
        self._samples = sum(df.Samples)
        self._duration = datetime.timedelta(seconds=(self._samples-1)/self._rate)
        self._stop = self._start + self._duration

    def __str__(self):
        dur_str = strfdelta(self.duration, '{hours:02d}h {minutes:02d}m {seconds:02d}s {microseconds:06d}us')
        s = '%s to %s (%s, %9d pts)' % (self.start, self.stop, dur_str, self.samples)
        return s

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

    @property
    def duration(self):
        """return datetime.timedelta as duration for this group"""
        return self._duration

    @property
    def stop(self):
        """return stop time for this group"""
        return self._stop

    @property
    def start(self):
        """return start time for this group"""
        return self._start


#pad_file = '/home/pims/PycharmProjects/mendTheGap/example2.pad'
# demo_write_read_pad_file(pad_file)


def demo_file_groups():
    sensors = ['121f02', '121f03', '121f04', '121f05', '121f08']
    # sensors = ['121f03', ]
    day, pth_str = '2020-04-07', '/misc/yoda/pub/pad'
    # day, pth_str = '2020-04-01', '/home/pims/data/pad'
    # day, pth_str = '2020-04-05', 'G:/data/pad'
    rate = 500.0
    delta_t = datetime.timedelta(seconds=1.0/rate)
    for sensor in sensors:
        print('---', sensor, '---')
        pad_groups = PadFileDayGroups(sensor, day, pth=pth_str, rate=rate)
        # runs = pad_groups.get_file_group_runs()
        # print(sensor, sum(runs), runs)
        prev_grp = None
        for i, grp in enumerate(pad_groups):
            if prev_grp is None:
                # print('no previous group')
                pass
            else:
                prefix = 'gap'
                suffix = ''
                sec_between_groups = (grp.start - prev_grp.stop).total_seconds()
                gap_start = prev_grp.stop + delta_t
                gap_rate = prev_grp.rate
                if sec_between_groups < 0:
                    print('*** HOW CAN GAP HAVE NEGATIVE LENGTH?! ***')
                    break
                elif sec_between_groups < delta_t.total_seconds():
                    print('*** A GAP THAT IS SHORTER THAN DELTA-T?! ***')
                    break
                elif (sec_between_groups == delta_t.total_seconds()) or (prev_grp.stop == grp.start):
                    prefix = 'wtf'
                    suffix = '*** A GAP THAT IS EQUAL TO DELTA-T IS NOT REALLY A GAP! ***'
                    gap_samples = 0
                else:
                    gap_stop = grp.start - delta_t
                    gap_duration = gap_stop - gap_start
                    gap_samples = (gap_duration.total_seconds() * grp.rate) + 1
                    # if gap_samples < 0:
                    #     pass
                    # elif gap_samples == 0:
                    #     pass
                    # elif gap_samples < 1:
                    #     gap_str = '--h --m --s ------us'
                    # else:
                    #     gap_str = strfdelta(gap_duration,
                    #                         '{hours:02d}h {minutes:02d}m {seconds:02d}s {microseconds:06d}us')
                    # print('gap %s to %s (%s, %13.3f pts)' % (gap_start, gap_stop, gap_str, gap_samples))
                gap = PadGap(gap_start, gap_rate, gap_samples)
                print(prefix, gap, suffix)
            print('%03d' % i, grp)
            prev_grp = grp


class GmtIterator(object):

    def __init__(self, start, stop, rate):
        self.start = start
        self.stop = stop
        self.rate = rate
        self.interval = po.closed(self.start, self.stop)
        self.step = datetime.timedelta(seconds=1.0/self.rate)
        self.iter = po.iterate(self.interval, self.step)

    def __str__(self):
        return '%s to %s rate of %0.3f sa/sec (step %s)' % (self.start, self.stop, self.rate, self.step)


def demo_gmt_iterator():
    start = datetime.datetime(2020, 3, 4, 5, 6, 7, 123456)
    #stop = datetime.datetime(2020,  3, 4, 5, 6, 8, 123456)
    fs = 50.0
    num_pts = 12
    dur = (num_pts - 1) / fs
    delta = datetime.timedelta(seconds=dur)
    stop = start + delta
    sdi = GmtIterator(start, stop, fs)
    for i in sdi.iter:
        print(i)


if __name__ == '__main__':
    demo_file_groups()
    #demo_gmt_iterator()
    # c = Count()
    # for i in c:
    #     print(i)
