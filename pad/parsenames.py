#!/usr/bin/env python

import re
from pims.patterns.dirnames import _HEADER_PATTERN

def match_header_filename(full_name):
    """
    Parse header filename into parts.
    >>> m = match_header_filename('/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f03/2013_01_02_00_01_02.210+2013_01_02_00_11_02.214.121f03.header')
    >>> m.group('sensor_subdir')
    'sams2_accel_121f03'
    >>> m.group('Y2')
    '2013'
    
    """
    return re.search( re.compile(_HEADER_PATTERN), full_name )
    
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    