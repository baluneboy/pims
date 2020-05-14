import os
from datetime import timedelta, date
from collections import deque
from pathlib import Path

from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.files.filter_pipeline import FileFilterPipeline, HeaderMatchesSensorRateCutoffPad, BigFile


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


sensor = '121f02'
fs, fc = 500.0, 200.0
min_bytes = 2.3 * 1024 * 1024  # bytes in 5 min = 5(16B/rec)(500rec/sec)(60sec/1min) = 2.28 MB
ffp = FileFilterPipeline(HeaderMatchesSensorRateCutoffPad(sensor, fs, fc), BigFile(min_bytes=min_bytes))
top_dir = os.sep.join(['d:', 'pad'])
start_date = date(2020, 4, 1)
num_days = 77

# create iterator
pfi = PadFilesIterator(sensor, start_date, num_days, reverse=False, top=top_dir, ffp=ffp)

file_count = 0
for f in pfi:
    file_count += 1
    print(file_count, f)
