# -*- coding: utf-8 -*-
"""PAD groups are pad groups or gaps that span either just a GMT day or start/stop times.

This module establishes PAD groups for a GMT day or arbitrary start/stop span via class definitions.

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
import datetime
from itertools import chain, groupby
from pathlib import Path
from pims.pad.sams_sensor_map import sensor_map
from pims.pad.mendmore import to_dtm
from pims.pad.pad_chunks import PadGroup, PadGap


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


class PadFileGroups(object):

    """iterator of metadata that contains PAD file groups (no gaps accounting here) for a start/stop range"""

    def __init__(self, sensor, start, stop=None, path='/misc/yoda/pub/pad', rate=500.0):
        self._sensor = sensor
        self._start = start if isinstance(start, datetime.datetime) else to_dtm(start)
        if stop is None:
            stop = self._start + datetime.timedelta(days=1)
        self._stop = stop if isinstance(stop, datetime.datetime) else to_dtm(stop)
        if self._start >= self._stop:
            raise Exception('in %s, start time must be strictly before stop time' % self.__class__.__name__)
        self._path = path
        self._rate = rate
        self._groups = iter(self._get_groups())

    def __str__(self):
        start_str = self._start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        stop_str = self._stop.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        s = '%s: %s from %s to %s (fs=%.2f)' % (self.__class__.__name__, self._sensor, start_str, stop_str, self._rate)
        return s

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._groups)

    def _get_groups(self):
        """return list of pad group objects that encompass this start/stop range"""
        d1, d2 = self._start.date(), self._stop.date()
        raw_groups = []
        for d in pd.date_range(d1, d2):
            pad_day_groups = PadFileDayGroups(self._sensor, d, path=self._path, rate=self._rate)
            if not pad_day_groups.df.empty:
                if d == d1:
                    # special handling first day (may need previous day too)
                    if self._start < pad_day_groups.df.iloc[0].Start:
                        prev_day = d - datetime.timedelta(days=1)
                        pre_grp = PadFileDayGroups(self._sensor, prev_day, path=self._path, rate=self._rate)
                        raw_groups.append(pre_grp)
                raw_groups.append(pad_day_groups)
        pad_days_groups = chain(*raw_groups)
        my_groups = []
        for g in pad_days_groups:
            if g.stop <= self._start:
                continue  # this group begins & ends completely before my desired start time, so skip it
            elif g.start >= self._stop:
                break  # we are already past stop time
            elif g.start <= self._start < g.stop:
                g.trim(self._start, self._stop)  # our span starts within this group sometime
            elif g.start <= self._stop < g.stop:
                g.trim(self._start, self._stop)  # our span stops within this group sometime
                my_groups.append(g)
                break
            my_groups.append(g)
        return my_groups

    @property
    def path(self):
        """return string for PAD path"""
        return self._path

    @property
    def rate(self):
        """return float for sample rate"""
        return self._rate

    @property
    def sensor(self):
        """return string for sensor"""
        return self._sensor

    @property
    def start(self):
        """return start datetime object for this group"""
        return self._start

    @property
    def stop(self):
        """return stop datetime object for this group"""
        return self._stop


class PadFileDayGroups(object):

    """iterator of metadata that contains PAD file groups (no gaps accounting here) for a day"""

    def __init__(self, sensor, day, path='/misc/yoda/pub/pad', rate=500.0):
        self._sensor = sensor
        self._day = day if isinstance(day, datetime.date) else to_dtm(day).date()
        self._path = path
        self._rate = rate
        self._df = self._get_files_dataframe()
        self._inds = self._get_group_inds()
        self._zip_inds = zip(self._inds, self._inds[1:])

    @property
    def sensor(self):
        """return string for sensor"""
        return self._sensor

    @property
    def day(self):
        """return day date object for this group"""
        return self._day

    @property
    def df(self):
        """return dataframe for PAD files in this group"""
        return self._df

    @property
    def path(self):
        """return string for PAD path"""
        return self._path

    @property
    def rate(self):
        """return float for sample rate"""
        return self._rate

    def __str__(self):
        day_str = self._day.strftime('%Y-%m-%d')
        s = '%s: %s for %s day directory (fs=%.2f)' % (self.__class__.__name__, self._sensor, day_str, self._rate)
        return s

    def __iter__(self):
        return self

    def __next__(self):
        i1, i2 = next(self._zip_inds)
        df_group = self._df.iloc[i1:i2]
        start = df_group.iloc[0].Start
        rate = df_group.iloc[0].SampleRate
        samples = sum(df_group.Samples)
        return PadGroup(start, rate, samples, df=df_group)

    def _get_files_dataframe(self):
        """return dataframe of file info for given sensor, day, pad_path"""
        ymd_str = 'year%04d/month%02d/day%02d' % (self._day.year, self._day.month, self._day.day)
        sensor_prefix, bytes_per_rec = sensor_map[self._sensor]
        sensor_subdir = sensor_prefix + self._sensor
        p = Path(self._path) / Path(ymd_str) / sensor_subdir
        if not p.exists():
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
        df_filtered = df[df['SampleRate'] == self._rate]
        return df_filtered

    def _get_plusminus_list(self):
        """return list of plus/minus signs extracted from each Filename in dataframe"""
        pm_func = lambda row: '+' if '+' in row.Filename else '-'
        pm_list = list(self._df.apply(pm_func, axis=1))
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
        inds[-1] += 1
        return inds


def demo_pad_file_day_groups(day, sensors, path_str='/misc/yoda/pub/pad', rate=500.0):
    delta_t = datetime.timedelta(seconds=1.0/rate)
    for sensor in sensors:
        pad_groups = PadFileDayGroups(sensor, day, path=path_str, rate=rate)
        print('---', sensor, '---', pad_groups)
        # runs = pad_groups.get_file_group_runs()
        # print(sensor, sum(runs), runs)
        prev_grp = None
        for i, grp in enumerate(pad_groups):
            if prev_grp is not None:
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
                gap = PadGap(gap_start, gap_rate, gap_samples)
                print(prefix, gap, suffix)
            print('%03d' % i, grp)
            prev_grp = grp


def demo_pad_file_groups(start, stop, sensors, pth_str='/misc/yoda/pub/pad', rate=500.0):
    delta_t = datetime.timedelta(seconds=1.0/rate)
    for sensor in sensors:
        pad_groups = PadFileGroups(sensor, start, stop=stop, path=pth_str, rate=rate)
        print('<--', sensor, '-->', pad_groups)
        # runs = pad_groups.get_file_group_runs()
        # print(sensor, sum(runs), runs)
        prev_grp = None
        for i, grp in enumerate(pad_groups):
            if prev_grp is not None:
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
                gap = PadGap(gap_start, gap_rate, gap_samples)
                print(prefix, gap, suffix)
            print('%03d' % i, grp)
            prev_grp = grp


if __name__ == '__main__':
    pass
