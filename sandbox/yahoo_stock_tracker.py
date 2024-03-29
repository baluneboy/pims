#!/usr/bin/env python

import datetime
import numpy as np
from dateutil import parser

import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.dates

from yahoo_finance import Share


# a generator to get dates between start_date and day before end_date
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

#start_date = datetime.date(2013, 1, 1)
#end_date = datetime.date(2014, 1, 1)
#for date in daterange(start_date, end_date):
#    print date.strftime("%Y-%m-%d")

s = Share('SNXFX')
h = s.get_historical('2015-01-01','2016-08-08')
t = [ (d['Adj_Close'], parser.parse(d['Date'])) for d in h ]
p = sorted(t, key=lambda x: x[1])
print p[-3:]
    
raise SystemExit

def demo1():
    # Generate dummy data
    nd = nextFiveMinutes()
    num = 38
    some_dates = [nd.next() for i in range(0,num)] #get 20 dates
    y_values = [random.randint(1,100) for i in range(0,num)] # get dummy y data
    
    # Figure and axis objects
    fig = plt.figure(figsize=(16,9), dpi=100)
    ax = fig.gca()
    
    # Plotting goes here ...
    h = ax.plot_date(some_dates, y_values, 'b.-')[0]
    print h
    ax.set_xlabel('GMT (hh:mm)')
    
    # Set major x ticks every 15 minutes
    ax.xaxis.set_major_locator( matplotlib.dates.MinuteLocator(byminute=[0, 30, 60]) )
    ax.xaxis.set_minor_locator( matplotlib.dates.MinuteLocator(byminute=[15, 45]) )
    ax.xaxis.set_major_formatter( matplotlib.dates.DateFormatter('%H:%M\n%d-%b-%Y') )
    ax.xaxis.set_minor_formatter( matplotlib.dates.DateFormatter('%H:%M') )
    
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

def demo2():
    # Figure and axis objects
    fig = plt.figure(figsize=(16,9), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_axis_bgcolor('white')
    
    x = np.array([unix2dtm(u) for u in [
        UTCDateTime(2012, 10, 19, 10, 0,  0),
        UTCDateTime(2012, 10, 19, 11, 3, 0),
        UTCDateTime(2012, 10, 19, 12, 6, 0),
        UTCDateTime(2012, 10, 19, 13, 9, 0)] ])
    y = np.array([1, 3, 4, 2])
    
    # Plotting goes here ...
    h = ax.plot_date(x, y, 'b.-')[0]
    ax.set_xlabel('GMT (hh:mm)')
    
    # Set major x ticks every 30 minutes, minor every 15 minutes
    ax.xaxis.set_major_locator( matplotlib.dates.MinuteLocator(byminute=[0, 30, 60]) )
    ax.xaxis.set_minor_locator( matplotlib.dates.MinuteLocator(byminute=[15, 45]) )
    ax.xaxis.set_major_formatter( matplotlib.dates.DateFormatter('%H:%M\n%d-%b-%Y') )
    ax.xaxis.set_minor_formatter( matplotlib.dates.DateFormatter('%H:%M') )

    xmin, xmax = plt.xlim()    
    plt.xlim( xmin + (20.0/1440.0), xmax )
    
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

def demo3():
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
    y = np.zeros(x.shape)    
    
    # Plotting goes here ...
    h = ax.plot_date(x, y, 'b.-')[0]
    ax.set_xlabel('GMT (hh:mm)')
    
    # Set major x ticks every 30 minutes, minor every 15 minutes
    ax.xaxis.set_major_locator( matplotlib.dates.MinuteLocator(interval=2) )
    ax.xaxis.set_minor_locator( matplotlib.dates.MinuteLocator(interval=1) )
    ax.xaxis.set_major_formatter( matplotlib.dates.DateFormatter('%H:%M:%S\n%d-%b-%Y') )
    ax.xaxis.set_minor_formatter( matplotlib.dates.DateFormatter('%H:%M:%S') )

    xmin, xmax = plt.xlim()    
    print xmin, xmax
    
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
    demo3()