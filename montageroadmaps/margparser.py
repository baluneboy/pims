#!/usr/bin/env python

"""This module utilizes argparse from the standard library to define what arguments it requires, and figure out how to
parse those from sys.argv.  The argparse module automatically generates help and usage messages and issues errors when
users give the program invalid arguments.
"""

import os
import re
import argparse
import datetime
from dateutil import parser


_TWODAYSAGO = datetime.date.today() + datetime.timedelta(days=-2)
_DEFAULT_START = datetime.datetime.combine(_TWODAYSAGO, datetime.time(0,0))
_DEFAULT_MISSING8HR = '/home/pims/dev/programs/python/pims/montageroadmaps/missing8hr.pdf'
_DEFAULT_MISSINGDAY = '/home/pims/dev/programs/python/pims/montageroadmaps/missingday.pdf'
_DEFAULT_BATCHDIR = '/misc/yoda/www/plots/batch'


def dtm_str(d):
    """return datetime object converted from input string, d"""
    dtm = parser.parse(d)
    return dtm


def folder_str(f):
    """return string provided only if this folder exists"""
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError('"%s" does not exist as foscam image folder' % f)
    return f


def pattern_str(p):
    """return string provided only if it is a valid regular expression pattern string"""
    try:
        re.compile(p)
        is_valid = True
    except re.error:
        is_valid = False
    if not is_valid:
        raise argparse.ArgumentError('"%s" does not appear to be a valid regular expression')
    return p


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
    parser = argparse.ArgumentParser(description='Create montage roadmap PDFs.')

    # positionals -----------------------------------------------------------
    
    # 2 sensors: top and bottom
    parser.add_argument('sensors', metavar='SENSOR', type=str, nargs=2,
        help='a sensor of interest (like 121f03 or es09)')

    # optionals -------------------------------------------------------------
    
    # date of interest
    help_date = "date of interest; today's default is %s" % str(_DEFAULT_START)
    parser.add_argument('-d', '--date', default=_DEFAULT_START,
                        type=dtm_str,
                        help=help_date)
        
    # verbosity
    parser.add_argument("-v", action="count", dest='verbosity',
        help="increase output verbosity (max of 3)")

    # get parsed args
    args = parser.parse_args()

    return args


if __name__ == '__main__':

    args = parse_inputs()
    print args
    
    raise SystemExit
    s1 = sys.argv[1]
    s2 = sys.argv[2]

    h0 = parser.parse(sys.argv[3])
    h1 = parser.parse(sys.argv[4])
    
    ptype = 'spgs'

    suffix1 = '_%s_%s_roadmaps500.pdf' % (s1, ptype)
    suffix2 = '_%s_%s_roadmaps500.pdf' % (s2, ptype)
    suffix3 = '_%s_%s_%s_roadmapsmont.pdf' % (s1, s2, ptype)

    #h0 = datetime.datetime(2017,  9,  22)
    #h1 = datetime.datetime(2017,  9,  24)
    #h0 = datetime.datetime(2017,  9,   1)
    #h1 = datetime.datetime(2017, 11,  12)
    
    outdir = '/tmp'   