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

import os
import math
import numpy as np
import pandas as pd
import portion as po
import datetime
from itertools import groupby, tee
from pathlib import Path
from sams_sensor_map import sensor_map
#from pims.pad.walkpad import PadFileIntRms
# from pandas_ods_reader import read_ods
from ugaudio.load import pad_read
# from ugaudio.create import demo_write_read_pad_file


def read_sample_rate(hdr):
    """return sample rate (sa/sec) from header file object"""
    with open(hdr, mode='r') as fid:
        fs_str = [line.rstrip('\n') for line in fid if 'SampleRate' in line]
        fs = float(fs_str[0].split('>')[1].split('<')[0])
    return fs


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
        return PadGroup(df_group)

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
        columns = ["Filename", "Parent", "NumPts", "SampleRate", "Start", "Stop"]
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

    def _get_file_group_runs(self):
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
        runs = self._get_file_group_runs()
        inds = np.cumsum(np.array([0] + runs))
        inds[-1] = inds[-1] + 1
        return inds

    # def dataframe_groups(self):
    #     """return iterable over groups of files in form of dataframe"""
    #     inds = self._get_group_inds()
    #     dfi = DataFrameIterator(self.df, inds)
    #     return dfi


class PadGroup(object):

    def __init__(self, df):
        self.df = df
        self.start = df.iloc[0].Start
        self.rate = df.iloc[0].SampleRate
        self.duration = self._get_duration()

    def __str__(self):
        s = '%s %d pts' % (self.start, self.duration)
        return s

    def _get_duration(self):
        return sum(self.df.NumPts)


#pad_file = '/home/pims/PycharmProjects/mendTheGap/example2.pad'
# demo_write_read_pad_file(pad_file)


def demo_file_groups():
    sensors = ['121f02', '121f03', '121f04', '121f05', '121f08']
    sensors = ['121f03']
    day = '2020-04-01'
    # pth_str = '/home/pims/data/pad'
    pth_str = '/mnt/pad'
    rate = 500.0
    for sensor in sensors:
        pfdg = PadFileDayGroups(sensor, day, pth=pth_str, rate=rate)
        runs = pfdg._get_file_group_runs()
        print(sensor, sum(runs), runs)

        for i, g in enumerate(pfdg):
            print(i, g)

        for a, b in zip(pfdg.df.Parent, pfdg.df.Filename):
            fname = os.path.join(a, b)
            arr = pad_read(fname)
            print(arr.shape, fname)

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