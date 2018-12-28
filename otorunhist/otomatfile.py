#!/usr/bin/env python

"""Get/check parameters related to histograms for OTOB grms values (per-axis and RSS).

This module provides classes for handling parameters needed for running histogram(s) of OTOB grms values..

"""

import numpy as np
import scipy.io as sio


class OtoParamFileException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class C(object):

    def __init__(self):
        self._x = None

    @property
    def x(self):
        """I'm the 'x' property."""
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @x.deleter
    def x(self):
        del self._x


class MyClass(object):
    def __init__(self):
        self._freqs = None

    # getter
    @property
    def freqs(self):
        if self._freqs is None:
            v = sio.loadmat(self.oto_mat_file, variable_names=['foto'])
            self._freqs = v['foto']
        return self._freqs

    freqs = property(freqs, None)  # only getter, no setter


class OtoMatFile(object):
    """
    This is a class for operating with OTO band mat file data.

    Attributes:
        oto_mat_file (str): The OTO mat file that we get OTO values from.
        data (dict): The dict we get array and other OTO values from.
    """

    def __init__(self, oto_mat_file):
        self.oto_mat_file = oto_mat_file
        self.data = self._get_data()

    def _get_data(self):
        try:
            v = sio.loadmat(self.oto_mat_file)
        except Exception:
            print 'FILE IS %s' % self.oto_mat_file
            raise OtoParamFileException('could not read a from oto mat file')
        return v

    def __eq__(self, other):
        """return True if self's a['foto'] array equals that of other for these 2 objects"""
        if isinstance(other, OtoMatFile):
            return np.array_equal(self.data['foto'], other.data['foto'])
        return False

    def __ne__(self, other):
        """return True if self's a['foto'] array NOT equal to that of other for these 2 objects"""
        return not self.__eq__(other)

    def __str__(self):
        s = self.__class__.__name__
        s += ' %s' % self.oto_mat_file
        s += ' has {:d} frequency bands'.format(len(self.data['foto']))
        return s


def demo():
    try:
        f1 = '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/day01/sams2_accel_121f03/2016_01_01_00_01_58.751+2016_01_01_00_11_58.755.121f03.mat'
        op1 = OtoMatFile(f1)
        f2 = '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/day01/sams2_accel_121f03/2016_01_01_03_38_12.716-2016_01_01_03_48_12.717.121f03.mat'
        op2 = OtoMatFile(f2)

        print op1 == op2

    except OtoParamFileException:
        print 'an exception'

    else:
        print 'no exceptions'

    finally:
        print 'finally, regardless of exception or not'

# demo()
