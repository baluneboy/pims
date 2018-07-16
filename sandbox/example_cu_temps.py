#!/usr/bin/env python

import datetime
from pims.database.samsquery import SimpleQueryAOS, query_cu_packet_temps
from pimsdateutil import round_time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def format_x_date_month_day(ax):   
    # Standard date x-axis formatting block, labels each month and ticks each day
    days = mdates.DayLocator()
    hours = mdates.HourLocator()
    #months = mdates.MonthLocator()  # every month
    dayFmt = mdates.DateFormatter('%D  ')
    hourFmt = mdates.DateFormatter('%H')
    #monthFmt = mdates.DateFormatter('%Y-%m')
    ax.figure.autofmt_xdate()
    #ax.xaxis.set_major_locator(months) 
    #ax.xaxis.set_major_formatter(monthFmt)
    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(dayFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hourFmt)
    

def plot_cu_temps():
    d2 = round_time(datetime.datetime.now(), round_to=1)
    d1 = round_time(d2 - datetime.timedelta(hours=36), round_to=1)
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print d1.strftime('%Y-%m-%d %H:%M:%S')
    #print d2.strftime('%Y-%m-%d %H:%M:%S')
    df = query_cu_packet_temps(d1, d2)
    ax = plt.figure(figsize=(16, 8), dpi=150).add_subplot(111)
    df.plot(ax=ax, x='timestamp').legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    format_x_date_month_day(ax)
    
    dt = datetime.datetime.now()
    plt.title('SAMS CU Laptop Temperatures (updated at %s)' % dt.strftime('%Y-%m-%d %H:%M:%S'))
    plt.ylabel('Temp. (deg. C)')
    plt.xlabel('GMT Hour')
    plt.ylim((20, 100))
    ax.grid(which='both', color=(0.2, 0.3, 0.3), linestyle=':', linewidth=0.4)
    
    #plt.show()
    
    for label in ax.xaxis.get_ticklabels(minor=True)[::2]:
        label.set_visible(False)
    
    plt.savefig('/misc/yoda/www/plots/user/sams/status/cutemps.png')
        

if __name__ == '__main__':
    plot_cu_temps()
