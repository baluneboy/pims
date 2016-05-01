#!/usr/bin/env python

import os
import sys
from datetime import timedelta, date
from dateutil import parser
import wget

help(wget)
raise SystemExit

wget('http://pims.grc.nasa.gov/ftp/pad/year2005/month01/day01/mams_accel_ossbtmf')
raise SystemExit

# input parameters
defaults = {
'subdirs':    ['sams2_accel_121f05', 'mma_accel_0bbd'],
'destdir':    '/tmp/pad',
'start':      '2014-05-01', # start date
'stop':       '2014-05-03', # end date
'dryrun':     'False',      # False for default processing; True to not actually download
}
parameters = defaults.copy()

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def parameters_ok():
    """check for reasonableness of parameters entered on command line"""    

    # check for destination dir
    if not os.path.exists(parameters['destdir']):
        print 'destination directory %s does not exist' % parameters['destdir']
        return False
    
    # convert start & stop parameters to date objects
    parameters['start'] = parser.parse( parameters['start'] ).date()
    parameters['stop'] = parser.parse( parameters['stop'] ).date()
    if parameters['stop'] < parameters['start']:
        print 'stop is less than start'
        return False
    
    # boolean dryrun
    try:
        parameters['dryrun'] = eval(parameters['dryrun'])
        assert( isinstance(parameters['dryrun'], bool))
    except Exception, err:
        print 'cound not handle dryrun parameter, was expecting it to eval to True or False'
        return False    
    
    return True # all OK; otherwise, return False somewhere above

def print_usage():
    """print short description of how to run the program"""
    
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def download():
    """download PAD files"""
    
    # decide if we do dry run or actually run download
    if parameters['dryrun']:
        print 'do dryrun, not actually download'
    else:
        print 'actually download'
    
    # iterate over date range and subdirs
    for single_date in daterange(parameters['start'], parameters['stop']):
        print single_date.strftime("year%Y/month%m/day%d")
        
def main(argv):
    """main routine to check inputs and download pad files"""
    
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
            download()
            return 0
    print_usage()  

url = 'http://www.futurecrew.com/skaven/song_files/mp3/razorback.mp3'

if __name__ == '__main__':
    sys.exit(main(sys.argv))
