#!/usr/bin/env python

import os
import sys
import datetime

import numpy as np
import pandas as pd
from dateutil import parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil.relativedelta import relativedelta
from scipy.stats import trim_mean
from PIL import Image

from pims.database.samsquery import RtsDrawerCurrentQuery
from pims.database.samsquery import _SCHEMA_SAMS, _UNAME_SAMS, _PASSWD_SAMS, _HOST_SAMS
from pims.utils.pimsdateutil import floor_five_minutes
from pims.files.utils import mkdir_p


# define some useful values
_ENDTIME = floor_five_minutes(datetime.datetime.now())
_NOW = _ENDTIME.strftime('%Y-%m-%d %H:%M:%S')
_TWELVEHOURSAGO = floor_five_minutes((_ENDTIME - relativedelta(hours=12))).strftime('%Y-%m-%d %H:%M:%S')

DRAWER_PARAMS = {
# abbrev    device    variable1              variable2
    'd1': ('RTS/D1', 'er1_drawer_1_current', None),
    'd2': ('RTS/D2', 'er5_drawer_2_current', None),
    }

# input parameters
defaults = {
    'start': _TWELVEHOURSAGO,  # string for start datetime
    'stop':  _NOW,             # string for stop datetime
    'output_dir': '/misc/yoda/www/plots/user/sams/status/drawer_current',  # string for output directory
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
        print 'ABORT BECAUSE STOP IS BEFORE START'
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


def run(start, stop, out_dir):
    """create plots and gather data from start to stop date (results into output_dir)"""

    # date axis locators and formatter
    even_hours = mdates.HourLocator(byhour=range(0, 24, 2))
    odd_hours = mdates.HourLocator(byhour=range(1, 24, 2))
    dtFmt = mdates.DateFormatter('%Y-%m-%d\n%H:%M')

    # iterate over 2 RTS Drawers (aka here as d1 and d2)
    for d in ['d1', 'd2']:

        # get output PDF file basename based on start/stop times (WITHOUT .pdf EXTENSION)
        output_bname = '_'.join([start.strftime('%Y-%m-%d_%H_%M'), stop.strftime('%Y-%m-%d_%H_%M'), 'rts' + d])

        label, current_field, temperature_field = DRAWER_PARAMS[d]

        # iterate over just one variable (one field) -- we used to do temperature too
        for variable in ['current', ]:  # for variable in ['current', 'temperature']:

            # FIXME the following switch case type lines can be more pythonic
            if variable == 'current':
                field_name = current_field
                ymin, ymax, ylabel_str, ylabel_units, yticks = -0.05, 1.0, 'Current', 'A', np.arange(-0.1, 1.0 + 0.1, 0.1)
            elif variable == 'temperature':
                field_name = temperature_field
                ymin, ymax, ylabel_str, ylabel_units, yticks = 15, 45, 'Temperature', 'degC', np.arange(16.0, 44.0 + 1.0, 2.0)
            else:
                raise Exception('unhandled variable %s' % variable)
            ylabel = ylabel_str + '(' + ylabel_units + ')'

            # initialize and run query
            dqv = RtsDrawerCurrentQuery(_HOST_SAMS, _SCHEMA_SAMS, _UNAME_SAMS, _PASSWD_SAMS, field_name, start, stop)
            dfv = dqv.dataframe_from_query()

            # rename from db table column naming to local variable name here
            dfv = dfv.rename(index=str, columns={field_name: variable})

            # get median value from original (not rolling mean) data set
            median_value = dfv[variable].median(skipna=True)

            # FIXME not sure if/why we operate on copy, but we are sticking with this for now

            # create copy of dataframe to operate on
            dfv_new = dfv.copy()

            # compute 300-second rolling mean (abandon in favor of trimmed mean below instead)
            # y = dfv_new[variable].rolling(window=300).mean()

            # compute 900-second rolling (25% proportion cut) trimmed mean & get time data for plot
            y = dfv_new[variable].rolling(window=900).apply(lambda x: trim_mean(x, 0.25), raw=True)
            t = pd.to_datetime(dfv_new.index)

            # create plot
            fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
            ax.plot(t, y)

            # format the ticks
            ax.xaxis.set_major_locator(even_hours)
            ax.xaxis.set_minor_locator(odd_hours)
            ax.xaxis.set_major_formatter(dtFmt)

            # limits for datetime axis
            ax.set_xlim(t[0], t[-1])

            # set yticks
            plt.yticks(yticks)
            # ax.set_ylim(-0.02, yticks[-1])
            ax.set_ylim(-0.02, 1.02)

            # subtle grid lines
            ax.xaxis.grid(b=True, which='major', color='gray', alpha=0.55)
            ax.xaxis.grid(b=True, which='minor', color='gray', alpha=0.35)
            ax.yaxis.grid(b=True, which='major', color='gray', alpha=0.55)
            ax.yaxis.grid(b=True, which='minor', color='gray', alpha=0.35)

            # title and labels
            t1 = '%s %s' % (label, ylabel.title().split('(')[0])
            t2 = '15-Minute Rolling Trimmed Mean, Median = %0.3f A' % median_value
            # t3 = 'Expect decrease (step down in current) of about 0.2 A when drawer fan goes off.'
            # long_title = '\n'.join([t1, t2, t3])
            long_title = '\n'.join([t1, t2])
            plt.title(long_title)
            plt.xlabel('GMT')
            plt.ylabel(ylabel.replace('(', ' ('))

            # add modified timestamp (small, gray, upper-right)
            ix = int(0.85 * len(t))
            xtext = t[ix]
            ytext = 1.1
            stext = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            plt.text(xtext, ytext, 'modified: %s' % stext, color='gray', fontsize=8, alpha=0.7)

            # output filename for PDF
            #pdf = os.path.join(out_dir, output_bname) + '.pdf'

            # set figure size landscape
            fig.set_size_inches(11, 8.5)

            # save without timestamp
            plt.savefig(os.path.join(out_dir, 'rts%s' % d) + '.pdf', dpi=120)
            plt.savefig(os.path.join(out_dir, 'rts%s' % d) + '.png', dpi=120)

            # if top- or mid-day, then archive the pdf too
            if (start.hour == 0 or start.hour == 12) and start.minute == 0:
                subdir = os.path.join('year%4d' % start.year, 'month%02d' % start.month, 'day%02d' % start.day)
                pth = os.path.join(out_dir, subdir)
                mkdir_p(pth)
                pdf_file = os.path.join(pth, output_bname + '.pdf')
                plt.savefig(pdf_file, dpi=120)

            plt.close(fig)


def paste_images():
    # img = Image.new('RGB', (1320, 1239), (255, 255, 255))
    # img.save('blank_image.png', 'PNG')

    img = Image.open('/misc/yoda/www/plots/user/sams/status/drawer_current/blank_image.png')
    img.paste(Image.open('/misc/yoda/www/plots/user/sams/status/drawer_current/rtsd1.png'), (0, 0))
    img.paste(Image.open('/misc/yoda/www/plots/user/sams/status/drawer_current/rtsd1_text.png'), (0, 1020))
    width, height = 1320, 1239
    new_width = 1600
    new_height = 1200
    img = img.resize((new_width, new_height), Image.ANTIALIAS)
    img.save('/misc/yoda/www/plots/user/sams/status/drawer_current/rtsd1txt.png')

    img = Image.open('/misc/yoda/www/plots/user/sams/status/drawer_current/blank_image.png')
    img.paste(Image.open('/misc/yoda/www/plots/user/sams/status/drawer_current/rtsd2.png'), (0, 0))
    img.paste(Image.open('/misc/yoda/www/plots/user/sams/status/drawer_current/rtsd2_text.png'), (0, 1020))
    img = img.resize((new_width, new_height), Image.ANTIALIAS)
    img.save('/misc/yoda/www/plots/user/sams/status/drawer_current/rtsd2txt.png')


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
            # paste_images()  # concatenate upper plot and lower static text (as image) to form one uber image
            return 0
    print_usage()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
