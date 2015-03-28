#!/usr/bin/env python

from obspy.core import read
from obspy.core.stream import Stream
import matplotlib.pyplot as plt
import numpy as np

# Read in entire example file
stEntireFile = read('/home/pims/dev/programs/python/pims/sandbox/data/slist_for_example.ascii')

# Trace slicing
st = Stream()
tr = stEntireFile[0]
t1 = tr.stats.starttime
starts_stops = [
    (0, 1),
    (1.004, 2),
    ]
for start, stop in starts_stops:
    st += Stream(traces=[tr.slice(t1 + start, t1 + stop)])
st += Stream(traces=[tr.slice(t1 + stop + 0.004, tr.stats.endtime)])

# sort
st.sort(['starttime'])
# start time in plot equals 0
dt = st[0].stats.starttime.timestamp

# Go through the stream object, determine time range in julian seconds
# and plot the data with a shared x axis
nt = len(st)
ax = plt.subplot(nt + 1, 1, 1) # dummy for tying axis
for i in range(nt):
    plt.subplot(nt + 1, 1, i + 1, sharex=ax)
    t = np.linspace(st[i].stats.starttime.timestamp - dt,
                    st[i].stats.endtime.timestamp - dt,
                    st[i].stats.npts)
    plt.plot(t, st[i].data)

# Merge the data together and show plot in a similar way
st.merge(method=0)
print st
plt.subplot(nt + 1, 1, nt + 1, sharex=ax)
t = np.linspace(st[0].stats.starttime.timestamp - dt,
                st[0].stats.endtime.timestamp - dt,
                st[0].stats.npts)
plt.plot(t, st[0].data, 'r')
plt.show()