#!/usr/bin/env python

import math


def round2ten(a):
    """return value rounded to multiple of ten"""
    return int(round(a, -1))


def round_down(x, m):
    """return value of x rounded down to multiple of m"""    
    return x - (x%m)


def round_up(x, m):
    """return value of x rounded up to multiple of m"""        
    return (int(math.floor(x / m)) + 1) * m


def demo_round2ten():
    for v in range(65740, 65860, 10):
        print v / 10.0, round2ten(v/10.0)


def demo_numpy_array_append_rows(sensor, y, m, d):
    import glob
    import datetime
    import numpy as np
    from ugaudio.load import pad_read
    from pims.utils.pimsdateutil import datetime_to_ymd_path
    ymd_dir = datetime_to_ymd_path(datetime.date(y, m, d))
    glob_pat = '%s/*_accel_%s/*%s' % (ymd_dir, sensor, sensor)
    fnames = glob.glob(glob_pat)
    arr = np.empty((0, 5), dtype=np.float32)    # float32 matches what we read from PAD file
    for fname in fnames[:3]:
        # read data from file (not using double type here like MATLAB would, so we get courser demeaning)
        a = pad_read(fname)
        a[:,1:4] = a[:,1:4] - a[:,1:4].mean(axis=0)  # demean x, y and z columns
        v = np.array( np.sqrt(a[:,1]**2 + a[:,2]**2 + a[:,3]**2) )  # compute vector magnitude
        #new_col = np.reshape(v, (-1, 1))
        ncols = 1
        v.shape = (v.size//ncols, ncols)
        #print v.shape, a.shape
        a = np.append(a, v, axis=1) # append to get 5th column for vecmag
        #print v.shape, a.shape
        arr = np.append(arr, a, axis=0)
        #print arr.shape        
    
    return arr    


if __name__ == '__main__':
    arr = demo_numpy_array_append_rows('121f03006', 2017, 11, 1)
    print arr
