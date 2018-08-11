#!/usr/bin/env python

import os
import glob
from collections import OrderedDict
from pims.padrunhist.main import sensor2subdir


def glob_latest_pad_path(prefix, suffix):
    """return latest chrono PAD path after matching prefix/suffix and reverse sort of glob"""
    L = glob.glob(os.path.join(prefix, suffix))
    L.sort(reverse=True)  # put most recent at beginning
    return L[0]


class PadHeadersLatest(object):

    def __init__(self, pad_dir='/misc/yoda/pub/pad'):
        self.pad_dir = pad_dir
        self.sensor = None
        self.results = OrderedDict()

    def __str__(self):
        return self.__class__.__name__

    def get_headers(self):

        # get latest day directory
        latest_day_dir = glob_latest_pad_path(self.pad_dir, 'year*/month*/day*')

        # get list of sensor subdirectories under latest day directory
        sensor_subdirs = os.listdir(latest_day_dir)
        sensor_subdirs.sort()

        # iterate over sensor subdirs to get latest header and header file count for each sensor
        for sensor_subdir in sensor_subdirs:
            subdir = os.path.join(latest_day_dir, sensor_subdir)
            L = os.listdir(subdir)
            L.sort(reverse=True)
            self.results[sensor_subdir] = (os.path.join(subdir, L[0]), len(L))


class PadHeadersLatestBySensor(object):

    def __init__(self, sensor, pad_dir='/misc/yoda/pub/pad'):
        self.pad_dir = pad_dir
        if '*' in sensor:
            raise ValueError('no asterisks allowed in sensor string; be specific, like "121f03" or "es05"')
        self.sensor = sensor
        self.results = OrderedDict()

    def __str__(self):
        return self.__class__.__name__

    def get_headers(self):

        # get subdir pattern from sensor string
        subdir = sensor2subdir(self.sensor)
        ymd_sensor_subdir = os.path.join('year*/month*/day*', subdir)

        # get latest day directory
        sensor_subdir = glob_latest_pad_path(self.pad_dir, ymd_sensor_subdir)
        L = os.listdir(sensor_subdir)
        L.sort(reverse=True)
        self.results[subdir] = ([os.path.join(sensor_subdir, L[0])], len(L))


def demo():

    phd = PadHeadersLatest()
    phd.get_headers()
    print phd.results

    phs = PadHeadersLatestBySensor('121f06')
    phs.get_headers()
    print phs.results


if __name__ == '__main__':
    demo()
