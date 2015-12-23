#!/usr/bin/python

import signal
import time

def test_request(arg=None):
    """Your request goes here."""
    time.sleep(2)
    return arg

def test_args_kwargs(func, *args, **kwargs):
    print "func:", func
    for (ind, arg) in enumerate(args):
        print "arg %d is:" % ind, arg
    for key in kwargs:
        print "keyword arg: %s: %s" % (key, kwargs[key])
    return "F I N I S H E D"
 
class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass
 
    def __init__(self, sec):
        self.sec = sec
 
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)
 
    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm
 
    def raise_timeout(self, *args):
        raise Timeout.Timeout()
 
def main():
    # Run blocks of code with separate timeouts
    try:

        with Timeout(4):
            out = test_args_kwargs(zip, 1, 'two', myarg3="three", myarg4=4.0)
            print out
            
        with Timeout(3):
            print test_request("Request 1")
            test_args_kwargs(zip, 1, 'two', myarg3="three", myarg4=4.0)

        with Timeout(1):
            print test_request("Request 2")
            test_args_kwargs(map, 2, 'two', myarg3="threepeat", myarg4=44)            

    except Timeout.Timeout:
        print "Timeout"
 
#############################################################################
 
if __name__ == "__main__":
    main()