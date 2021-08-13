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

from pims.utils.datetime_ranger import DateRange


_TWODAYSAGO = datetime.date.today() + datetime.timedelta(days=-2)
_DEFAULT_START = datetime.datetime.combine(_TWODAYSAGO, datetime.time(0,0))
_DEFAULT_MISSING8HR = '/home/pims/dev/programs/python/pims/montageroadmaps/missing8hr.pdf'
_DEFAULT_MISSINGDAY = '/home/pims/dev/programs/python/pims/montageroadmaps/missingday.pdf'
_DEFAULT_BATCHDIR = '/misc/yoda/www/plots/batch'
_DEFAULT_PLOTTYPE = 'spgs'
_DEFAULT_OUTDIR = '/home/pims/temp/montageout'


def dtm_str(d):
    """return datetime object converted from input string, d"""
    dtm = parser.parse(d)
    return dtm


def ptype_str(p):
    """return string provided only if this plot type abbrev is in expected list"""
    L = ['spgs', 'spgx', 'spgy', 'spgz']
    if p not in L:
        raise argparse.ArgumentTypeError('"%s" is not in [%s]' % (p, str(L)))
    return p


def folder_str(f):
    """return string provided only if this folder exists"""
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError('"%s" does not exist as a folder' % f)
    return f

def date_str(d):
    """return datetime date object converted from input string, s"""
    dtm = date_parser.parse(d)
    return dtm.date()

def runs_str(r):
    """return valid min_runs int value converted from string, r"""
    try:
        value = int(r)
    except Exception, e:
        raise argparse.ArgumentTypeError('minimum runs could not be converted from %s' % e.message)

    if value < 1 or value > 999:
        raise argparse.ArgumentTypeError('minimum runs has to be 1 <= r <= 999')

    return value

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

def team_str(t):
    """return uppercase of string input, provided it exists in teams.team_abbrevs"""
    t = t.upper()
    if t not in teams.team_abbrevs:
        raise argparse.ArgumentTypeError('"%s" is not in official list of teams.team_abbrevs' % t)
    return t


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
    
    # start date
    help_start = "start date; today's default is %s" % str(_DEFAULT_START)
    parser.add_argument('-d', '--start', default=_DEFAULT_START,
                        type=dtm_str,
                        help=help_start)

    # stop date
    help_stop = "stop date; today's default is %s" % str(_DEFAULT_START)
    parser.add_argument('-e', '--stop', default=_DEFAULT_START,
                        type=dtm_str,
                        help=help_stop)

    # plot type abbrev
    help_ptype = "plot type abbrev; default is %s" % _DEFAULT_PLOTTYPE
    parser.add_argument('-t', '--plottype', default=_DEFAULT_PLOTTYPE,
                        type=ptype_str,
                        help=help_ptype)

    # batch dir
    help_batchdir = "batch dir; default is %s" % _DEFAULT_BATCHDIR
    parser.add_argument('-b', '--batchdir', default=_DEFAULT_BATCHDIR,
                        type=folder_str,
                        help=help_batchdir)

    # output dir
    help_outdir = "output dir; default is %s" % _DEFAULT_OUTDIR
    parser.add_argument('-o', '--outdir', default=_DEFAULT_OUTDIR,
                        type=folder_str,
                        help=help_outdir)
        
    # verbosity
    parser.add_argument("-v", action="count", dest='verbosity',
        help="increase output verbosity (max of 3)")

    # get parsed args
    args = parser.parse_args()

    return args


if __name__ == '__main__':

    args = parse_inputs()
    print args
    
    s1 = args.sensors[0]
    s2 = args.sensors[1]

    h0 = args.start
    h1 = args.stop
    
    ptype = args.plottype

    suffix1 = '_%s_%s_roadmaps500.pdf' % (s1, ptype)
    suffix2 = '_%s_%s_roadmaps500.pdf' % (s2, ptype)
    suffix3 = '_%s_%s_%s_roadmapsmont.pdf' % (s1, s2, ptype)
    
    outdir = '/tmp'
