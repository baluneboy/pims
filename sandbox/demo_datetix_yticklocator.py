#!/usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.dates
from pims.gui.pimsticker import CushionedLinearLocator
from matplotlib.ticker import FormatStrFormatter
import datetime
import random
from obspy.core.utcdatetime import UTCDateTime
from pims.utils.pimsdateutil import unix2dtm
import numpy as np

# A generator to get datetimes (every 5 minutes start on 31-Dec-2012)
def nextFiveMinutes():
    #dtm = datetime.datetime(2012, 12, 31, 22, 0, 0) - datetime.timedelta(minutes=5)
    dtm = UTCDateTime(2012, 12, 31, 22, 0, 0) - datetime.timedelta(minutes=5)
    while 1:
        dtm += datetime.timedelta(minutes=5)
        #yield (dtm)
        yield ( datetime.datetime( *dtm.timetuple()[0:-2] ) )

def demo():
    # Figure and axis objects
    fig = plt.figure(figsize=(16,9), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_axis_bgcolor('white')
    
    x = np.array([unix2dtm(u) for u in [
        UTCDateTime(2013, 12, 31, 23, 56, 0),
        UTCDateTime(2013, 12, 31, 23, 58, 0),
        UTCDateTime(2014,  1,  1,  0,  0, 0),
        UTCDateTime(2014,  1,  1,  0,  2, 0),
        UTCDateTime(2014,  1,  1,  0,  4, 0),
        UTCDateTime(2014,  1,  1,  0,  6, 0)] ])
    y = np.array(range(len(x)))
    #y = y - 3
    
    # Plotting goes here ...
    h = ax.plot_date(x, y, 'b.-')[0]
    ax.set_xlabel('GMT (hh:mm)')
    
    # Set major x ticks every 30 minutes, minor every 15 minutes
    ax.xaxis.set_major_locator( matplotlib.dates.MinuteLocator(interval=2) )
    ax.xaxis.set_minor_locator( matplotlib.dates.MinuteLocator(interval=1) )
    ax.xaxis.set_major_formatter( matplotlib.dates.DateFormatter('%H:%M:%S\n%d-%b-%Y') )
    ax.xaxis.set_minor_formatter( matplotlib.dates.DateFormatter('%H:%M:%S') )

    # Set major y ticks "smartly"
    ytick_locator = CushionedLinearLocator()
    #ytick_locator = PositiveLinearLocator()
    ytick_formatter = FormatStrFormatter('%g')
    ax.yaxis.set_major_locator( ytick_locator )
    ax.yaxis.set_major_formatter( ytick_formatter )
    
    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()
    plt.ylim(-0.1, 5)
    
    # Make tick_params more suitable to your liking...
    plt.tick_params(axis='both', which='both', width=2, direction='out')
    # tick_params for x-axis
    plt.tick_params(axis='x', which='major', labelsize=12, length=8)
    plt.tick_params(axis='x', which='minor', labelsize=12)
    plt.tick_params(axis='x', which='minor', length=6, colors='gray')
    # tick_params for y-axis
    plt.tick_params(axis='y', which='both', labelsize=12)
    plt.tick_params(right=True, labelright=True)
    plt.show()

if __name__ == "__main__":
    demo()