#!/usr/bin/env python

from obspy.core import read
from obspy.core.stream import Stream
import matplotlib.pyplot as plt
import numpy as np

# Read in all files starting with dis.
##st1 = read("http://examples.obspy.org/dis.G.SCZ.__.BHE")
##st2 = read("http://examples.obspy.org/dis.G.SCZ.__.BHE.1")
##st3 = read("http://examples.obspy.org/dis.G.SCZ.__.BHE.2")
##st1.write('/misc/yoda/tmp/stream1.mseed', format='MSEED')
##st2.write('/misc/yoda/tmp/stream2.mseed', format='MSEED')
##st3.write('/misc/yoda/tmp/stream3.mseed', format='MSEED')
##raise SystemExit
st1 = read('/misc/yoda/tmp/stream1.mseed')
st2 = read('/misc/yoda/tmp/stream2.mseed')
st3 = read('/misc/yoda/tmp/stream3.mseed')
#st = st1 + st2 + st3

# Introduce some gaps
st = Stream()
tr = st1[0]
t1 = tr.stats.starttime
starts_stops = [
    (0, 1000),
    (1020, 3250),
    (3300, 3600),
    (3610, 3678),
    ]
for start, stop in starts_stops:
    st += Stream(traces=[tr.slice(t1 + start, t1 + stop)])
st += Stream(traces=[tr.slice(t1 + stop + 20, tr.stats.endtime)])

# sort
st.sort(['starttime'])
# start time in plot equals 0
dt = st[0].stats.starttime.timestamp

# Go through the stream object, determine time range in julian seconds
# and plot the data with a shared x axis
nt = len(st)
ax = plt.subplot(nt + 1, 1, 1)  # dummy for tying axis
for i in range(nt):
    plt.subplot(nt + 1, 1, i + 1, sharex=ax)
    t = np.linspace(st[i].stats.starttime.timestamp - dt,
                    st[i].stats.endtime.timestamp - dt,
                    st[i].stats.npts)
    plt.plot(t, st[i].data)

# Merge the data together and show plot in a similar way
st.merge(method=1)
plt.subplot(nt + 1, 1, nt + 1, sharex=ax)
t = np.linspace(st[0].stats.starttime.timestamp - dt,
                st[0].stats.endtime.timestamp - dt,
                st[0].stats.npts)
plt.plot(t, st[0].data, 'r')
plt.show()