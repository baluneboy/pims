"""
Graphical user interface (gui) code...
keep it simple!
"""

import numpy as np
from obspy import UTCDateTime
from pims.utils.pimsdateutil import unix2dtm

DUMMYDATA = {}
x = np.array([unix2dtm(u) for u in [
    UTCDateTime(2013, 12, 31, 23, 57, 0),
    UTCDateTime(2013, 12, 31, 23, 58, 0),
    UTCDateTime(2013, 12, 31, 23, 59, 0),
    UTCDateTime(2014,  1,  1,  0,  0, 0),
    UTCDateTime(2014,  1,  1,  0,  1, 0),
    UTCDateTime(2014,  1,  1,  0,  2, 0),
    UTCDateTime(2014,  1,  1,  0,  3, 0)] ])
y = np.array(range(len(x)), dtype='float')
y[3] = np.nan
DUMMYDATA['x'] = x
DUMMYDATA['y'] = y

