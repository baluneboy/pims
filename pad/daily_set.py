#!/usr/bin/env python
version = '$Id$'

import os
import re
import sys
import datetime
from dateutil import parser
from daterange import daterange
import pandas as pd
from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.files.utils import filter_dirnames

_TWODAYSAGO = str( datetime.datetime.now().date() - datetime.timedelta(days=2) )

# input parameters
defaults = {
'start':        _TWODAYSAGO,    # string for start date
'stop':         _TWODAYSAGO,    # string for stop date
'subdirpat':    '(sams2|mams|samses)_accel_(121f0.*|hirap.*|es.*)', # string regexp pattern for sensor subdirs
}
parameters = defaults.copy()

def parametersOK():
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
    
    return True # all OK; otherwise, return False above

def printUsage():
    """print short description of how to run the program"""
    print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def run(start, stop, subdirpat):
    """explain this where the real work is done"""
    sensor_set = set()
    for d in daterange(start, to=stop):
        daydir = datetime_to_ymd_path(d)
        if not os.path.exists(daydir):
            print daydir, 'NO_YMD_PATH_FOR_SUBDIRS'
            continue
        predicate = re.compile(os.path.join(daydir, subdirpat)).match
        [sensor_set.add(os.path.basename(d)) for d in filter_dirnames(daydir, predicate)]
    sensor_list = list(sensor_set)
    print sorted(sensor_list, reverse=True)
    
def cmp_items(a, b):
    if a.startswith('sams'):
        if b.startswith('mams'):
            return 1
    elif a.startswith('mams'):
        if b.startswith('sams'):
            return -1
    else:
        return 0
        
def main(argv):
    """describe what this routine does here"""
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parametersOK():
            run(parameters['start'], parameters['stop'], parameters['subdirpat'])          
            return 0
    printUsage()  

if __name__ == '__main__':
    sys.exit(main(sys.argv))