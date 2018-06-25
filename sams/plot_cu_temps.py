#!/usr/bin/env python

import numpy as np
import pandas as pd
import datetime
from pims.database.samsquery import SimpleQueryAOS, query_cu_packet_temps, query_gse_packet_current
from pimsdateutil import round_time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.transforms import Bbox
from sqlalchemy import create_engine


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
    #print d1.strftime('%Y-%m-%d %H:%M:%S')
    #print d2.strftime('%Y-%m-%d %H:%M:%S')
    df = query_cu_packet_temps(d1, d2)
    ax = plt.figure(figsize=(11, 8.5), dpi=200).add_subplot(111)
    df.plot(ax=ax, x='timestamp').legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.subplots_adjust(left=0.1, right=0.85, bottom=0.0, top=0.88)
    
    format_x_date_month_day(ax)
    
    dt = datetime.datetime.now()
    plt.title('SAMS CU Laptop Temperatures (updated at %s)' % dt.strftime('%Y-%m-%d %H:%M:%S'))
    plt.ylabel('Temp. (deg. C)')
    plt.xlabel('GMT Hour')
    plt.ylim((20, 100))
    ax.grid(which='both', color=(0.2, 0.3, 0.3), linestyle=':', linewidth=0.4)
        
    for label in ax.xaxis.get_ticklabels(minor=True)[::2]:
        label.set_visible(False)

    #plt.show()

    plt.savefig('/misc/yoda/www/plots/user/sams/status/cutemps.pdf')    
    

def plot_gse_current():
    d2 = round_time(datetime.datetime.now(), round_to=1)
    d1 = round_time(d2 - datetime.timedelta(hours=36), round_to=1)
    #print d1.strftime('%Y-%m-%d %H:%M:%S')
    #print d2.strftime('%Y-%m-%d %H:%M:%S')
    df = query_gse_packet_current(d1, d2)
    
    # resample for mean every minute
    dfc_m = df.reset_index().set_index('ku_timestamp').resample('60S').mean()
    dfc_m = dfc_m.reset_index()
    #print dfc_m
        
    ax = plt.figure(figsize=(11, 8.5), dpi=150).add_subplot(111)
    #dfc_m.plot(ax=ax, x='ku_timestamp', y='er6_locker_3_current', legend=False)
    plt.plot(dfc_m['ku_timestamp'], dfc_m['er6_locker_3_current'])
    plt.subplots_adjust(left=0.1, right=0.85, bottom=0.15, top=0.88)
    
    format_x_date_month_day(ax)
    
    dt = datetime.datetime.now()
    plt.title('ER6 Locker 3 Current, 60-Second Average (updated at %s)' % d2.strftime('%Y-%m-%d %H:%M:%S'))
    plt.ylabel('Current (A)')
    plt.xlabel('GMT Hour')
    plt.ylim((-0.1, 6.1))
    ax.grid(which='both', color=(0.2, 0.3, 0.3), linestyle=':', linewidth=0.4)
    plt.yticks([0, 1, 2, 3, 4, 5, 6])
        
    for label in ax.xaxis.get_ticklabels(minor=True)[::2]:
        label.set_visible(False)
    
    #plt.show()
    plt.savefig('/misc/yoda/www/plots/user/sams/status/er6_locker3_current.pdf')   

    

