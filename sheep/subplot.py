#!/usr/bin/env python

"""Example illustrating the use of plt.subplots().

This function creates a figure and a grid of subplots with a single call, while
providing reasonable control over how the individual plots are created.  For
very refined tuning of subplot creation, you can still use add_subplot()
directly on a new figure.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
from mpl_finance import candlestick_ohlc, quotes_historical_yahoo_ohlc

"""
EE_FIELD  maps2 VARNAME isa MTYPE
----------------------------------
SE 0 Temp X --> se0tempx    TEMPS
SE 0 Temp Y --> se0tempy    TEMPS
SE 0 Temp Z --> se0tempz    TEMPS
SE 0 +5V    --> se0p5v      VOLTS
HEAD 0 +15V --> se0p15v     VOLTS
HEAD 0 -15V --> se0n15v     VOLTS
SE 1 Temp X --> se1tempx    TEMPS
SE 1 Temp Y --> se1tempy    TEMPS
SE 1 Temp Z --> se1tempz    TEMPS
SE 1 +5V    --> se1p5v      VOLTS
HEAD 1 +15V --> se1p15v     VOLTS
HEAD 1 -15V --> se1n15v     VOLTS
Base Temp   --> basetemp    TEMPS
PC104 +5V   --> pc104p5v    VOLTS
Ref +5V     --> refp5v      VOLTS
Ref 0V      --> ref0v       VOLTS

"""


class FigureSet(object):
    
    def __init__(self, nrows, ncols, save_file):
        self.nrows = nrows
        self.ncols = ncols
        self.save_file = save_file
        self.figsize = (10, 7.5)
        self.dpi = 300
        self.fig, self.axarr = plt.subplots(nrows, ncols, sharex='col', sharey='row', figsize=self.figsize, dpi=self.dpi)
        self._get_format_info()
        
    def _get_format_info(self):
        self.mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
        self.alldays = DayLocator()                  # minor ticks on the days
        self.weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12

    def add_subplot(self, r, c, sub_results, title):
        
        self.axarr[r, c].xaxis.set_major_locator(self.mondays)
        self.axarr[r, c].xaxis.set_minor_locator(self.alldays)
        self.axarr[r, c].xaxis.set_major_formatter(self.weekFormatter)
        candlestick_ohlc(self.axarr[r, c], sub_results, width=0.6, colordown='b', colorup='r')
        
        if c == 0:
            self.axarr[r, c].set_ylabel('%d%d' % (r,c))
        if r == 0:
            self.axarr[r, c].set_title(title)
        
        # date axis and autoscale view
        self.axarr[r, c].xaxis_date()
        self.axarr[r, c].autoscale_view()
    
    def save(self):
        print 'writing', self.save_file
        self.fig.savefig(self.save_file, dpi=self.dpi, orientation='landscape', transparent=False)


class StatusHealthEePlot(object):
    
    def __init__(self, host, schema, table, file_prefix, num_days):
        self.host = host
        self.schema = schema
        self.table = table
        self.file_prefix = file_prefix
        self.num_days = num_days
        self.results = None
        
    def query(self):
        """fetch results, each record (row) is for a given EE and timestamp"""
        
        # FIXME results = samsquery.fetch_num_days(host, schema, d1, d2)
        
        # FIXME (Year, month, day) tuples suffice as args for quotes_historical_yahoo
        date1 = (2016, 12, 1)
        date2 = (2016, 12, 14)
                
        results = quotes_historical_yahoo_ohlc('DJIA', date1, date2)
        if len(results) == 0:
            print 'no results!?'
        
        # NOTE: for candlestick, results [quotes] is list of tuples: (utime, open, close, high, low, volume)
        # FIXME return query as list of tuples, where (for a given date)
        #       utime is unix time
        #       open is yesterday's median value
        #       close is today's median value
        #       high is today's max value
        #       low is today's min value
        #       volume is number of records for today
        self.results = results
    
    def plot(self, dtype):
        if len(self.results) == 0:
            print 'no results!?'
            
        if dtype == 'temps':
            nrows, ncols = 4, 7
        elif dtype == 'volts':
            nrows, ncols = 4, 9
        else:
            error('unrecognized data type identifier: %s' % dtype)

        plt.close('all')        
        save_file = self.file_prefix + dtype + '.png'
        figset = FigureSet(nrows, ncols, save_file)
        
        figset.fig.suptitle('%s for %d Days Starting on GMT %s' % (dtype.upper(), self.num_days, 'DAYONE'), fontsize=18)
        
        for r in range(nrows):
            for c in range(ncols):
                # FIXME how best to get this (r, c) subresults from uber query results?
                subresults = self.results
                figset.add_subplot(r, c, subresults, 'title')
            
        # make subplots a bit farther from each other
        # DEFAULTS ARE:
        # left  = 0.125  # the left side of the subplots of the figure
        # right = 0.9    # the right side of the subplots of the figure
        # bottom = 0.1   # the bottom of the subplots of the figure
        # top = 0.9      # the top of the subplots of the figure
        # wspace = 0.2   # the amount of width reserved for blank space between subplots,
        #                # expressed as a fraction of the average axis width
        # hspace = 0.2   # the amount of height reserved for white space between subplots,
                         # expressed as a fraction of the average axis height
        figset.fig.subplots_adjust(left=0.1, hspace=0.25, wspace=0.15)
        
        # hide x ticks for top plots and y ticks for right plots
        plt.setp([a.get_xticklabels() for a in figset.axarr[0, :]], visible=False)
        plt.setp([a.get_yticklabels() for a in figset.axarr[:, 1]], visible=False)
        plt.setp([a.get_xticklabels() for a in figset.axarr[-1, :]], rotation=45, horizontalalignment='right')
        
        figset.save()       


def main():
    
    # get parameters, mostly for query of samsmon.ee_packet on yoda
    host = 'yoda'
    schema = 'samsmon'
    table = 'ee_packet'
    file_prefix = '/tmp/fileprefix'
    num_days = 14
    
    sheep = StatusHealthEePlot(host, schema, table, file_prefix, num_days)
    sheep.query()

    sheep.plot('temps')
    sheep.plot('volts')
    
    return 0

if __name__ == '__main__':
    main()
