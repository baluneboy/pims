# -*- coding: utf-8 -*-
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
import datetime
from pathlib import Path
from pims.pad.mendmore import to_dtm, CountEndtime
from pims.pad.pad_chunks import PadGap
from pims.pad.pad_groups import PadFileGroups
from ugaudio.load import sams_pad_read


class PadRaw(object):

    """A metadata object to represent collection of PAD files (groups) and gaps.

    This is a cohesive collection of PAD file groups interleaved with gaps...
    BUT no nudging of times though, so use derived class, Pad (see below), instead.
    """

    def __init__(self, sensor, start, stop=None, pathstr='/misc/yoda/pub/pad', rate=500.0):
        self._sensor = sensor
        self._start = start if isinstance(start, datetime.datetime) else to_dtm(start)

        # set duration to one day if stop is None
        if stop is None:
            stop = self._start + datetime.timedelta(days=1)
        self._stop = stop if isinstance(stop, datetime.datetime) else to_dtm(stop)

        # make sure we don't have zero span
        if self._start >= self._stop:
            raise Exception('in %s, start time must be before stop time' % self.__class__.__name__)

        self._pathstr = pathstr
        self._rate = rate
        self._groups = self._get_groups()

    def __str__(self):
        start_str = self._start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        stop_str = self._stop.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        s = '%s: %s from %s to %s (fs=%.2f)' % (self.__class__.__name__, self._sensor, start_str, stop_str, self._rate)
        return s

    def show_groups(self):
        for i, g in enumerate(self._groups):
            print('%03d' % i, g, end='')
            if 'PadGap' == g.__class__.__name__:
                print(' --- gap ---')
            else:
                print('')

    @property
    def sensor(self):
        """return string for sensor"""
        return self._sensor

    @property
    def start(self):
        """return start time for this group"""
        return self._start

    @property
    def stop(self):
        """return stop time for this group"""
        return self._stop

    @property
    def pathstr(self):
        """return string for top of PAD path"""
        return self._pathstr

    @property
    def rate(self):
        """return float for data rate (sa/sec)"""
        return self._rate

    @property
    def groups(self):
        """return list of PadGroup objects"""
        return self._groups

    def _get_groups(self):
        """call PadFileGroups and use times to interleave gaps between them"""
        delta_t = datetime.timedelta(seconds=1.0/self._rate)
        pad_groups = PadFileGroups(self._sensor, self._start, stop=self._stop, pth=self._pathstr, rate=self._rate)
        # print('<--', self.sensor, '-->', pad_groups)
        # runs = pad_groups.get_file_group_runs()
        # print(sensor, sum(runs), runs)
        grps = []
        prev_grp = None
        for i, grp in enumerate(pad_groups):
            if prev_grp is not None:
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
                grps.append(gap)
                # print(prefix, gap, suffix)
            grps.append(grp)
            # print('%03d' % i, grp)
            prev_grp = grp
        # print('+' * 55)
        return grps


class Pad(PadRaw):

    """A metadata object that facilitates reading/processing of SAMS data.

    This is an extension of PadRaw functionality but with nudging to get all times on step.
    """

    def __init__(self, sensor, start, stop=None, pathstr='/misc/yoda/pub/pad', rate=500.0):
        PadRaw.__init__(self, sensor, start, stop=stop, pathstr=pathstr, rate=rate)
        self._nudge_groups()
        self._start_ind = self._get_ind_start()
        self._stop_ind = self._get_ind_stop()

    def _nudge_groups(self):
        """based on start time of first group, nudge subsequent group start/stop times (max of one time step)"""
        t_step = 1.0 / self._rate
        last_time = None
        for g in self._groups:
            if last_time is None:
                last_time = g.stop
                # print('grp:', g)
                continue
            grp_step = (g.start - last_time).total_seconds()
            num_steps = grp_step / t_step
            nudged_num_steps = int(num_steps)
            nudged_grp_step = nudged_num_steps * t_step
            new_g_start = last_time + datetime.timedelta(seconds=nudged_grp_step)
            g.start = new_g_start  # the setter method will nudge entire group in lockstep
            # print("grp:", g)
            last_time = g.stop

    @property
    def start_ind(self):
        """return integer which is index into first group to get actual (floor) start time"""
        return self._start_ind

    @property
    def stop_ind(self):
        """return integer which is index into last group to get actual (ceil) stop time"""
        return self._stop_ind

    def _get_ind(self, i_group, i_file, t2, math_fun):
        # FIXME should next line reference df or should it be group metadata's start attribute?
        t1 = self._groups[i_group].df.iloc[i_file].Start
        delta_sec = (t2 - t1).total_seconds()
        pts = self._rate * delta_sec
        return math_fun(pts)

    def _get_ind_start(self):
        ind_grp, ind_file, t2 = 0, 0, self._start
        i_start = self._get_ind(ind_grp, ind_file, t2, math.floor)
        return max([i_start, 0])

    def _get_ind_stop(self):
        ind_grp, ind_file, t2 = -1, 0, self._stop
        i_stop = self._get_ind(ind_grp, ind_file, t2, math.ceil)
        return min([i_stop, (self._groups[-1].samples-1)])


