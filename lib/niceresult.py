#!/usr/bin/env python
"""
Graceful handling of exception in result.
"""

import sys


# from http://nedbatchelder.com/blog/200711/rethrowing_exceptions_in_python.html
class NiceResult(object):
    
    """
    It's easy to write code that does the right thing when everything is going
    well. It's much harder to write code that does a good job when things go
    wrong. Properly manipulating exceptions helps.
    
    A problem could be arise that traceback for an exception shows the
    problem starting in e.g. get_result. When debugging problems, it's
    enormously helpful to know their real origin, which might be in e.g. do_work.
    
    To solve that problem, we'll store more than the exception, we'll also store
    the traceback at the time of the original problem, e.g. in get_results, we'll
    use the full three-argument form of the raise statement to use the original
    traceback too!
    
    Now when we run it, the traceback points to do_something_dangerous, called
    from e.g. do_work, which is the real culprit (not from in e.g. get_result)
    
    The three-argument raise statement is a little odd, owing to
    its heritage from the old days of Python when exceptions could be things
    other than instances of subclasses of Exception. This accounts for the odd
    tuple-dance we do on the saved exc_info.
    
    """
    
    def __init__(self, func, params):
        self.func = func
        self.params = params
        self.exc_info = None
        self.result = None
         
    def do_work(self):
        try:
            self.result = self.func(self.params)
        except Exception, e:
             self.exc_info = sys.exc_info()
    
    def get_result(self):
        # odd, heritage tuple dance here
        if self.exc_info: raise self.exc_info[1], None, self.exc_info[2]
        return self.result