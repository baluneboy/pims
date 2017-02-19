#!/usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
from mpl_finance import candlestick_ohlc, quotes_historical_yahoo_ohlc
from subplot_volts import FigureVolts

def demo_try():
    # (Year, month, day) tuples suffice as args for quotes_historical_yahoo
    date1 = (2016, 12, 5)
    date2 = (2016, 12, 15)
    
    mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
    alldays = DayLocator()                  # minor ticks on the days
    weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
    dayFormatter = DateFormatter('%b %d')   # e.g., 12
    
    quotes = quotes_historical_yahoo_ohlc('DJIA', date1, date2)
    if len(quotes) == 0:
        print 'no quotes!?'
        raise SystemExit
    
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)
    #ax.xaxis.set_minor_formatter(dayFormatter)
    
    # TODO does finance have anything in plot_day_summary we can use?
    
    # simple OHLC candlestick
    candlestick_ohlc(ax, quotes, width=0.6, colordown='b', colorup='r')
    
    ax.xaxis_date()
    ax.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    
    plt.show()

def demo_serious():
    
    # (Year, month, day) tuples suffice as args for quotes_historical_yahoo
    date1 = (2016, 12, 5)
    date2 = (2016, 12, 15)
    
    mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
    alldays = DayLocator()                  # minor ticks on the days
    weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
    dayFormatter = DateFormatter('%b %d')   # e.g., 12
    
    quotes = quotes_historical_yahoo_ohlc('DJIA', date1, date2)
    if len(quotes) == 0:
        print 'no quotes!?'
        raise SystemExit
    
    plt.close('all')
    
    # return RxC array of subplots in 2-d array
    # rows share y-ticks, columns share x-ticks
    nrows, ncols = 4, 9
    save_file = '/tmp/volts.png'
    fv = FigureVolts(nrows, ncols, save_file)
    for r in range(nrows):
        for c in range(ncols):
            fv.axarr[r, c].xaxis.set_major_locator(mondays)
            fv.axarr[r, c].xaxis.set_minor_locator(alldays)
            fv.axarr[r, c].xaxis.set_major_formatter(weekFormatter)
            candlestick_ohlc(fv.axarr[r, c], quotes, width=0.6, colordown='b', colorup='r')
            
            # date axis and autoscale view
            fv.axarr[r, c].xaxis_date()
            fv.axarr[r, c].autoscale_view()
            #fv.add_subplot(r, c, x, y, 'V%d%d' % (r, c) )
        
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
    fv.fig.subplots_adjust(left=0.1, hspace=0.25, wspace=0.15)
    
    # hide x ticks for top plots and y ticks for right plots
    plt.setp([a.get_xticklabels() for a in fv.axarr[0, :]], visible=False)
    plt.setp([a.get_yticklabels() for a in fv.axarr[:, 1]], visible=False)
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    
    plt.show()    
    #fv.save()    

if __name__ == '__main__':
    demo_serious()