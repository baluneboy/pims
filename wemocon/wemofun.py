#!/usr/bin/python

import sys
import time
import datetime
import timeit
import pywemo
from pims.lib.timeout import run_with_timeout

def do_wemo(target='the light', action='toggle', max_iter=9):
    success = False
    count = 0
    for i in range(max_iter):
        devices = pywemo.discover_devices()
        count += 1
        target_device = [ x for x in devices if x.name == target ]
        if target_device:

            devname = target_device[0].name
            # FIXME we should extend device object to have a blink method (with num_cycles and duty_cycle)
            result = getattr(target_device[0], action)()
            #time.sleep(2)
            #result = getattr(target_device[0], action)()
            success = True
            break
        time.sleep(0.1)
    return count, devname, success

def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

if __name__ == "__main__":
    
    #target = 'the light'
    #action = 'toggle'
    #timeout = 6
    
    target, action, timeout = sys.argv[1], sys.argv[2], int(sys.argv[3])
    
    strtime = datetime.datetime.now().strftime('%A, %d-%b-%Y, at %H:%M:%S')
    
    start_time = timeit.default_timer()
    count, devname, success = run_with_timeout(do_wemo, timeout, target=target, action=action)
    num_sec = timeit.default_timer() - start_time
    
    if success:
        print "Starting on %s, after %.2f seconds and %d iterations, found device named '%s' and did action '%s'." % (strtime, num_sec, count, devname, action)
    else:
        print "Starting on %s, after %.2f seconds and %d iterations, COULD NOT FIND THE DEVICE NAMED '%s' to do action '%s'." % (strtime, num_sec, count, devname, action)
    