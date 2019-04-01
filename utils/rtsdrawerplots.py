#!/usr/bin/env python

import os
import sys
import datetime
import tempfile
import shutil

import numpy as np
import pandas as pd
from dateutil import parser
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

from pims.database.samsquery import RtsDrawerQuery, InsertToDeviceTracker
from pims.database.samsquery import _SCHEMA_SAMS, _UNAME_SAMS, _PASSWD_SAMS, _HOST_SAMS
from pims.files.pdfs.pdfcat import pdf_cat
from pims.utils.pimsdateutil import floor_day, ceil_day

_SEVENDAYSAGO = (datetime.datetime.now() - relativedelta(days=7)).strftime('%Y-%m-%d')
_ZERODAYSAGO = (datetime.datetime.now() - relativedelta(days=0)).strftime('%Y-%m-%d')

DAYSTEP = 86400.0  # seconds in a day

DRAWER_PARAMS = {
# abbrev    device    variable1               variable2
    'd1': ('RTS/D1', 'er1_drawer_1_current', 'sams_rts_d1_baseplate_temp'),
    'd2': ('RTS/D2', 'er5_drawer_2_current', 'sams_rts_d2_baseplate_temp'),
    }

# input parameters
defaults = {
    'start': _SEVENDAYSAGO,  # string for start date
    'stop':  _ZERODAYSAGO,   # string for stop date
    'output_dir': '/misc/yoda/www/plots/user/sams/status/rtsdrawers',  # string for output directory
}
parameters = defaults.copy()


def parameters_ok():
    """check for reasonableness of parameters entered on command line"""
    for param in ['start', 'stop']:
        try:
            parameters[param] = parser.parse(parameters[param])
        except Exception, e:
            print 'ABORT WHILE TRYING TO PARSE ' + param + ' INPUT BECAUSE ' + e.message
            return False

    if parameters['stop'] < parameters['start']:
        print 'ABORT BECAUSE STOP DATE IS BEFORE START'
        return False

    if (parameters['stop'] - parameters['start']) > datetime.timedelta(days=7):
        print 'ABORT BECAUSE AT MOST WE SHOULD ONLY CONSIDER 7 DAYS SPAN AT MOST'
        return False

    if not os.path.exists(parameters['output_dir']):
        print 'ABORT BECAUSE OUTPUT DIR ' + parameters['output_dir'] + ' DOES NOT EXIST'
        return False

    return True  # all OK; otherwise, return False above


def print_usage():
    """print short description of how to run the program"""
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])


