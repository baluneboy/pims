#!/usr/bin/env python

"""This module utilizes argparse from the standard library to define what
arguments it requires, and figure out how to parse those from sys.argv. The
argparse module automatically generates help and usage messages and issues
errors when users give the program invalid arguments. """

import os
import argparse
import datetime
from dateutil import parser, relativedelta
from pims.utils.pimsdateutil import relative_start_stop


_start_offset = relativedelta.relativedelta(months=1, days=6)
_stop_offset = relativedelta.relativedelta(months=1)
DEFAULT_START, DEFAULT_STOP = relative_start_stop(datetime.date.today(), _start_offset, _stop_offset)
DEFAULT_SENSOR = '121f03'
DEFAULT_PADDIR = '/misc/yoda/pub/pad'
DEFAULT_HISTDIR = '/misc/yoda/www/plots/batch/results/dailyhistpad'

# TODO an axis parameter is not employed; we always do daily save for all 4 axes (x,y,z,v); maybe use axis for plot filter?


def folder_str(f):
    """return string provided only if this folder exists"""
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError('"%s" does not exist as a folder' % f)
    return f


def day_str(d):
    """return datetime.date object converted from input string, d"""
    day = parser.parse(d).date()
    return day


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
    help_sensor = "a 200 Hz sensor of interest (like 121f03, 121f02); default is %s" % DEFAULT_SENSOR
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

    # batch dir
    help_paddir = "PAD dir; default is %s" % DEFAULT_PADDIR
    parser.add_argument('-p', '--paddir', default=DEFAULT_PADDIR,
                        type=folder_str,
                        help=help_paddir)

    # output dir
    help_histdir = "histogram dir; default is %s" % DEFAULT_HISTDIR
    parser.add_argument('-g', '--histdir', default=DEFAULT_HISTDIR,
                        type=folder_str,
                        help=help_histdir)

    # verbosity
    parser.add_argument("-v", action="count", dest='verbosity',
                        help="increase output verbosity (max of 3)")

    # get parsed args
    args = parser.parse_args()

    # finalize start and stop dates
    if args.start is None and args.stop is None:
        args.start = DEFAULT_START
        args.stop = args.start + relativedelta.relativedelta(days=6)
    elif args.stop is None:
        args.stop = args.start + relativedelta.relativedelta(days=6)
    elif args.start is None:
        args.start = args.stop - relativedelta.relativedelta(days=6)

    # check start/stop
    if args.stop < args.start:
        raise Exception('stop less than start')

    return args


if __name__ == '__main__':

    args = parse_inputs()

    d = vars(args)
    for k, v in d.iteritems():
        print k, 'is', v
