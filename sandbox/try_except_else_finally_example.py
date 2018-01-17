#!/usr/bin/env python

import sys


def demo_zero_div():
    try:
        x = 1.0 / 0.0
    except Exception, e:
        print 'an exception happened: %s' % e.message
    else:
        print 'the try worked, so this is the else clause'
    finally:
        print 'no matter what, we do clean-up with finally clause'


# from http://nedbatchelder.com/blog/200711/rethrowing_exceptions_in_python.html
class DelayedResult(object):
    
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
    
    def __init__(self):
        self.exc_info = None
        self.result = None
         
    def do_work(self):
        try:
            self.result = self.do_something_dangerous()
        except Exception, e:
             self.exc_info = sys.exc_info()
     
    def do_something_dangerous(self):
        raise Exception("Something bad happened here.")
    
    def get_result(self):
        # odd, heritage tuple dance here
        if self.exc_info: raise self.exc_info[1], None, self.exc_info[2]
        return self.result


# stupid demo example of try catch
demo_zero_div()


print '##################################################'

# use class to get a better feel for try except
dr = DelayedResult()
print 'doing work toward a delayed result'
dr.do_work()
print 'now getting delayed result'
dr.get_result()