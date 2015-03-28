#!/usr/bin/env python

import os
import sys
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import datetime
from dateutil import parser
import numpy as np
import matplotlib.dates as dates
import mpl_toolkits.axes_grid.axes_size as Size
from mpl_toolkits.axes_grid import Divider
from matplotlib.dates import MonthLocator, DateFormatter

# parse GMT date strings for pandas dataframe
def dateparse(s):
    """parse GMT date strings for pandas dataframe"""
    try:
        d = pd.datetime.strptime(s, '%d-%b-%Y %H:%M:%S')
    except ValueError:
        d = pd.datetime.strptime(s, '%d-%b-%Y')
    return d

# return subset of dataframe matching input criteria
def filter_dataframe(df, dstart, dstop, include_sensors, include_axis, include_hours):
    """return subset of dataframe matching input criteria"""
    sensmask = df['sensor'].isin(include_sensors)
    axismask = df['axis'].isin(include_axis)
    hourmask = df['hour'].isin(include_hours)
    datemask = (df['GMT'] >= dstart) & (df['GMT'] < dstop)
    #return df[ (df['sensor'].isin(include_sensors)) & (df['axis'].isin(include_axis)) & (df['hour'].isin(include_hours)) ]
    return df[ sensmask & axismask & hourmask & datemask ]

# save figure
def my_savefig(plotdir, prefix, sensorstr, axisstr, hourstr, plottype):
    """save figure"""
    for ext in ['pdf', 'png']:
        outfile = os.path.join(plotdir, '_'.join([prefix, sensorstr, axisstr, hourstr]) + '_' + plottype + '.' + ext)
        plt.savefig( outfile )
        print 'saved figure %s' % outfile
    
