#!/usr/bin/env python

def dict_as_str(d):
    """show the dict sorted by keys as string"""
    s = ''
    keys = d.keys()
    keys.sort()
    maxlen = max(len(x) for x in keys)  # find max length
    fmt = '{0:<%ds} : {1:s}\n' % maxlen
    for k in keys:
        s += fmt.format( k, str(d[k]) )
    return s

d = {'one':1, "two too to too too":2}
print dict_as_str(d)