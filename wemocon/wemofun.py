#!/usr/bin/python

import sys
import time
import datetime
import timeit
import pywemo
from pims.lib.timeout import verbose_run_with_timeout

# input parameters
defaults = {
'target':        'the light',   # string for name of target device
'action':        'toggle',      # string corresponding to device method to be called
'timeout':       '10',          # converts to integer number of seconds for timeout period
'max_iter':      '5',           # converts to integer for max # tries at discovering wemo devices
}
parameters = defaults.copy()

def do_wemo(target='the light', action='toggle', max_iter=9):
    count = 0
    success = False
    for i in range(max_iter):
        devices = pywemo.discover_devices()
        #print devices
        count += 1
        target_device = [ x for x in devices if x.name == target ]
        if len(target_device) == 1:
            dev = target_device[0]
            # FIXME we should extend device object to have a blink method (with num_cycles and duty_cycle)
            result = getattr(dev, action)() # call target device's method referenced as action
            success = True
            return success, count
    return success, count

def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

def process_inputs(target='the light', action='toggle', timeout=50, max_iter=5):
   
    strtime = datetime.datetime.now().strftime('%a, %d-%b-%Y, at %H:%M:%S')
    tup, timed_str = verbose_run_with_timeout(do_wemo, timeout, target=target, action=action, max_iter=max_iter)

    # FIXME with pythonic handling of timeout yielding "standardized" output    
    if not isinstance(tup, tuple):
        success, count = False, 0
    else:
        success, count = tup[0], tup[1]
    
    outstr = ("SUCCESS" if success else "FAILURE")
    outstr += " %s after %d iterations: " % (strtime, count)
    outstr += timed_str
    
    return outstr

# FIXME with better checking
def parameters_ok():
    """check for reasonableness of parameters entered on command line"""    
    parameters['timeout'] = int(parameters['timeout'])
    parameters['max_iter'] = int(parameters['max_iter'])
    return True # all OK; otherwise, return False before this line

def print_usage():
    """print short description of how to run the program"""
    print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

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
        if parameters_ok():
            #print parameters

            print process_inputs(
                target=parameters['target'],
                action=parameters['action'],
                timeout=parameters['timeout'],
                max_iter=parameters['max_iter']
                )

            return 0
        
    print_usage()  

if __name__ == "__main__":
    main(sys.argv)
