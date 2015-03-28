#!/usr/bin/env python

from scipy import signal
from numpy import arange, cos, pi
from numpy import random
import pylab as p

FS = 1000.0                                          # sampling rate
FC = 0.05/(0.5*FS)                                   # cutoff frequency at 0.05 Hz
N = 1001                                             # number of filter taps (order)
a = 1                                                # filter denominator
b = signal.firwin(N, cutoff=FC, window='hanning')    # filter numerator

M = FS*60                                            # number of samples (60 seconds)
n = arange(M)                                        # time index
x1 = cos(2*pi*n*0.025/FS)                            # signal at 0.025 Hz
x = x1 + 2*random.rand(M)                            # signal + noise
y = signal.lfilter(b, a, x)                          # filtered output

p.plot(n/FS, x); p.plot(n/FS, y, 'r', lw=2)          # output in red
p.grid()
p.show()