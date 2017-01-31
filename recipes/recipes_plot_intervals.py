#!/usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator, MinuteLocator
import numpy as np
import datetime

def plotIntervalSet(fig, ax, yval, start, stop, color='k', lw=6):
    """ plot interval data """
    
    # Generate y values from scalar yval
    y = np.empty(len(start))
    y.fill(yval)   
    
    # Set current axes
    fig.sca(ax)
    
    # Plot horizontal lines
    hLines = plt.hlines(y, start, stop, color, lw=lw)

def getDemoData():
    """ example data """
    from StringIO import StringIO

    # a file-like object to read from via numpy
    a = StringIO("""
    a 2012-12-31/02:15:22 2012-12-31/22:15:30 OK
    b 2012-12-31/23:45:33 2013-01-01/11:05:40 OK
    c 2013-01-01/11:25:40 2013-01-01/19:44:55 OK
    """)
    
    # Converts str into a datetime object.
    conv = lambda s:datetime.datetime.strptime(s,'%Y-%m-%d/%H:%M:%S')
    
    # Use numpy to read the data in. 
    data = np.genfromtxt(a, converters={1: conv, 2: conv}, names=['caption','start','stop','state'], dtype=None)
    cap, start, stop = data['caption'], data['start'], data['stop']
    
    # Let's ignore "caption" and "state" for this example
    yval = 2
    return yval, start, stop

def showDemo():
    # Build y values from the number of start values
    yval, start, stop = getDemoData()

    # Init figure and axes
    fig = plt.figure( figsize=(20,12), dpi=80 )
    ax = fig.add_axes([0.075, 0.1, 0.85,  0.85]) 
    
    hLines2 = plotIntervalSet(fig, ax, 2, start, stop, color='b', lw=2)
    hLines3 = plotIntervalSet(fig, ax, 3, start, stop)
    
    # Set major x ticks every 4 hours
    ax.xaxis_date()
    ax.xaxis.set_major_locator( HourLocator( byhour=[ 0,  8, 16 ] ) )
    ax.xaxis.set_minor_locator( HourLocator( byhour=[ 4, 12, 20 ] ) )   
    ax.xaxis.set_major_formatter( DateFormatter('%H:%M\n%d-%b-%Y') )
    ax.xaxis.set_minor_formatter( DateFormatter('%H:%M') )    
    
    # To adjust the xlimits a timedelta is needed.
    delta = (stop.max()-start.min())/20
    ax.set_ylim([0, 5])
    ax.set_xlim([start.min()-delta, stop.max()+delta])
    xLabel = ax.set_xlabel('GMT (HH:MM)')
        
    ax.xaxis.grid(True,'minor')
    ax.xaxis.grid(True,'major',linewidth=2)
    
    plt.savefig('/tmp/trash.pdf')
    plt.show()
    
if __name__ == '__main__':
    showDemo()