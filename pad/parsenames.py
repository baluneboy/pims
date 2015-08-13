#!/usr/bin/env python

import re
import sys

from pims.patterns.dirnames import _HEADER_PATTERN

def match_header_filename(full_name, pattern=_HEADER_PATTERN):
    """
    Parse header filename into parts.
    >>> m = match_header_filename('/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f03/2013_01_02_00_01_02.210+2013_01_02_00_11_02.214.121f03.header')
    >>> m.group('sensor_dir')
    '/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f03'
    >>> m.group('pad_dir')
    '/misc/yoda/pub/pad'
    >>> m.group('sensor_subdir')
    'sams2_accel_121f03'
    >>> m.group('system')
    'sams2'
    >>> m.group('start_str')
    '2013_01_02_00_01_02.210'
    >>> m.group('Y1')
    '2013'
    >>> m.group('M1')
    '01'
    >>> m.group('D1')
    '02'
    >>> m.group('h1')
    '00'
    >>> m.group('m1')
    '01'
    >>> m.group('s1')
    '02'
    >>> m.group('ms1')
    '210'
    >>> m.group('pm')
    '+'
    >>> m.group('stop_str')
    '2013_01_02_00_11_02.214'
    >>> m.group('Y2')
    '2013'
    >>> m.group('M2')
    '01'
    >>> m.group('D2')
    '02'
    >>> m.group('h2')
    '00'
    >>> m.group('m2')
    '11'
    >>> m.group('s2')
    '02'
    >>> m.group('ms2')
    '214'
    >>> m.group('sensor')    
    '121f03'
    
    """
    return re.search( re.compile(pattern), full_name )

def pad_start_stop(fname):
    from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop, format_datetime_as_pad_underscores    
    start, stop = pad_fullfilestr_to_start_stop(fname)
    return start, stop

def pad_stop(fname):
    start, stop = pad_start_stop(fname)
    return stop

def remedy_start(fname):
    import datetime
    start, stop = pad_start_stop(fname)   
    remedy_start = stop + datetime.timedelta(seconds=1)
    return remedy_start
    
if __name__ == "__main__":
    if len(sys.argv) == 1:
        import doctest
        doctest.testmod(verbose=True)
    elif len(sys.argv) == 3:
        from pims.utils.pimsdateutil import format_datetime_as_pad_underscores    
        fname = sys.argv[2]
        gmt = eval( sys.argv[1] + "('" + fname + "')" )
        print format_datetime_as_pad_underscores(gmt)