def run(start, stop, output_dir):
    """create plots and gather data from start to stop date (results into output_dir)"""

    # create temp path to hold individual plots' PDF
    tmp_dir = tempfile.mkdtemp()

    # get output PDF file basename based on start/stop times (WITHOUT .pdf EXTENSION)
    output_bname = '_'.join([start.strftime('%Y-%m-%d'), stop.strftime('%Y-%m-%d'), 'RTS_Drawers'])

    T = (stop - start).total_seconds()
    DAYSTEP = 86400.0

    # iterate over 2 RTS Drawers (aka here as d1 and d2)
    pdf_files = []
    for d in ['d1', 'd2']:

        label, current_field, temperature_field = DRAWER_PARAMS[d]

        # iterate over 2 variables (fields)
        for variable in ['current', 'temperature']:

            # FIXME the following switch case type lines can be more pythonic
            if variable == 'current':
                field_name = current_field
                ymin, ymax, ylabel_str, ylabel_units, yticks = -0.05, 1.5, 'Current', 'A', np.arange(0.0, 1.5 + 0.1, 0.1)
            elif variable == 'temperature':
                field_name = temperature_field
                ymin, ymax, ylabel_str, ylabel_units, yticks = 15, 45, 'Temperature', 'degC', np.arange(16.0, 44.0 + 1.0, 2.0)
            else:
                raise Exception('unhandled variable %s' % variable)
            ylabel = ylabel_str + '(' + ylabel_units + ')'

            # initialize and run query
            dqv = RtsDrawerQuery(_HOST_SAMS, _SCHEMA_SAMS, _UNAME_SAMS, _PASSWD_SAMS, field_name, begin_date=start, end_date=stop)
            dfv = dqv.dataframe_from_query()

            # rename from db table column naming to local variable name here
            dfv = dfv.rename(index=str, columns={field_name: variable})

            # get median value from original (not rolling mean) data set
            median_value = dfv[variable].median(skipna=True)

            #              device    variable
            print ','.join([label, field_name, ylabel_units, start.strftime('%Y-%m-%d'), stop.strftime('%Y-%m-%d'), '%0.3f' % median_value]),

            # insert to device_tracker db table on yoda (once a week, when start is Monday)
            if start.weekday() == 0 and T == 604800.0:
                i2dt = InsertToDeviceTracker(_HOST_SAMS, _SCHEMA_SAMS, 'device_tracker', _UNAME_SAMS, _PASSWD_SAMS)
                i2dt.insert(label, field_name, ylabel_units, start.strftime('%Y-%m-%d'), stop.strftime('%Y-%m-%d'), 'median', median_value)
                pdf_suffix = ".pdf"  # these are keepers
            else:
                pdf_suffix = "_tmp.pdf"  # short lived (less than a month should do it) since keepers are weekly

            # FIXME not sure if/why we operate on copy, but we are sticking with this for now

            # create copy of dataframe to operate on
            dfv_new = dfv.copy()

            # create column for 60-second rolling mean
            prefix_str = '60sec_rolling_mean_'
            dfv_new[prefix_str + variable] = dfv_new[variable].rolling(window=60).mean()

            # FIXME I bet we can make the following index shuffle go away with better pandas know-how
            dfv_new.reset_index(level=0, inplace=True)
            dfv_new = dfv_new.rename(index=str, columns={'index': 'gmt'})
            ax = dfv_new.plot(x='gmt', y=prefix_str + variable)

            # some plotting stuff
            long_title = '%s, Median %s = %0.3f' % (label, ylabel, median_value)
            plt.title(long_title)
            plt.xlabel('GMT')
            plt.ylabel(ylabel)
            # x1, x2, y1, y2 = plt.axis()
            # plt.axis((x1, x2, ymin, ymax))

            xticks = pd.date_range(start, stop, freq='D')

            plt.axis((0.0, T, ymin, ymax))
            trange = np.arange(0.0, T + DAYSTEP - 1.0, DAYSTEP)
            plt.xticks(trange)
            ax.set_xticklabels([x.strftime('%Y-%m-%d') for x in xticks])
            plt.yticks(yticks)

            # plt.xticks(rotation=10)
            bname = label + '_' + variable.title()
            pdf = os.path.join(tmp_dir, bname.replace('/', '_') + '.pdf')
            fig = plt.gcf()
            fig.set_size_inches(11, 8.5)
            # fig.suptitle(prefix_str + variable, fontsize=20)

            ax = plt.gca()
            ax.xaxis.grid(b=True, which='major', color='gray', alpha=0.55)
            ax.xaxis.grid(b=True, which='minor', color='gray', alpha=0.35)
            ax.yaxis.grid(b=True, which='major', color='gray', alpha=0.55)
            ax.yaxis.grid(b=True, which='minor', color='gray', alpha=0.35)
            plt.minorticks_on()

            plt.savefig(pdf, dpi=120)
            print '  ', pdf  # the tempfile PDF for this plot
            pdf_files.append(pdf)
            plt.close(fig)

    # sort and concatenate PDFs
    s = sorted(pdf_files, key=lambda x: os.path.basename(x).split('_')[2])
    output_file = os.path.join(output_dir, output_bname + pdf_suffix)
    pdf_cat(s, output_file)
    print 'evince ' + output_file + ' &'

    # get rid of temp dir & its single-plot PDFs
    shutil.rmtree(tmp_dir)


def get_dataframe(start, stop, variable, field_name):
    """get dataframe for start/stop range"""
    
    # init and run query
    dq = RtsDrawerQuery(_HOST_SAMS, _SCHEMA_SAMS, _UNAME_SAMS, _PASSWD_SAMS, field_name, begin_date=start, end_date=stop)
    df = dq.dataframe_from_query()
    
    # rename from db table column naming to local variable name here
    df = df.rename(index=str, columns={field_name: variable})
    
    # rename from db table column naming to local variable name here
    df = df.rename(index=str, columns={field_name: variable})    
    
    return df


