#!/usr/bin/env python3

import os
import time
import datetime
import math
import pandas as pd
import portion as po
from pathlib import Path
from sams_sensor_map import sensor_map


pd.options.display.width = 0


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


pad_path_str = 'G:/data/pad'
sensor = '121f02'
day = '2020-04-05'

ymd_parts = (int(x) for x in day.split('-'))
ymd = datetime.datetime(*ymd_parts).date()
ymd_str = 'year%04d/month%02d/day%02d' % (ymd.year, ymd.month, ymd.day)
sensor_prefix, bytes_per_rec = sensor_map[sensor]
sensor_subdir = sensor_prefix + sensor
p = Path(pad_path_str) / Path(ymd_str) / sensor_subdir

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

columns = ["Filename", "Parent", "NumPts", "SampleRate", "Start", "Stop"]
df = pd.DataFrame.from_records(all_files, columns=columns)
print(df)

d = po.IntervalDict()
print(d)
d[po.closed(0, 3)] = 'banana'
print(d)
d[4] = 'apple'
print(d)
d[po.closed(2, 4)] = 'orange'
print(d)
