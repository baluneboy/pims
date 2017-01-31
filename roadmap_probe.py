#!/usr/bin/env python

import os
import re
import sys
import datetime
import subprocess
from dateutil import parser

from pims.lib.niceresult import NiceResult
from pims.files.utils import filter_filenames
from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.files.filter_pipeline import FileFilterPipeline, EndsWith
from pims.patterns.probepats import _ROADMAP_PDF_FILENAME_PATTERN

# input parameters
defaults = {
'base_path':    '/misc/yoda/www/plots/batch',  # base path
'first_day':    '2011-12-23',                  # first day to process
'last_day':     '2011-12-24',                  # last day to process
'basename_pat': _ROADMAP_PDF_FILENAME_PATTERN, # regular expression pattern to match
}
parameters = defaults.copy()

    
def get_day_roadmap_pdf_files(base_path, day, basename_pat=_ROADMAP_PDF_FILENAME_PATTERN):
    """get list of files for given day dir and file pattern"""
    day_dir = datetime_to_ymd_path(day, base_path=base_path)
    pat = '.*' + basename_pat
    return list(filter_filenames(day_dir, re.compile(pat).match))


def parameters_ok():
    """check for reasonableness of parameters"""

    # verify base path
    if not os.path.exists(parameters['base_path']):
        print 'base path (%s) does not exist' % parameters['base_path']
        return False
    
    # convert start day to date object
    try:
        parameters['first_day'] = parser.parse( parameters['first_day'] ).date()
    except Exception, e:
        print 'could not get first_day input as date object: %s' % e.message
        return False
    
    # convert stop day to date object
    try:
        parameters['last_day'] = parser.parse( parameters['last_day'] ).date()
    except Exception, e:
        print 'could not get last_day input as date object: %s' % e.message
        return False

    # verify pattern is good regular expression
    try:
        re.compile(parameters['basename_pat'])
    except Exception, e:
        print 'basename_pat "%s" would not compile as valid regular expression' % parameters['basename_pat']

    return True # all OK; otherwise, return False somewhere above


def print_usage():
    """print helpful text how to run the program"""
    #FIXME with git keyword sub via following:
    # http://stackoverflow.com/questions/11534655/git-keyword-substitution-like-those-in-subversion
    #print version << BETTER GO AT THIS???
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])


def probe_roadmaps(parameters):
    pdf_files = []
    base_path = parameters['base_path']
    day = parameters['first_day']
    basename_pat = parameters['basename_pat']
    pdf_files.extend( get_day_roadmap_pdf_files(base_path, day, basename_pat=basename_pat) )
    print len(pdf_files)
    

def main(argv):
    """describe main routine here"""

    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parameters_ok():
            nr = NiceResult(get_day_roadmap_pdf_files, parameters)
            nr.do_work()
            result = nr.get_result()
            if result:
                return 0 # zero for unix success
            else:
                return -1

    print_usage()


if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))