def subplot_dataframe(df2, start, stop, variable, ylabel, ymin, ymax, yticks, label, sup_title):
    """plot this variable for this time range"""
    
    T = (stop - start).total_seconds()
    
    # create copy of dataframe to operate on
    df2_new = df2.copy()

    # create column for 60-second rolling mean
    prefix_str = '60sec_rolling_mean_'
    df2_new[prefix_str + variable] = df2_new[variable].rolling(window=60).mean()

    df2_new.reset_index(level=0, inplace=True)
    df2_new = df2_new.rename(index=str, columns={'index': 'gmt'})
    
    ax = df2_new.plot(x='gmt', y=prefix_str + variable)

    # some plotting stuff
    plt.xlabel('GMT')
    plt.ylabel(ylabel)
    plt.axis((0.0, 1.00 * T, ymin, ymax))
    
    # ticks
    xticks = pd.date_range(start, stop, freq='D')
    trange = np.arange(0.0, T + DAYSTEP, DAYSTEP)
    plt.xticks(trange)
    ax.set_xticklabels([x.strftime('%Y-%m-%d') for x in xticks])
    plt.yticks(yticks)
    
    # branch on BEFORE vs. AFTER power cycle
    if 'AFTER Power Cycle' == sup_title:
        fromstr = xticks[-3].strftime('%Y-%m-%d')
        tostr = xticks[-1].strftime('%Y-%m-%d')
        i1, i2 = -3, -1
    elif 'BEFORE Power Cycle' == sup_title:
        fromstr = xticks[0].strftime('%Y-%m-%d')
        tostr = xticks[2].strftime('%Y-%m-%d')
        i1, i2 = 0, 2
    else:
        raise Exception('unhandled condition %s' % sup_title)
        
    df2_tmp = df2_new[(df2_new['gmt'] > fromstr) & (df2_new['gmt'] < tostr)]
    median_value = df2_tmp[variable].median(skipna=True)
    
    long_title = '%s, From %s To %s' % (label, start.strftime('%Y-%m-%d'), stop.strftime('%Y-%m-%d'))
    plt.title(long_title)
    
    out_dir = '/misc/yoda/www/plots/user/sams/status/rtsdrawers/powercycles'
    bname = label + '_' + variable.title()
    pdf = os.path.join(out_dir, bname.replace('/', '_') + '.pdf')
    fig = plt.gcf()
    fig.set_size_inches(11, 8.5)
    fig.suptitle(sup_title, fontsize=20)

    ax = plt.gca()
    ax.xaxis.grid(b=True, which='major', color='gray', alpha=0.55)
    ax.xaxis.grid(b=True, which='minor', color='gray', alpha=0.35)
    ax.yaxis.grid(b=True, which='major', color='gray', alpha=0.55)
    ax.yaxis.grid(b=True, which='minor', color='gray', alpha=0.35)
    plt.minorticks_on()
    
    xlocs = ax.get_xticks()
    xtxt_loc =(xlocs[i1] + xlocs[i2]) / 2.0
    xarrow1, xarrow2 = xlocs[i1], xlocs[i2]
    if 'current' == variable:
        ytxt_loc = 1.0
    elif 'temperature' == variable:
        ytxt_loc = 31.0
    else:
        raise Exception('unhandled variable %s' % variable)

    plt.annotate(s='', xytext=(xarrow1, ytxt_loc), xy=(xarrow2, ytxt_loc), arrowprops=dict(arrowstyle='<->', color='r'))
    plt.text(xtxt_loc, ytxt_loc, 'median=%.3f A' % median_value, color='red', fontsize=12, horizontalalignment='center')
    
    bname = '_'.join([start.strftime('%Y-%m-%d'), stop.strftime('%Y-%m-%d'), label, variable.title(), sup_title.replace(' ', '_')])
    pdf = os.path.join(out_dir, bname.replace('/', '_') + '.pdf')
    fig = plt.gcf()
    fig.set_size_inches(11, 8.5)
    
    plt.savefig(pdf, dpi=120)
    print 'saved %s' % pdf
    
    plt.close(fig)
    

def plot_rtsd_power_cycle(rtsd, gmtoff, gmton, tdelta_span, variable):
    """save 2-by-2 plot of current & temperature for before & after power cycle"""
        
    # get field info for this drawer
    label, current_field, temperature_field = DRAWER_PARAMS[rtsd]

    # FIXME the following switch case type lines can be more pythonic
    if variable == 'current':
        field_name = current_field
        ymin, ymax, ylabel_str, ylabel_units, yticks = -0.05, 1.5, 'Current', 'A', np.arange(0.0, 1.5 + 0.1, 0.1)
    elif variable == 'temperature':
        field_name = temperature_field
        ymin, ymax, ylabel_str, ylabel_units, yticks = 15, 45, 'Temperature', 'degC', np.arange(16.0, 44.0 + 1.0, 2.0)
    else:
        raise Exception('unhandled variable %s' % variable)
    ylabel = ylabel_str + '(' + ylabel_units + ')'
   
    # run query for current going OFF
    start = ceil_day(gmtoff) - tdelta_span
    stop = ceil_day(gmtoff)
    df2off = get_dataframe(start, stop, variable, field_name)

    subplot_dataframe(df2off, start, stop, variable, ylabel, ymin, ymax, yticks, label, 'BEFORE Power Cycle')

    # run query for current going ON
    start = floor_day(gmton)
    stop = ceil_day(gmton) + tdelta_span - datetime.timedelta(days=1)
    T = (stop - start).total_seconds()
    df2on = get_dataframe(start, stop, variable, field_name)
    
    subplot_dataframe(df2on, start, stop, variable, ylabel, ymin, ymax, yticks, label, 'AFTER Power Cycle')
    
    plt.show()


