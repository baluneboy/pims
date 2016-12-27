#!/usr/bin/env python

import os
import re
import sys
import datetime

# input parameters
defaults = {
'somePath':      '/misc/yoda/pub/pad',      # a path of interest
'dateStart':     '2011_12_23_00_00_00.000', # first data time to process
'daysAgoEnd':    '3',                       # last data time to process (n days ago)
'somePattern':   'sams2_accel_121f0.',      # regular expression pattern to match PAD sensor subdir LIKE "sams2_accel_121f03"
}
parameters = defaults.copy()

# check for reasonableness of parameters
def parameters_ok():
    """check for reasonableness of parameters"""    

    if not os.path.exists(parameters['somePath']):
        print 'the path (%s) does not exist' % parameters['somePath']
        return 0

    parameters['daysAgoEnd'] = int(parameters['daysAgoEnd'])

    return 1 # all OK; otherwise, return 0 above

# print helpful text how to run the program
def print_usage():
    """print helpful text how to run the program"""
    print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

# briefly state what real work is done here
def process_data(sensor):
    """briefly state what real work is done here"""
    
    if not sensor:
        return 2

    print 'Working on (%s).' % sensor

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
            # Initialize verbose logging
            logInputs, logWhatElse, logVerify = startLogging()
            recordInputs( logInputs )
            try:
                processDatax(parameters['somePattern'], logWhatElse)
            except Exception, e:
                # Log error
                logging.error( e.message )
           
            return 0
    print_usage()  

# run main with cmd line args and return exit code
if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))