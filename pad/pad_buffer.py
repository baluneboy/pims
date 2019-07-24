#!/usr/bin/env python

import os
import glob
import pandas as pd
import numpy as np
import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from collections import deque

from ugaudio.load import padread_vxyz, padread_hourpart
from pims.padrunhist.main import get_pad_day_sensor_rate_mindur_files
from pims.utils.pimsdateutil import datetime_to_ymd_path, pad_fullfilestr_to_start_stop


class PadBottomBuffer(object):

    """an Nx4 array/container that fills like a bucket, bottom-up"""

    def __init__(self, fs, sec):
        self.fs = fs    # float sample rate, like 500.0
        self.sec = sec  # approximate size of data buffer (in seconds)
        self.num = np.int(np.ceil(2 * fs * sec))  # twice too big for buffer (never gets completely filled)
        self.vxyz = np.empty((self.num, 4))  # NOTE: this will contain garbage values
        self.vxyz.fill(np.nan)         # NOTE: this cleans up garbage values, replacing with NaNs
        self.is_full = False           # flag that goes True when data buffer is full
        self.idx = self.num + 1

    def __str__(self):
        s = '%s: ' % self.__class__.__name__
        s += 'sec = %.4f' % self.sec
        return s

    def add(self, more):

        if self.is_full:
            # TODO log warning that we tried to add to a buffer that's already full
            print 'buffer full already'
            # logger.info('Buffer already full, array shape is %s' % str(self.xyz.shape))
            # return

        offset = more.shape[0]
        idx1 = self.idx - offset - 1
        idx2 = self.idx - 1

        if idx1 < 0:
            raise Exception('unhandled condition...more data will overflow %s' % self.__class__.__name__)
        else:
            # print idx1, idx2, 'of', self.txyz.shape[0]
            self.vxyz[idx1:idx2, :] = more
            if self.idx == 0:
                self.is_full = True

        self.idx -= offset

    # def add_pad_file(self, f, dh):
    #     """extract dayhour, dh, part of PAD file, f, and add to buffer"""
    #
    #     # read file into vxyz, which has xyz already demeaned, and 1st column replaced by vecmag
    #     a = padread_vxyz(f)
    #
    #     # extract dayhour part of file to be added
    #
    #
    #     # add this file to buffer
    #     self.add(a)

    def summarize(self):

        # compute stats
        min_values = np.nanmin(self.vxyz, axis=0)
        max_values = np.nanmax(self.vxyz, axis=0)
        rms_values = np.nanstd(self.vxyz, axis=0)

        # # get magnitudes
        # mags = np.nanmax(np.abs(self.vxyz), axis=0)
        # mags[0] = np.nan

        # need to replace vecmag RMS with RSS(xRMS, yRMS, zRMS)
        rms_values[0] = np.sqrt(rms_values[1] ** 2 + rms_values[2] ** 2 + rms_values[3] ** 2)

        return min_values, max_values, rms_values

    def append_to_csv(self, csv_file, dh):
        min_values, max_values, rms_values = self.summarize()
        min_str = '{:.4e},{:.4e},{:.4e},{:.4e}'.format(*min_values)
        max_str = '{:.4e},{:.4e},{:.4e},{:.4e}'.format(*max_values)
        rms_str = '{:.4e},{:.4e},{:.4e},{:.4e}'.format(*rms_values)
        # mag_str = '{:.4e},{:.4e},{:.4e}'.format(*mags[1:])
        new_row = '%s,%02d,%s,%s,%s\n' % (dh.strftime('%Y-%m-%d'), dh.hour, min_str, max_str, rms_str)
        # csv_file = '/misc/yoda/www/plots/batch/results/monthly_minmaxrms/year1983/month12/1983-12_121f00_minmaxrms.csv'
        with open(csv_file, 'a') as fd:
            fd.write(new_row)


def demo_bottom_buffer():

    # fake/dummy arguments for buffer creation
    sec = 60 * 60  # seconds of TSH data (x,y,z acceleration values)
    fs = 500.0

    # create data buffer -- at some pt in code before we need mean(counts), probably just after GSS min/max found
    buffer = PadBottomBuffer(fs, sec)

    # test with sample data

    dh = datetime.datetime(2019, 7, 20, 0)

    filename = '/misc/yoda/pub/pad/year2019/month07/day20/sams2_accel_121f03/2019_07_20_00_00_00.522+2019_07_20_00_10_00.531.121f03'
    a = padread_hourpart(filename, fs, dh)
    buffer.add(a)

    filename = '/misc/yoda/pub/pad/year2019/month07/day20/sams2_accel_121f03/2019_07_20_01_00_00.590+2019_07_20_01_10_00.599.121f03'
    a = padread_hourpart(filename, fs, dh)
    buffer.add(a)

    return buffer


if __name__ == '__main__':

    buff = demo_bottom_buffer()
    csv_file = '/misc/yoda/www/plots/batch/results/monthly_minmaxrms/year1983/month12/1983-12_121f00_minmaxrms.csv'
    buff.append_to_csv(csv_file)
