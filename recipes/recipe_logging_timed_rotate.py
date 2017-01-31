#!/usr/bin/env python
version = '$Id$'

import os
import sys
import logging, logging.handlers
import datetime
import re
import time

# input parameters
defaults = {
'logPath':       '/misc/yoda/www/plots/user/pims/logs', # the path to log files
'somePath':      '/misc/yoda/pub/pad',      # a path of interest
'dateStart':     '2011_12_23_00_00_00.000', # first data time to process
'daysAgoEnd':    '3',                       # last data time to process (n days ago)
'somePattern':   'sams2_accel_121f0.',      # regular expression pattern to match PAD sensor subdir LIKE "sams2_accel_121f03"
}
parameters = defaults.copy()
#logging.handlers.TimedRotatingFileHandler(filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False)
def startLogging():
    logFile = parameters['logFile']
    logging.basicConfig(filename=logFile, filemode='w', level=logging.DEBUG, format='%(asctime)s,%(name)s,%(levelname)s,%(message)s')

    # Define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # Add rotating log message handler to the logger
    rotatingFileHandler = logging.handlers.TimedRotatingFileHandler(logFile, when='s', interval=7, backupCount=9)

    # Set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-9s: %(levelname)-8s: %(message)s')

    # Tell the handler to use this format
    console.setFormatter(formatter)

    # Add handler to the root logger
    logging.getLogger('').addHandler(console)

    # Now, we can log to the root logger, or any other logger. First the root...
    logging.info('Logging started at %s.', datetime.datetime.now() )

    # Now, define a couple of other loggers which represent areas in this app:
    logInputs = logging.getLogger('INPUTS')
    logWhatElse = logging.getLogger('WHATELSE')
    logVerify = logging.getLogger('VERIFY')
    
    # Add each to handler
    logInputs.addHandler(rotatingFileHandler)
    logWhatElse.addHandler(rotatingFileHandler)
    logVerify.addHandler(rotatingFileHandler)

    return logInputs, logWhatElse, logVerify

def parametersOK():
    """check for reasonableness of parameters entered on command line"""    
    parameters['logFile'] = os.path.join( parameters['logPath'], os.path.basename(__file__).replace('.py','.log') )

    if not os.path.exists(parameters['somePath']):
        print 'the path (%s) does not exist' % parameters['somePath']
        return 0

    parameters['daysAgoEnd'] = int(parameters['daysAgoEnd'])

    return 1 # all OK; otherwise, return 0 above

def printUsage():
    """print short description of how to run the program"""
    print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def processData(sensor, logProcess):
    """explain this where the real work is done"""
    
    if not sensor:
        logging.warn( 'nothing to do for (%s)' % sensor )
        return 2

    logging.info( 'Working on (%s).' % sensor )
    
    count = 0
    maxCount = 3
    while count < maxCount:
        # process data goes here
        time.sleep(2)
        logProcess.info('Something informative about the process.')
        count += 1

    logging.info( 'Done working on (%s).' % sensor )

def recordInputs( logInps ):
    logInps.info( '='*44 )
    for k,v in parameters.iteritems():
        logInps.info( k + ':' + str(v) )
    logInps.info( '='*44 )

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
            # Initialize verbose logging
            logInputs, logWhatElse, logVerify = startLogging()
            recordInputs( logInputs )
            try:
                processData(parameters['somePattern'], logWhatElse)
            except Exception, e:
                # Log error
                logging.error( e.message )
           
            return 0
    printUsage()  

if __name__ == '__main__':
    sys.exit(main(sys.argv))