def plot_ad_hoc_gse_current(stofile):

    from pims.pad.amp_kpi import sto2dataframe
    from pims.pad.amp_kpi import ER6_LOCKER3_MSID_MAP
    from pims.utils.pimsdateutil import doytimestr_to_datetime
    
    df = sto2dataframe(stofile, ER6_LOCKER3_MSID_MAP)
    df['GMT'] = df['GMT'].apply(doytimestr_to_datetime)
    dmin = min(df['GMT'])
    dmax = max(df['GMT'])
    d2 = round_time(dmax, round_to=1)
    d1 = round_time(d2 - datetime.timedelta(hours=36), round_to=1)
    print d1.strftime('%Y-%m-%d %H:%M:%S')
    print d2.strftime('%Y-%m-%d %H:%M:%S')

    # resample for mean every minute
    dfc_m = df.reset_index().set_index('GMT').resample('60S').mean()
    dfc_m = dfc_m.reset_index()
    #print dfc_m
        
    ax = plt.figure(figsize=(11, 8.5), dpi=150).add_subplot(111)
    #dfc_m.plot(ax=ax, x='ku_timestamp', y='er6_locker_3_current', legend=False)
    plt.plot(dfc_m['GMT'], dfc_m['ER6_Locker3_Current'])
    plt.subplots_adjust(left=0.1, right=0.85, bottom=0.15, top=0.88)
    
    format_x_date_month_day(ax)
    
    dt = datetime.datetime.now()
    plt.title('ER6 Locker 3 Current, 60-Second Average (updated at %s)' % d2.strftime('%Y-%m-%d %H:%M:%S'))
    plt.ylabel('Current (A)')
    plt.xlabel('GMT Hour')
    plt.ylim((-0.1, 6.1))
    ax.grid(which='both', color=(0.2, 0.3, 0.3), linestyle=':', linewidth=0.4)
    plt.yticks([0, 1, 2, 3, 4, 5, 6])
        
    for label in ax.xaxis.get_ticklabels(minor=True)[::2]:
        label.set_visible(False)
    
    #plt.show()
    plt.savefig('/misc/yoda/www/plots/user/sams/status/er6_locker3_current_adhoc.pdf')   


def insert_ad_hoc_gse_current(stofile):
    """not really insert (for now), just write as importable csv"""

    from pims.pad.amp_kpi import sto2dataframe
    from pims.pad.amp_kpi import ER6_LOCKER3_MSID_MAP
    from pims.utils.pimsdateutil import doytimestr_to_datetime
    from pims.database.samsquery import _HOST_SAMS, _UNAME_SAMS, _PASSWD_SAMS
    
    df = sto2dataframe(stofile, ER6_LOCKER3_MSID_MAP)
    df['GMT'] = df['GMT'].apply(doytimestr_to_datetime)
    df.columns = df.columns.str.lower()
    df.drop('er6_locker3_status', axis=1, inplace=True)
    df.drop('status', axis=1, inplace=True)
    df.drop('status.1', axis=1, inplace=True)
    df.columns = df.columns.str.lower()    
    df = df.rename(columns={'gmt': 'ku_timestamp'})
    #print df
    #constr = 'mysql://%s:%s@%s/%s' % (_UNAME_SAMS, _PASSWD_SAMS, _HOST_SAMS, 'samsnew')
    #engine = create_engine(constr, echo=False)
    #con = engine.raw_connection()
    #df.to_sql('gse_packet', con, flavor='mysql', schema='samsnew', if_exists='append', index=False)
    df.to_csv(stofile.replace('.sto', '.csv'))


def plot_cu_temps_custom(d1, d2=None):
    if d2 is None:
        d2 = d1 + datetime.timedelta(hours=36, seconds=9)

    print d1.strftime('%Y-%m-%d %H:%M:%S'),
    print d2.strftime('%Y-%m-%d %H:%M:%S')
    dfc = query_gse_packet_current(d1, d2)
    #print dfc
    
    df = query_cu_packet_temps(d1, d2)

    ax = plt.figure(figsize=(11, 8.5), dpi=200).add_subplot(111)
    df.plot(ax=ax, x='timestamp').legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.subplots_adjust(left=0.1, right=0.85, bottom=0.0, top=0.88)
    
    format_x_date_month_day(ax)
    
    plt.title('SAMS CU Laptop Temperatures (updated at %s)' % d2.strftime('%Y-%m-%d %H:%M:%S'))
    plt.ylabel('Temp. (deg. C)')
    plt.xlabel('GMT Hour')
    plt.ylim((20, 100))
    ax.grid(which='both', color=(0.2, 0.3, 0.3), linestyle=':', linewidth=0.4)
    
    #plt.show()
    
    for label in ax.xaxis.get_ticklabels(minor=True)[1::2]:
        label.set_visible(False)
    
    plt.savefig('/misc/yoda/www/plots/user/sams/status/cutemps_cache/temp/%s_cutemps_CUSTOM.pdf' % d2.strftime('%Y-%m-%d'))


