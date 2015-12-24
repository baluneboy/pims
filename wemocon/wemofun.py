#!/usr/bin/python

from pims.lib.timeout import run_with_timeout

def simple_test(*args, **kwargs):
    import time   
    if 'delay' in kwargs:
        time.sleep(kwargs['delay'])
    s = ''
    for (ind, arg) in enumerate(args):
        s += "arg %d is: %s, " % (ind, str(arg))
    for key in kwargs:
        s += "keyword['%s'] = %s, " % (key, kwargs[key])
    return s.rstrip(', ')

if __name__ == "__main__":
    func = simple_test
    timeout = 2
    run_with_timeout(func, timeout, 'uno',   400, dog='meat')
    run_with_timeout(func, timeout, 'dos', 888, read=None, delay=1)
    run_with_timeout(func, timeout, 9.81,  0.1, read=None, delay=3)