class SamsShow(object):

    """Iterator over Pad object to describe SAMS data chunks."""

    def __init__(self, pad, size, fun, verbose=False):
        self.pad = pad
        self.size = size
        self.fun = fun
        self.verbose = verbose

    def __str__(self):
        s = ''
        for i, g in enumerate(self.pad.groups):
            if i == 0 and self.verbose:
                s = 'FIRST GROUP'
                first_grp_start = self.pad.groups[0].df.iloc[0].Start
                actual_start = first_grp_start + datetime.timedelta(seconds=self.pad.start_ind/self.pad.rate)
                delta_time = actual_start - first_grp_start
                s += '\nBEG %s = first grp start' % first_grp_start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                s += '\nBEG %s = desired start' % self.pad.start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                s += '\nBEG %s = actual start (ind = %d) <-- %s into first group\n' %\
                     (actual_start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], self.pad.start_ind, delta_time)

                s += '\nGrp GroupStart                 GroupStopCalc            Duration'
                s += '                         NumPts    NumFiles'

            s += '\n%03d %s' % (i, g)

            if i == len(self.pad.groups) - 1 and self.verbose:
                s += '\n\nLAST GROUP'
                last_grp_start = self.pad.groups[-1].start
                delta_time = datetime.timedelta(seconds=self.pad.stop_ind/self.pad.rate)
                actual_stop = last_grp_start + delta_time
                s += '\nEND %s = last grp start' % self.pad.groups[-1].start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                s += '\nEND %s = desired stop' % self.pad.stop.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                s += '\nEND %s = actual stop (ind = %d) <-- %s into last group' % \
                     (actual_stop.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], self.pad.stop_ind, delta_time)

        return s.lstrip('\n')

    def run(self):

        # use metadata for one-hour data array creation
        num_pts = int(self.pad.rate * 60 * 60)
        print("num_pts", num_pts)

        # setup empty buffer to hold xyz array for one hour
        xyz = np.empty((num_pts, 3))  # this will contain garbage values
        xyz[:] = np.NaN  # replace garbage values with NaN

        xyz_row = 0
        t1 = self.pad.groups[0].start + datetime.timedelta(seconds=self.pad.start_ind / self.pad.rate)
        cet = CountEndtime(t1, self.pad.rate)

        for ind_grp, g in enumerate(self.pad.groups):
            if 'PadGap' == g.__class__.__name__:
                print("ind_grp =", ind_grp, "is a gap")
                cet += g.samples
                print('{:84s} {:7d} of {:7d} pts [n = {:9d} pts, end {}]'.
                      format(' <------- gap ------->',
                             g.samples, g.samples, cet.count, cet.end.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]))
                xyz_row = cet.count
                print("xyz_row", xyz_row)
            else:
                count_pts = self.pad.stop_ind + 1
                for ind_file, row in g.df.iterrows():
                    print("ind_grp =", ind_grp, "ind_file =", ind_file)
                    i1 = 0
                    if row['Start'] <= self.pad.start <= row['Stop']:
                        i1 = self.pad.start_ind
                    i2 = row['Samples'] - 1
                    if ind_grp == len(self.pad.groups) - 1:
                        if count_pts < row['Samples']:
                            i2 = count_pts - 1
                        count_pts -= row['Samples']
                    cet += (i2 - i1) + 1
                    fname = Path(row['Parent'], row['Filename'])
                    if (i2-i1) + 1 == row['Samples']:
                        count_rows = -1
                    else:
                        count_rows = (i2-i1) + 1
                    arr = sams_pad_read(fname, offset_rows=i1, count_rows=count_rows)
                    end_row = np.min([xyz.shape[0], cet.count])
                    xyz[xyz_row:end_row, :] = arr
                    print('file {}, inds=[{:7d} {:7d}], {:7d} of {:7d} pts [n = {:9d} pts, end {}]'.
                          format(row['Filename'], i1, i2, (i2-i1) + 1, row['Samples'], cet.count,
                                 cet.end.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]))
                    xyz_row = cet.count
                    print("xyz_row", xyz_row)
        print(xyz)


if __name__ == '__main__':

    # day, sensors, pathstr = '2020-04-07', ['121f02', '121f03', '121f04', '121f05', '121f08'], '/misc/yoda/pub/pad'
    # day, sensors, pathstr = '2020-04-06', ['121f02', '121f03', '121f04', '121f05', '121f08'], 'G:/data/pad'
    # day, sensors, pathstr = '2020-04-02', ['121f02', '121f03'], '/home/pims/data/pad'
    rate = 500.0
    # demo_pad_file_day_groups(day, sensors, pathstr=pathstr, rate=rate)
    # start, stop, sensors, pathstr = '2020-04-02 00:00:00.000', None, ['121f03', ], '/home/pims/data/pad'
    # start, stop, sensors, pathstr = '2020-04-06 00:06:00.211', '2020-04-06 00:06:03.206', ['121f03', ], 'G:/data/dummy_pad'
    start, stop, sensors, pathstr = '2020-04-06 00:00:00', '2020-04-06 01:00:00', ['121f03', ], '/home/pims/data/dummy_pad'
    # start, stop, sensors, pathstr = '2020-04-04 00:00:00', '2020-04-04 01:00:00', ['121f03', ], '/misc/yoda/pub/pad'
    # demo_pad_file_groups(start, stop, sensors, pathstr=pathstr, rate=rate)

    p = Pad(sensors[0], start, stop, pathstr=pathstr, rate=rate)

    size = 500
    fun = print
    ss = SamsShow(p, size, fun, verbose=True)
    print('=' * 108)
    print(ss)
    print('=' * 108)
    ss.run()
