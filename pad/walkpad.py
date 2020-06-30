import os
from datetime import timedelta, date
from collections import deque
from pathlib import Path
from scipy import signal

from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.files.filter_pipeline import FileFilterPipeline, HeaderMatchesSensorRateCutoffPad, BigFile
from pims.signal.filter import my_psd, my_int_rms
from ugaudio.load import padread


# FIXME this function should go in better/generic location BUT w/o breaking daily infrastructure from 2to3 deal
def sensor_subdir(sensor):
    """return string for sensor subdir name given sensor designation"""
    if sensor.startswith('121f0'):
        return 'sams2_accel_' + sensor
    elif sensor.startswith('es'):
        return 'samses_accel_' + sensor
    else:
        return 'unknown'


# FIXME this needs StopIteration on probably the cumulative number of days that have been visited
class PadFilesIterator(object):
    """Iterator for walking PAD files forever...no stop at num_days visited!"""

    def __init__(self, sensor, start, num_days, reverse=True, top='/misc/yoda/pub/pad', ffp=None):
        self.sensor = sensor
        self.subdir = sensor_subdir(sensor)
        self.day = start
        self.reverse = reverse
        self.top = top
        self.delta = timedelta(days=-1) if self.reverse else timedelta(days=1)
        self.files = deque([])
        self.num_days = num_days
        self._day_count = 0
        self.ffp = ffp

    def __iter__(self):
        return self

    def apply_file_filter(self, files):
        """apply processing pipeline (note: self.ffp is callable)"""
        if len(files) == 0 or self.ffp is None:
            keep_files = files
        else:
            keep_files = list(self.ffp(files))
        return keep_files

    def __next__(self):
        while not self.files:
            # build path to PAD files for glob pattern based on sensor extension
            day = self.day
            self.day += self.delta
            self._day_count += 1
            ymd_path = os.path.join(datetime_to_ymd_path(day, base_dir=self.top), self.subdir)
            p = Path(ymd_path)

            # glob PAD files for this pad_path/ymd/sensor
            sorted_files = sorted(list(p.glob('*.' + self.sensor)), reverse=self.reverse)

            # get filenames as strings instead of some form of generic path objects
            files = [str(i) for i in sorted_files]

            # apply file filter pipeline (if needed) to keep only desirable files for this day
            keep_files = self.apply_file_filter(files)

            # extend deque to include these kept files for this day
            self.files.extend(keep_files)

            # stop iteration if day count exceeds desired number of days
            if self._day_count > self.num_days:
                raise StopIteration

        return self.files.popleft()


class PadFileProcess(object):

    def __init__(self, label):
        self.count = 0
        self.label = label

    def __str__(self):
        return '%s, count = %d' % (self.label, self.count)

    def process_file(self, pad_file):
        self.count += 1


class PadFilePsd(PadFileProcess):

    def save_config(self, file1):
        print('do something special with very first file & call process_file too')
        data = padread(file1)
        # TODO get label, deltaf (to get freqs), nfft, etc. into config file for this labeled data set

    def process_file(self, pad_file, fs, nfft):
        super().process_file(pad_file)
        # return os.stat(pad_file).st_size // 16 // nmax

        y = padread(pad_file)[:, 2]  # indexing here gives JUST Y-AXIS
        n = nfft * (len(y) // nfft)
        y = y[:n]  # y gets truncated after an integer multiple of nfft pts

        f, pyy = my_psd(y, fs, nfft)
        return pyy


class PadFileIntRms(PadFileProcess):

    def process_file(self, pad_file, int_pts, olap_pts):
        super().process_file(pad_file)
        # return os.stat(pad_file).st_size // 16 // nmax

        y = padread(pad_file)[:, 2]  # indexing here gives JUST Y-AXIS
        n = int_pts * (len(y) // int_pts)
        y = y[:n]  # y gets truncated after an integer multiple of nfft pts

        t, arms = my_int_rms(y, fs, int_pts)
        return t, arms


nfft = 8192
nmax = 8192 * 4
nover = nfft//2

sensor = '121f03006'
# fs, fc = 500.0, 200.0
# min_bytes = 2.3 * 1024 * 1024  # bytes in 5 min = 5(16B/rec)(500rec/sec)(60sec/1min)/1024/1024 = 2.28 MB
fs, fc = 142.0, 6.0
min_bytes = 0.7 * 1024 * 1024  # bytes in 5 min = 5(16B/rec)(142rec/sec)(60sec/1min)/1024/1024 = 0.65 MB
ffp = FileFilterPipeline(HeaderMatchesSensorRateCutoffPad(sensor, fs, fc), BigFile(min_bytes=min_bytes))
# top_dir = os.sep.join(['d:', 'pad'])
# top_dir = 'p:' + os.sep
top_dir = '/misc/yoda/pub/pad'
start_date = date(2020, 3, 1)
num_days = 2 # 120

# create iterator
pfi = PadFilesIterator(sensor, start_date, num_days, reverse=False, top=top_dir, ffp=ffp)

for i, f in enumerate(pfi):
    print(i, f)

raise SystemExit

# pad_file = next(pfi)
# data = padread(pad_file)
# print(data.shape)
# y = data[:, 2]
# print(len(y))
# f, pyy = my_rolling_psd(y, fs, nfft)

# process per pad file
pfp = PadFilePsd('daily_psd')
for i, f in enumerate(pfi):
    # special handling for first file only
    if i == 0:
        pfp.save_config(f)
    pyy = pfp.process_file(f, fs, nfft)
    print(pfp, f, pyy.shape)
