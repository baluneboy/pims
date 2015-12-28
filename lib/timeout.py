#!/usr/bin/python

import time
import signal
from pims.lib.timed import timed

# FIXME this does not work as expected with zero for input sec
class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception): pass
 
    def __init__(self, sec):
        self.sec = sec
 
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)
 
    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm
 
    def raise_timeout(self, *args):
        raise Timeout.Timeout()

def run_with_timeout(fun, timeout, *args, **kwargs):
    # Run fun in under timeout seconds or bail out
    out = None
    try:
        with Timeout(timeout):
            out = fun(*args, **kwargs)
            #print "OUTPUT FROM %s:" % fun.__name__, out
    except Timeout.Timeout:
        out = 'TIMEOUT VALUE OF %d SECONDS WAS REACHED FOR %s' % (timeout, fun.__name__)
    return out


@timed
def verbose_run_with_timeout(fun, timeout, *args, **kwargs):
    return run_with_timeout(fun, timeout, *args, **kwargs)

 
#############################################################################

def test_request(arg=None):
    """Your request goes here."""
    time.sleep(2)
    return arg

def show_args_kwargs(*args, **kwargs):
    if 'delay' in kwargs:
        time.sleep(kwargs['delay'])
    s = ''
    for (ind, arg) in enumerate(args):
        s += "arg %d is: %s, " % (ind, str(arg))

    for key in kwargs:
        s += "keyword['%s'] = %s, " % (key, kwargs[key])

    return s.rstrip(', ')
 
def demo_two():
    
    # Read the comments as running narrative...
    
    # let's start with timeout of 2 seconds...
    timeout = 2
    
    # now run show_args_kwargs without delay (IT COMPLETES WITHOUT TIMEOUT)...
    fun = show_args_kwargs
    print run_with_timeout(fun, timeout, 3.3, dog='meat')
    
    # run same function again, but this time it will delay itself 3 seconds (IT SHOULD TIMEOUT)...
    fun = show_args_kwargs
    print run_with_timeout(fun, timeout, 4.4, 5.6, read=None, delay=3)
    
    # next, run this other function, test_request and since it has built-in sleep of 2 sec (IT SHOULD TIMEOUT)...
    fun = test_request
    print run_with_timeout(fun, timeout, 'Test %s with timeout of %d' %(fun.__name__, timeout))

    # finally, run test_request again with new timeout value (IT COMPLETES WITHOUT TIMEOUT)...
    timeout = 4
    fun = test_request
    print run_with_timeout(fun, timeout, 'Test %s was run now with timeout of %d' % (fun.__name__, timeout))

def demo_one():
    """ simple demo

        >>> timeout = 2
        >>> # let's run show_args_kwargs without delay (IT COMPLETES WITHOUT TIMEOUT)...
        >>> fun = show_args_kwargs
        >>> run_with_timeout(fun, timeout, 3.3, dog='meat')
        OUTPUT FROM show_args_kwargs: arg 0 is: 3.3, keyword['dog'] = meat
        
        >>> # run same function again, but this time it will delay itself 3 seconds (IT SHOULD TIMEOUT)...
        >>> fun = show_args_kwargs
        >>> run_with_timeout(fun, timeout, 4.4, 5.6, read=None, delay=3)
        TIMEOUT VALUE OF 2 SECONDS WAS REACHED FOR show_args_kwargs
        
        >>> # next, run this other function, test_request and since it has built-in sleep of 2 sec (IT SHOULD TIMEOUT)...
        >>> fun = test_request
        >>> run_with_timeout(fun, timeout, 'Test %s with timeout of %d' %(fun, timeout))
        TIMEOUT VALUE OF 2 SECONDS WAS REACHED FOR test_request
        
        >>> # finally, run test_request again with new timeout value (IT COMPLETES WITHOUT TIMEOUT)...
        >>> timeout = 4
        >>> fun = test_request
        >>> run_with_timeout(fun, timeout, 'which was run now with timeout of %d' % timeout)
        OUTPUT FROM test_request: which was run now with timeout of 4
        
    """
    print 'done with simple demo'

if __name__ == "__main__":
    #import doctest
    #doctest.testmod(verbose=True)
    demo_two()
