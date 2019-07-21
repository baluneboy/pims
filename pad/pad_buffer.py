#!/usr/bin/env python

import glob
import pandas as pd
import numpy as np
import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
from collections import deque

from ugaudio.load import padread
from pims.padrunhist.main import get_pad_day_sensor_rate_mindur_files
from pims.utils.pimsdateutil import datetime_to_ymd_path, pad_fullfilestr_to_start_stop


class PadBottomBuffer(object):

    def __init__(self, fs, sec):
        self.fs = fs  # float sample rate, like 500.0
        self.sec = sec  # approximate size of data buffer (in seconds)
        self.num = np.int(np.ceil(1.2 * fs * sec))  # 1.2x too big of buffer (never gets completely filled)
        self.txyz = np.empty((self.num, 4))  # NOTE: this will contain garbage values
        self.txyz.fill(np.nan)         # NOTE: this cleans up garbage values, replacing with NaNs
        self.is_full = False           # flag that goes True when data buffer is full
        self.idx = 0

    def __str__(self):
        s = '%s: ' % self.__class__.__name__
        s += 'sec = %.4f' % self.sec
        return s

    def add(self, more):

        if self.is_full:
            # TODO log entry that we tried to add to a buffer that's already full
            raise Exception('never expecting buffer to completely fill')
            # logger.info('Buffer already full, array shape is %s' % str(self.xyz.shape))
            # return

        offset = more.shape[0]
        if self.idx + offset > self.txyz.shape[0]:
            offset = self.txyz[self.idx:, :].shape[0]
            self.txyz[self.idx:self.idx + offset, :] = more[0:offset, :]
            self.is_full = True
            raise Exception('unhandled condition...more data will overflow %s' % self.__class__.__name__)
        else:
            self.txyz[self.idx:self.idx + offset, :] = more
        # print(self.idx, self.idx + offset)
        self.idx = self.idx + offset


def demo_bottom_buffer():

    # fake/dummy arguments for buffer creationg
    sec = 2  # how many seconds-worth of TSH data (x,y,z acceleration values)
    fs = 3.0

    # create data buffer -- at some pt in code before we need mean(counts), probably just after GSS min/max found
    buffer = PadBottomBuffer(fs, sec)
    print buffer.txyz

    # add some data to buffer (note shape is Nx3, with 3 columns for xyz)
    b = np.arange(8).reshape(2, 4)
    buffer.add(b)
    print buffer.txyz

    # add some data to buffer (note shape is Nx3, with 3 columns for xyz)
    b = np.arange(12).reshape(3, 4)
    buffer.add(b)
    print buffer.txyz

    # add some data to buffer (note shape is Nx3, with 3 columns for xyz)
    b = np.arange(12).reshape(3, 4)
    buffer.add(b)
    print buffer.txyz


if __name__ == '__main__':
    demo_bottom_buffer()
