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


_SEVENDAYSAGO = (datetime.datetime.now() - relativedelta(days=7)).strftime('%Y-%m-%d')
_ZERODAYSAGO = (datetime.datetime.now() - relativedelta(days=0)).strftime('%Y-%m-%d')

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
    day_step = 86400.0

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
            trange = np.arange(0.0, T + day_step - 1.0, day_step)
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


if __name__ == '__main__':
    sys.exit(main(sys.argv))
