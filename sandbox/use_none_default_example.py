#!/usr/bin/env python

"""Use None and Docstrings to specify dynamic default arguments."""

import datetime

def my_fun(message, when=None):
    """Do something with message and a timestamp.
    
    Args:
        message: string message to do something with
        when: datetime of when for this message (if None, then default to now)
    """
    when = datetime.datetime.now() if when is None else when
    print '%s: %s' % (when.strftime('%Y-%m-%d, %H:%M:%S'), message)
    
if __name__ == "__main__":
    
    # use default for when (now)
    my_fun('first message')
    
    # explicilty specify when for timestamp
    my_fun('second message', when=datetime.datetime(2016, 5, 11, 7, 28, 33, 123456))
    
    # sloppily specify when without keyword equals
    my_fun('second message', datetime.datetime(2016, 5, 11, 7, 28, 44, 123456))
    
    # sloppy call without keyword equals for when
    my_fun('second message', None)
