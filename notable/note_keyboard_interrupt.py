#!/usr/bin/env python

"""handle keyboard interrupt, Ctrl-C, via 2 approaches"""

import sys
import time
import signal
import datetime

def signal_handler(signum, frame):
    print "\nThis is the custom interrupt handler.  Bye!"
    sys.exit(3)

def long_running_process():
    while True:
        print datetime.datetime.now(), " whenever, type Ctrl-C to interrupt..."
        time.sleep(1)

def main_one():
    # try/catch approach
    try:
        print 'use try/catch approach:'
        long_running_process()   
    except KeyboardInterrupt:
        print "\ninterrupt received, no custom handler, proceeding..."
    
    # or you can use a custom handler
    signal.signal(signal.SIGINT, signal_handler)
    print 'use custom handler approach:'
    long_running_process()

def main_two():

    data_for_signal_handler = 10

    def internal_signal_handler(*args):
        print
        print data_for_signal_handler
        sys.exit(4)

    signal.signal(signal.SIGINT, internal_signal_handler) # Or whatever signal

    while True:
        data_for_signal_handler += 1
        print datetime.datetime.now(), "type Ctrl-C to interrupt..."
        time.sleep(1)

class BreakHandler:
    """Trap CTRL-C, set a flag, and keep going.
    
    This is very useful for gracefully exiting database loops while simulating
    transactions.
 
    To use this, make an instance and then enable it.  You can check
    whether a break was trapped using the trapped property.
 
    # EXAMPLE
    # If CTRL+C is detected at the start of the loop, then break is
    # called. Next, do_cleanup() runs, and the break handler is disabled, returning
    # things to normal. The idea is that do_thing_1(), do_thing_2(), and
    # do_thing_3() all run to completion, even when the user presses CTRL+C, and
    # do_cleanup() always runs when the loop is exited.
    #
    # Create and enable a break handler to trap a break
    bh = BreakHandler()
    bh.enable()
    for item in big_set:
        if bh.trapped:
            print ' Stopping at user request (keyboard interrupt)...'
            break
        do_thing_1()
        do_thing_2()
        do_thing_3()
    do_cleanup()
    bh.disable()
    
    """
    
    def __init__(self, emphatic=9):
        """Create a new break handler.
 
        @param emphatic: This is the number of times that the user must
                    press break to *disable* the handler.  If you press
                    break this number of times, the handler is automagically
                    disabled, and one more break will trigger an old
                    style keyboard interrupt.  The default is nine.  This
                    is a Good Idea, since if you happen to lose your
                    connection to the handler you can *still* disable it.
        """
        self._count = 0
        self._enabled = False
        self._emphatic = emphatic
        self._oldhandler = None
        return
 
    def _reset(self):
        """
        Reset the trapped status and count.  You should not need to use this
        directly; instead you can disable the handler and then re-enable it.
        This is better, in case someone presses CTRL-C during this operation.
        """
        self._count = 0
        return
 
    def enable(self):
        """
        Enable trapping of the break.  This action also resets the
        handler count and trapped properties.
        """
        if not self._enabled:
            self._reset()
            self._enabled = True
            self._oldhandler = signal.signal(signal.SIGINT, self)
        return
 
    def disable(self):
        """
        Disable trapping the break.  You can check whether a break
        was trapped using the count and trapped properties.
        """
        if self._enabled:
            self._enabled = False
            signal.signal(signal.SIGINT, self._oldhandler)
            self._oldhandler = None
        return
 
    def __call__(self, signame, sf):
        """
        A break just occurred.  Save information about it and keep
        going.
        """
        self._count += 1
        # If we've exceeded the "emphatic" count disable this handler.
        if self._count >= self._emphatic:
            self.disable()
        return
 
    def __del__(self):
        """
        Python is reclaiming this object, so make sure we are disabled.
        """
        self.disable()
        return
 
    @property
    def count(self):
        """
        The number of breaks trapped.
        """
        return self._count
 
    @property
    def trapped(self):
        """
        Whether a break was trapped.
        """
        return self._count > 0

def do_thing_1(i):
    time.sleep(i*0.05)

def do_thing_2(i):
    time.sleep(0.25)

def do_thing_3(i):
    time.sleep(0.5)

def do_cleanup():
    print ' cleaning up'
    
def main_three():
    """
    # If CTRL+C is detected at the start of the loop, then break is
    # called. Next, do_cleanup() runs, and the break handler is disabled, returning
    # things to normal. The idea is that do_thing_1(), do_thing_2(), and
    # do_thing_3() all run to completion, even when the user presses CTRL+C, and
    # do_cleanup() always runs when the loop is exited.
    """
    # Create and enable a break handler to trap a break
    bh = BreakHandler()
    bh.enable()
    for item in range(2):
        if bh.trapped:
            print ' Stopping at user request (keyboard interrupt)...'
            break
        do_thing_1(item)
        do_thing_2(item)
        do_thing_3(item)
    do_cleanup()
    bh.disable()    

if __name__ == '__main__':
    #main_one()
    #main_two()
    main_three()