def main(argv):
    """get command line arguments (or defaults) and run processing"""
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if 2 != len(pair):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parameters_ok():
            run(parameters['start'], parameters['stop'], parameters['output_dir'])
            return 0
    print_usage()


def play_catchup(startstr, stopstr):
    """run some catch-up code to get us up-to-date"""
    # for d in pd.date_range(start='2018-01-01', end='2018-08-09', freq='7D'):
    for d in pd.date_range(start=startstr, end=stopstr, freq='1D'):
        start = d
        stop = d + datetime.timedelta(days=7)
        run(start, stop, '/misc/yoda/www/plots/user/sams/status/rtsdrawers')


def plot_power_cycles():
    #-----------------------------------
    #RTS Drawer Current and Temperature:
    #-----------------------------------
    #
    #POWER CYCLES RTS/D1
    #2019-02-12 043/15:34:26 RTS/D1 OFF SCREEN CLEAN
    #2019-02-12 043/16:38:31 RTS/D1 ON  SCREEN CLEAN
    #2018-11-23 327/23:19:14 RTS/D1 OFF
    #2018-11-24 328/14:37:12 RTS/D1 ON
    #2018-09-14 257/12:22:35 RTS/D1 OFF
    #2018-09-14 257/13:58:46 RTS/D1 ON
    #2018-08-01 213/08:26:15 RTS/D1 OFF SCREEN CLEAN
    #2018-08-01 213/10:12:57 RTS/D1 ON  SCREEN CLEAN
    #
    #POWER CYCLES RTS/D2
    #2019-02-25 056/01:03:58 RTS/D2 OFF
    #2019-02-25 056/01:10:55 RTS/D2 ON
    #2019-02-12 043/15:34:53 RTS/D2 OFF SCREEN CLEAN
    #2019-02-12 043/16:42:46 RTS/D2 ON  SCREEN CLEAN
    #2019-02-11 042/03:58:30 RTS/D2 OFF
    #2019-02-11 042/04:05:00 RTS/D2 ON
    #2018-08-01 213/08:26:23 RTS/D2 OFF SCREEN CLEAN
    #2018-08-01 213/10:19:30 RTS/D2 ON  SCREEN CLEAN
    
    pwr_cycs = [
      # drawer                   power OFF GMT                                power ON GMT
        ('d1', datetime.datetime(2019,  2, 12, 15, 34, 26), datetime.datetime(2019,  2, 12, 16, 38, 31)),
        ('d1', datetime.datetime(2018, 11, 23, 23, 19, 14), datetime.datetime(2018, 11, 24, 14, 37, 12)),
        ('d1', datetime.datetime(2018,  9, 14, 12, 22, 35), datetime.datetime(2018,  9, 14, 13, 58, 46)),
        ('d1', datetime.datetime(2018,  8,  1,  8, 26, 15), datetime.datetime(2018,  8,  1, 10, 12, 57)),
        ('d2', datetime.datetime(2019,  2, 25,  1,  3, 58), datetime.datetime(2019,  2, 25,  1, 10, 55)),
        ('d2', datetime.datetime(2019,  2, 12, 15, 34, 53), datetime.datetime(2019,  2, 12, 16, 42, 46)),
        ('d2', datetime.datetime(2019,  2, 11,  3, 58, 30), datetime.datetime(2019,  2, 11,  4,  5, 00)),
        ('d2', datetime.datetime(2018,  8,  1,  8, 26, 23), datetime.datetime(2018,  8,  1, 10, 19, 30)),
        ]
  
    tdelta_span = datetime.timedelta(days=7)
    variables = ['current', 'temperature']
    for variable in variables:
        for pc in pwr_cycs:
            rtsd, gmtoff, gmton = pc[0], pc[1], pc[2]
            plot_rtsd_power_cycle(rtsd, gmtoff, gmton, tdelta_span, variable)
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
