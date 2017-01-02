#!/usr/bin/env python

"""Enforce clarity with keyword arguments.  Use kwargs pop to achieve this."""

def safe_division(number, divisor, **kwargs):
    """Do something with message and a timestamp.
    
    Args:
        message: string message to do something with
        when: datetime of when for this message (if None, then default to now)
    """
    ignore_zero_div = kwargs.pop('ignore_zero_div', False)
    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)
    try:
        return number / divisor
    except ZeroDivisionError:
        if ignore_zero_div:
            return float('inf')
        else:
            raise
    
if __name__ == "__main__":
    
    # INTEGER division
    print safe_division(1, 10)

    # FLOAT division
    print safe_division(1.0, 10)
    
    print 'ignoring ZeroDivisionError gives: ', 
    print safe_division(1, 0, ignore_zero_div=True)
    
    #print safe_division(1, 0, my_bad=7, ignore_zero_div=True) # << THIS GIVES "Unexpected blah blah..."
    
    print safe_division(1, 0, ignore_zero_div=False)
    