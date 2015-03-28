#!/usr/bin/env python

import sys
import time
import signal

# custom signal handler
def signal_handler(signal, frame):
    """custom signal handler"""
    print '\nYou pressed Ctrl+C!  Exit with status code = 2.'
    sys.exit(3)

# artifical, long-running process
def long_running_process():
    """artifical, long-running process"""
    print 'Press Ctrl+C'
    while True:
        time.sleep(1)    

# use custom signal handler; note: no try/catch
def demo_one():
    """use custom signal handler; note: no try/catch"""
    
    print "use custom signal handler for SIGINT"
    
    # create custom signal handler for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    
    # now do long-running process
    long_running_process()

# use try/catch; NOT using custom signal handler for SIGINT 
def demo_two():
    """use try/catch; NOT using custom signal handler for SIGINT"""

    print "use try/catch"
    
    try:
        long_running_process()
        
    except KeyboardInterrupt:
        print "\nW: interrupt received, proceeding..."

# need to run in this order; otherwise, we'd exit right after demo_one
demo_two()
demo_one()