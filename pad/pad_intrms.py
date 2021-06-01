#!/usr/bin/env python3

import numpy as np


def interval_rms(arr, n, overlap=-1, demean=True):
    """return columnwise interval RMS for multi-column array, arr;  n is interval size [optional overlap]"""
    def _int_rms(x, num):
        x2 = np.power(x, 2)
        window = np.ones(num) / float(num)
        return np.sqrt(np.convolve(x2, window, 'valid'))
    if n > arr.shape[0]:
        raise Exception('too many interval points chosen for interval RMS')
    if demean:
        m = arr.mean(axis=0)
        arr = arr - m[np.newaxis, :]
    irms = np.apply_along_axis(func1d=_int_rms, axis=0, arr=arr, num=n)
    if overlap == -1:
        return irms
    every_nth = n - overlap
    return irms[::every_nth]


xyz = np.array(range(36)).reshape(-1, 3)

# demean
mm = xyz.mean(axis=0)
xyz = xyz - mm[np.newaxis, :]

npts, noverlap = 8, 3
int_rms = interval_rms(xyz, npts, overlap=noverlap)
print(xyz)
print(interval_rms(xyz, npts))
print(int_rms)
