#!/usr/bin/env python

"""This module utilizes argparse from the standard library to define what
arguments it requires, and figure out how to parse those from sys.argv. The
argparse module automatically generates help and usage messages and issues
errors when users give the program invalid arguments. """

import os
import argparse
import datetime
import dateutil
from dateutil.relativedelta import relativedelta
from pims.utils.pimsdateutil import relative_start_stop


START_OFFSET = relativedelta(months=1, days=6)
STOP_OFFSET = relativedelta(months=1)
DEFAULT_START, DEFAULT_STOP = relative_start_stop(datetime.date.today(), START_OFFSET, STOP_OFFSET)
DEFAULT_SENSOR = '121f03'
DEFAULT_PADDIR = '/misc/yoda/pub/pad'
DEFAULT_HISTDIR = '/misc/yoda/www/plots/batch/results/dailyhistpad'
DEFAULT_FROMFILE = '/tmp/padrunhistlist.txt'


def folder_str(fname):
    """return string provided only if this folder exists"""
    if not os.path.exists(fname):
        raise argparse.ArgumentTypeError('"%s" does not exist as a folder' % fname)
    return fname


def file_str(fname):
    """return string provided only if this file exists"""
    if not os.path.exists(fname):
        raise argparse.ArgumentTypeError('"%s" does not exist' % fname)
    return fname


def day_str(d_str):
    """return datetime.date object converted from input string, d"""
    day = dateutil.parser.parse(d_str).date()
    return day


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def show_args(args):
    """print arguments"""

    # demo show
    my_date = args.date
    if args.verbosity == 2:
        print "date of interest is {}".format(str(args.date))
    elif args.verbosity == 1:
        print "date = {}".format(str(args.date))
    else:
        print my_date
    print args


def parse_inputs():
    """parse input arguments using argparse from standard library"""
    parser = argparse.ArgumentParser(description='Running tally for PAD histograms.')

    # sensor of interest
    help_sensor = "a 200 Hz sensor (e.g. 121f03, 121f02); default is %s" % DEFAULT_SENSOR
    parser.add_argument('-s', '--sensor', default=DEFAULT_SENSOR,
                        type=str,
                        help=help_sensor)

    # start date
    help_start = "start date; default is None (for 1 month and 6 days ago)"
    parser.add_argument('-d', '--start', default=None,
                        type=day_str,
                        help=help_start)

    # stop date
    help_stop = "stop date; default is None (for 6 days after start)"
    parser.add_argument('-e', '--stop', default=None,
                        type=day_str,
                        help=help_stop)

    # PAD dir
    help_paddir = "PAD dir; default is %s" % DEFAULT_PADDIR
    parser.add_argument('-p', '--paddir', default=DEFAULT_PADDIR,
                        type=folder_str,
                        help=help_paddir)

    # output dir
    help_histdir = "histogram dir; default is %s" % DEFAULT_HISTDIR
    parser.add_argument('-g', '--histdir', default=DEFAULT_HISTDIR,
                        type=folder_str,
                        help=help_histdir)

    # get list of days from file
    help_fromfile = "from file; default is None"
    parser.add_argument('-f', '--fromfile', default=None,
                        type=file_str,
                        help=help_fromfile)

    # plot (or not)
    plot_parser = parser.add_mutually_exclusive_group(required=False)    
    plot_parser.add_argument('--plot', dest='plot', action='store_true')
    plot_parser.add_argument('--no-plot', dest='plot', action='store_false')
    parser.set_defaults(plot=False)
    
    # verbosity
    parser.add_argument("-v", action="count", dest='verbosity',
                        help="increase output verbosity (max of 3)")

    # get parsed args
    args = parser.parse_args()

    # handle the case when fromfile option is used (and we ignore start/stop)
    if args.fromfile is not None:
        print 'using fromfile option, so ignore start/stop info'
        args.start, args.stop = None, None
    else:
        # finalize start and stop dates
        if args.start is None and args.stop is None:
            args.start = DEFAULT_START
            args.stop = args.start + relativedelta(days=6)
        elif args.stop is None:
            args.stop = args.start + relativedelta(days=6)
        elif args.start is None:
            args.start = args.stop - relativedelta(days=6)
    
        # check start/stop
        if args.stop < args.start:
            raise Exception('stop less than start')

    return args


if __name__ == '__main__':

    ARGS = parse_inputs()

    DARGS = vars(ARGS)
    for k, v in DARGS.iteritems():
        print k, 'is', v
