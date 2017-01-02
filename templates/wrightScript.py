#!/usr/bin/env python

import os
import re
import sys
import datetime

from pims.lib.niceresult import NiceResult

# input parameters
defaults = {
'some_path':      '/tmp',                    # a path of interest; e.g. /misc/yoda/pub/pad
'date_start':     '2011_12_23_00_00_00.000', # first data time to process
'days_ago_end':    '3',                      # last data time to process (n days ago)
'some_pattern':   'sams2_accel_121f0.',      # regular expression pattern to match PAD sensor subdir LIKE "sams2_accel_121f03"
}
parameters = defaults.copy()


# check for reasonableness of parameters
def parameters_ok():
    """check for reasonableness of parameters"""    

    if not os.path.exists(parameters['some_path']):
        print 'the path (%s) does not exist' % parameters['some_path']
        return False

    parameters['days_ago_end'] = int(parameters['days_ago_end'])

    return True # all OK; otherwise, return False somewhere above in this def


# print helpful text how to run the program
def print_usage():
    """print helpful text how to run the program"""
    #FIXME with git keyword sub via following:
    # http://stackoverflow.com/questions/11534655/git-keyword-substitution-like-those-in-subversion
    #print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])


# briefly state what real work is done here
def process_data(params):
    """briefly state what real work is done here"""
    print 'Processing data using', params


# describe main routine here
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
            nr = NiceResult(process_data, parameters)
            nr.do_work()
            result = nr.get_result()
      
            return 0
    print_usage()  

# run main with cmd line args and return exit code
if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))