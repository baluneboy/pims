#!/usr/bin/env python

import numpy as np
from matplotlib import pyplot
from ugaudio.load import padread

filename = '/misc/yoda/pub/pad/year2016/month05/day22/sams2_accel_121f05/2016_05_22_00_04_41.047+2016_05_22_00_14_41.057.121f05'

# read data from file (not using double type here like MATLAB would, so we get courser demeaning)
B = padread(filename)

# demean each column
A = B - B.mean(axis=0)

print '{0:s},{1:>.4e},{2:>.4e},{3:>.4e},{4:>.4e},{5:>.4e},{6:>.4e}'.format(filename,
                                   A.min(axis=0)[1], A.max(axis=0)[1], A.min(axis=0)[2],
                                   A.max(axis=0)[2], A.min(axis=0)[3], A.max(axis=0)[3] )

## FIXME these bins will come by doing some homework for say the past umpteen years (all 200 Hz SAMS data)
#bins = np.linspace(-1e-3, 1e-3, 100)
#
###pyplot.hist(A[:,1], bins, alpha=0.3, label='x')
###pyplot.hist(A[:,2], bins, alpha=0.3, label='y')
###pyplot.hist(A[:,3], bins, alpha=0.3, label='z')
###pyplot.legend(loc='upper right')
###pyplot.show()
#
#Nx, Bx, Px = pyplot.hist(A[:,1], bins)
#Ny, By, Py = pyplot.hist(A[:,2], bins)
#Nz, Bz, Pz = pyplot.hist(A[:,3], bins)