# create 4 plots that match sensor, axis and hours criteria
def mode_one_plots(dfin, dstart, dstop, include_sensors, include_axis, include_hours, plotdir, daterange_prefix):
    
    df = filter_dataframe(dfin, dstart, dstop, include_sensors, include_axis, include_hours)    
    
    """create 4 plots that match sensor, axis and hours criteria"""
    
    # strings for filename output
    axisstr = ''.join(include_axis) + 'axis'
    hourstr = 'hours' + ''.join([ '%02d' % s for s in include_hours])
    
    # sensor abbrevs for filename output
    sensor_abbrevs = '+'.join([ x.replace('006', '')[-1] for x in include_sensors])
    sensorstr = 'sensors' + sensor_abbrevs.replace('+', '')
    
    xmin = df['median_frequencyHz'].min()
    xmax = df['median_frequencyHz'].max()
    ymin = df['median_ugRMS'].min()
    ymax = df['median_ugRMS'].max()
    
    ##################################################################################
    # scatter plot of median ugRMS vs. median frequency
    fig = plt.figure(1, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    plt.scatter(df['median_frequencyHz'], df['median_ugRMS'])
    plt.xlabel('Median Frequency (Hz)')
    plt.ylabel('Median RMS Acceleration (ug)')
    
    xmin, xmax = 0.06,  0.14
    ymin, ymax = 0.00, 10.00

    plt.axis([xmin, xmax, ymin, ymax])
    #plt.xticks(np.arange(0.05, 0.16, 0.01))

    # title
    sensors = [ x.replace('006','') for x in include_sensors]
    hours = ', '.join( ('%02d' % x) for x in include_hours )
    hours.rstrip(', ')
    titlestr = 'sensors = %s\n%s\naxis = %s; include 8-hour periods starting at hours: %s' % (sensor_abbrevs, daterange_prefix, include_axis, hours)
    plt.title(titlestr, fontsize=12)
    
    # save figure
    my_savefig(plotdir, daterange_prefix, sensorstr, axisstr, hourstr, 'rvf')
    plt.close(fig)
 
    ##################################################################################
    # hist2d plot of median ugRMS vs. median frequency
    fig = plt.figure(2, figsize=(8, 6), dpi=120, facecolor='w', edgecolor='k')
    nbins = 40.0
    xstep = (xmax - xmin) / nbins
    ystep = (ymax - ymin) / nbins
    xedges = np.arange(xmin, xmax + xstep, xstep)
    yedges = np.arange(ymin, ymax + ystep, ystep)
    plt.hist2d(df['median_frequencyHz'], df['median_ugRMS'], bins=[xedges, yedges]) #bins=40)
    plt.axis([xmin, xmax, ymin, ymax])
    
    # title
    plt.title(titlestr, fontsize=12)
    
    # axis labels
    plt.xlabel('Median Frequency (Hz)')
    plt.ylabel('Median RMS Acceleration (ug)')
    
    # axis limits
    #plt.axis([xmin, xmax, ymin, ymax])
    plt.axis([0.06, 0.14, 0.0, 10.0])
    #plt.xticks(np.arange(0.05, 0.16, 0.01))
    
    # colorbar
    cb = plt.colorbar()
    cb.set_label('counts')
    
    # set tickdir out because color obscures ticks
    ax = plt.gca()
    ax.xaxis.majorTicks[0]._apply_params(tickdir="out") 
    ax.yaxis.majorTicks[0]._apply_params(tickdir="out") 

    # save figure
    my_savefig(plotdir, daterange_prefix, sensorstr, axisstr, hourstr, 'rvfh')      
    plt.close(fig)
    
    # array of dates for time axis below
    t = [d.date() for d in df['GMT']]

    ##################################################################################
    # median ugRMS vs. time    
    fig = plt.figure(3, figsize=(16, 8), dpi=120, facecolor='w', edgecolor='k')
    plt.plot_date(t, df['median_ugRMS'])    
    plt.xlabel('GMT Date')
    plt.ylabel('Median RMS Acceleration (ug)')
    plt.gca().xaxis.set_major_formatter( dates.DateFormatter('%Y\n%m') )      
    plt.ylim([ymin, ymax])
    
    # title
    plt.title(titlestr, fontsize=12)
    
    # save figure
    my_savefig(plotdir, daterange_prefix, sensorstr, axisstr, hourstr, 'rvt')          
    plt.close(fig)
    
    ##################################################################################
    # hist2d plot of median ugRMS vs. time
    # every 6 months
    months = MonthLocator(range(1, 13), bymonthday=1, interval=6)
    monthsFmt = DateFormatter("%b %Y")
    fig = plt.figure(4, figsize=(16, 8), dpi=120, facecolor='w', edgecolor='k')
    
    tarr = np.array([ d.toordinal() for d in t])
    xmin, xmax = tarr.min(),  tarr.max()
    xstep = (xmax - xmin) / nbins
    ymin, ymax = 0.00, 10.00
    ystep = (ymax - ymin) / nbins
    xedges = np.arange(xmin, xmax + xstep, xstep)
    yedges = np.arange(ymin, ymax + ystep, ystep)    
    
    plt.hist2d(tarr, df['median_ugRMS'], bins=[xedges, yedges]) #bins=40)
    ax = plt.gca()
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    plt.xlabel('GMT Date')
    plt.ylabel('Median RMS Acceleration (ug)')
    plt.gca().xaxis.set_major_formatter( dates.DateFormatter('%Y\n%m') )      

    # colorbar
    cb = plt.colorbar()
    cb.set_label('counts')

    # set tickdir out because color obscures ticks
    ax = plt.gca()
    ax.xaxis.majorTicks[0]._apply_params(tickdir="out") 
    ax.yaxis.majorTicks[0]._apply_params(tickdir="out") 
    
    # title
    plt.title(titlestr, fontsize=12)
    
    # save figure
    my_savefig(plotdir, daterange_prefix, sensorstr, axisstr, hourstr, 'rvth')      
    plt.close(fig)
    
    ##################################################################################
    # median frequency vs. time    
    fig = plt.figure(5, figsize=(16, 8), dpi=120, facecolor='w', edgecolor='k')
    plt.plot_date(t, df['median_frequencyHz'])
    plt.xlabel('GMT Date')
    plt.ylabel('Median Frequency (Hz)')
    plt.gca().xaxis.set_major_formatter( dates.DateFormatter('%Y\n%m') )      

    ymin, ymax = 0.06,  0.14
    plt.ylim([ymin, ymax])
    
    # title
    plt.title(titlestr, fontsize=12)
    
    # save figure
    my_savefig(plotdir, daterange_prefix, sensorstr, axisstr, hourstr, 'fvt')          
    plt.close(fig)
    
    ##################################################################################
    # hist2d plot of median frequency vs. time
    fig = plt.figure(6, figsize=(16, 8), dpi=120, facecolor='w', edgecolor='k')

    ystep = (ymax - ymin) / nbins
    yedges = np.arange(ymin, ymax + ystep, ystep) 
    
    plt.hist2d(tarr, df['median_frequencyHz'], bins=[xedges, yedges]) #bins=40)
    ax = plt.gca()
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    plt.xlabel('GMT Date')
    plt.ylabel('Median Frequency (Hz)')
    plt.gca().xaxis.set_major_formatter( dates.DateFormatter('%Y\n%m') )      

    # colorbar
    cb = plt.colorbar()
    cb.set_label('counts')
    
    # set tickdir out because color obscures ticks
    ax = plt.gca()
    ax.xaxis.majorTicks[0]._apply_params(tickdir="out") 
    ax.yaxis.majorTicks[0]._apply_params(tickdir="out") 
    
    # title
    plt.title(titlestr, fontsize=12)
    
    # save figure
    my_savefig(plotdir, daterange_prefix, sensorstr, axisstr, hourstr, 'fvth')
    plt.close(fig)
    
    #plt.show()

def main(infile, dstart, dstop):
    
    # infile LIKE /misc/yoda/www/plots/user/mike/2011_04_01_to_2015_02_16_sensor_gmt_excelt_medfreq_medrms_cumulative.csv

    plotdir = '/misc/yoda/www/plots/user/mike/mode_one_plots'

    ## use date range from CSV filename as prefix
    #fname = os.path.basename(infile)
    #daterange_prefix = 'dates' + fname.split('_sensor')[0]
    
    # use date range from dstart to dstop
    daterange_prefix = 'dates' + dstart.strftime('%Y_%m_%d') + '_to_' + dstop.strftime('%Y_%m_%d')
    
    # read cumulative CSV infile into dataframe
    df = pd.read_csv(infile, parse_dates=['GMT'], date_parser=dateparse)

    # extract hour component so we can filter per 8-hour period
    df['hour'] = df.GMT.map( lambda x: pd.to_datetime(x).hour )
    
    # we will filter dataframe on: sensor(s), axis, and include_hours
    include_axis = ['s']
    include_hours = [8, 16]
    #include_sensors = ['121f02006', '121f03006', '121f04006', '121f05006', '121f08006', 'hirap006']
    include_sensors = ['121f03006', '121f04006', '121f05006', '121f08006']

     # create mode one plots
    mode_one_plots(df, dstart, dstop, include_sensors, include_axis, include_hours, plotdir, daterange_prefix)

    for s in include_sensors:
        mode_one_plots(df, dstart, dstop, [s], include_axis, include_hours, plotdir, daterange_prefix)

if __name__ == "__main__":
    infile = sys.argv[1]
    dstart = parser.parse(sys.argv[2])
    dstop = parser.parse(sys.argv[3])
    main(infile, dstart, dstop)