def plot_current_custom(d1, d2=None):
    if d2 is None:
        d2 = d1 + datetime.timedelta(hours=36, seconds=9)

    print d1.strftime('%Y-%m-%d %H:%M:%S'),
    print d2.strftime('%Y-%m-%d %H:%M:%S')
    
    df = query_gse_packet_current(d1, d2)

    # resample for mean every minute
    dfc_m = df.reset_index().set_index('ku_timestamp').resample('60S').mean()
    dfc_m = dfc_m.reset_index()
    #print dfc_m
        
    #ax = plt.figure(figsize=(16, 8), dpi=200).add_subplot(111)
    ax = plt.figure(figsize=(11, 8.5), dpi=200).add_subplot(111)
    #dfc_m.plot(ax=ax, x='ku_timestamp', y='er6_locker_3_current', legend=False)
    plt.plot(dfc_m['ku_timestamp'], dfc_m['er6_locker_3_current'])
    plt.subplots_adjust(left=0.1, right=0.85, bottom=0.15, top=0.88)
    
    format_x_date_month_day(ax)
    
    dt = datetime.datetime.now()
    plt.title('ER6 Locker 3 Current, 60-Second Average (updated at %s)' % d2.strftime('%Y-%m-%d %H:%M:%S'))
    plt.ylabel('Current (A)')
    plt.xlabel('GMT Hour')
    plt.ylim((-0.1, 6.1))
    ax.grid(which='both', color=(0.2, 0.3, 0.3), linestyle=':', linewidth=0.4)
    plt.yticks([0, 1, 2, 3, 4, 5, 6])
        
    for label in ax.xaxis.get_ticklabels(minor=True)[::2]:
        label.set_visible(False)
    
    #plt.show()
    #plt.savefig('/misc/yoda/www/plots/user/sams/status/cutemps_cache/2018-03-21_laptop_lockup_er6_locker3_current.pdf')   
    plt.savefig('/misc/yoda/www/plots/user/sams/status/cutemps_cache/2018-04-11_laptop_batt_replaced_er6_locker3_current.pdf')   


