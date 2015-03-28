#!/usr/bin/env python

import numpy as np
#import matplotlib.pyplot as plt

# Sample rates (sa/sec) with index from filename "r" value
#   r = [      0,      1,     2,    3,   4,   5,   6,    7 ]
rates = [ 7.8125, 15.625, 31.25, 62.5, 125, 250, 500, 1000 ]

r = sys.argv[1]
fs = rates[r]
csvfile = '/home/pims/dev/matlab/programs/sams/2014_11_06_es07_freq_resp/frequency/fr_tshes-07_r' + str(r) + '_g0'

# load first 3 columns from csv file
d = np.genfromtxt(csvfile, delimiter=",")[:, 0:3]

# total time of the signal
T = len(d) / float(fs)  

# prepend time vector for entire signal
t = np.linspace(0, T, len(d), endpoint=False)
data = np.c_[ t, d ]

# demean each axis
#medians = np.median(data, axis=0)
#data_means = data.mean(axis=0)
#d = data - data_means[np.newaxis, :]

np.savetxt(csvfile + '.csv', data, delimiter=",")

#plt.plot( t, d[:,0] )
#plt.show()
