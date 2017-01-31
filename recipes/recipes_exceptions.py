#!/usr/bin/env python

""" Shows how to re-raise an original exception first, and handle the clean up
in a try:finally block. This construction prevents the original exception from
being overwritten by the latter, and preserves the full stack in the traceback.
"""

import sys
import logging
import traceback
import datetime

class StackException( Exception ): pass 
class EmptyStackException( StackException ): pass 
class StackOverflowException( StackException ): pass

def throws(n):
    if   n == 1: raise RuntimeError('RuntimeError from throws (n=1)')
    elif n == 2: raise StackException('StackException from throws (n=2)')
    elif n == 3: raise EmptyStackException('EmptyStackException from throws (n=3)')
    elif n == 4: raise StackOverflowException('StackException from throws (n=4)')
    else: raise Exception('Exception from throws (n value of %d is unhandled)' % n)
    
def nested(n):
    logMessages = []
    try:
        throws(n)
    except StackException, stack_error:
        if isinstance(stack_error, EmptyStackException):
            print 'HANDLING EMPTY ERROR'
        elif isinstance(stack_error, StackOverflowException):
            msg = 'HANDLING OVERFLOW ERROR'
            print msg
            logMessages.append(msg) # the only message that gets into log
        else:
            print 'HANDLING GENERIC STACK ERROR (NOT EMPTY, NOT OVERFLOW)'
    except Exception, original_error:
        try:
            raise
        finally:
            try:
                cleanup()
            except:
                print 'THERE WAS AN ERROR IN CLEANUP, BUT WE IGNORED IT.'
                pass # ignore errors in cleanup
    return logMessages

def cleanup():
    raise RuntimeError('error from cleanup') # this gets ignored

def mainWithLog(n):
    logger = logging.getLogger('myapp')
    handler = logging.FileHandler('/var/tmp/myapp.log')
    formatter = logging.Formatter('\n**********\n%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler) 
    logger.setLevel(logging.INFO)
    try:
        logMessages = nested(n)
        [logger.info(msg) for msg in logMessages]
        return 0
    except Exception, err:
        logger.exception(err)
        return 1

def main(n):
    try:
        nested(n)
        return 0
    except Exception, err:
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    n = int(sys.argv[1])
    mainWithLog(n)
    # main(n)