def plot_cutemps_and_current(d1=None, d2=None, pdf_file=None):
    
    SEC_AVG = 30  # just for current (for now)
    
    if pdf_file is None:
        pdf_file = '/misc/yoda/www/plots/user/sams/status/cutemps_er6locker3aggcurrent.pdf'
        
    if d2 is None:
        d2 = round_time(datetime.datetime.now(), round_to=1)
    if d1 is None:
        d1 = round_time(d2 - datetime.timedelta(hours=36), round_to=1)   
    if d2 <= d1:
        print 'd2 <= d1, so nothing to do'
        return
    
    #print d1.strftime('%Y-%m-%d %H:%M:%S'),
    #print d2.strftime('%Y-%m-%d %H:%M:%S')

    # queries for temperatures and current
    df = query_cu_packet_temps(d1, d2)
    dfc = query_gse_packet_current(d1, d2)

    fig = plt.figure(num=None, figsize=(11, 8.5), dpi=200, facecolor='w', edgecolor='k')
    
    ax1 = plt.subplot(211)
    
    df.plot(ax=ax1, x='timestamp').legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    format_x_date_month_day(ax1)
    
    dt = datetime.datetime.now()
    plt.suptitle('SAMS CU Laptop Temperatures and %d-Sec. Avg. of\nER6 Locker 3 Aggregate Current (updated at %s)' % (SEC_AVG, dt.strftime('%Y-%m-%d %H:%M:%S')))
    
    plt.ylabel('Temp. (deg. C)')
    plt.xlabel('GMT Hour')
    plt.ylim((20, 100))
    ax1.grid(which='both', color=(0.2, 0.3, 0.3), linestyle=':', linewidth=0.4)
    
    for label in ax1.xaxis.get_ticklabels(minor=True):
        label.set_visible(False)

    plt.legend(prop={'size': 8}, bbox_to_anchor=(1, 0.88))

    ax2 = plt.subplot(212, sharex=ax1)
    
    # resample for averaging
    dfc_m = dfc.reset_index().set_index('ku_timestamp').resample('%dS' % SEC_AVG).mean()
    dfc_m = dfc_m.reset_index()
    #print dfc_m
        
    plt.plot(dfc_m['ku_timestamp'], dfc_m['er6_locker_3_current'])
    plt.subplots_adjust(left=0.1, right=0.85, bottom=0.15, top=0.88)
    
    format_x_date_month_day(ax2)
    
    #plt.title('ER6 Locker 3 Current, 60-Second Average (updated at %s)' % d2.strftime('%Y-%m-%d %H:%M:%S'))
    plt.ylabel('Current (A)')
    plt.xlabel('GMT Hour')
    plt.ylim((-0.1, 6.1))
    ax2.grid(which='both', color=(0.2, 0.3, 0.3), linestyle=':', linewidth=0.4)
    plt.yticks([0, 1, 2, 3, 4, 5, 6])
        
    for label in ax2.xaxis.get_ticklabels(minor=True)[::2]:
        label.set_visible(False)

    # fix top axes position to scootch it down a bit
    pos1, pos2 = ax1.get_position(), ax2.get_position()  # original positions
    pos1 = [pos1.x0, 0.94*pos1.y0, pos1.width, 1.12*pos1.height]
    ax1.set_position(pos1)  # new position for top axes
    
    #plt.show()

    plt.savefig(pdf_file)     
    

def poiwg_plot1():
    d1 = datetime.datetime(2018, 3, 21)
    d2 = datetime.datetime(2018, 3, 23)
    plot_cutemps_and_current(d1=d1, d2=d2)
    

def poiwg_plot2():
    d1 = datetime.datetime(2018, 4, 10)
    d2 = datetime.datetime(2018, 4, 12)
    plot_cutemps_and_current(d1=d1, d2=d2)    
    
    
def temp_catchup():
    import pandas as pd
    for d1 in pd.date_range(start='2018-03-31 20:00:00', end='2018-04-02 20:00:00'):
        plot_gse_locker_current(d1)


def long_current_plot():
    #d1 = datetime.datetime(2018,3,20,18,0)
    #d2 = datetime.datetime(2018,3,23,18,0)
    d2 = datetime.datetime(2018,4,12,0,0)
    d1 = d2 - datetime.timedelta(hours=36, seconds=9)
    plot_current_custom(d1, d2=d2)    


def long_temp_plot():
    #d1 = datetime.datetime(2018,3,20,18,0)
    #d2 = datetime.datetime(2018,3,23,18,0)
    d2 = datetime.datetime(2018,4,12,0,0)
    d1 = d2 - datetime.timedelta(hours=36, seconds=9)
    plot_cu_temps_custom(d1, d2=d2)


def quick_job():
    d1 = datetime.datetime(2018, 4, 30, 20)
    d2 = datetime.datetime(2018, 4, 30, 22)
    pdf_file = '/tmp/out.pdf'
    plot_cutemps_and_current(d1=d1, d2=d2, pdf_file=pdf_file)


def main():
    #plot_cu_temps()
    #plot_gse_current()
    plot_cutemps_and_current()


if __name__ == '__main__':
    main()
