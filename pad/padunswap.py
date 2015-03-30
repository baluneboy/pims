#!/usr/bin/env python

import sys
from datetime import timedelta
from dateutil import parser

from pims.pad.padcache import PimsDayCache
from pims.pad.parsenames import match_header_filename
from pims.patterns.dirnames import _HEADER_PATTERN_COLUMBUS_SWAP
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop

# identify PAD files that match pattern in GMT range from start to stop
def get_header_files_for_swap(start, stop, pattern):
    """identify PAD files that match pattern in GMT range from start to stop"""
    header_files = []
    day1 = start.date()
    day2 = stop.date()
    while day1 <= day2:
        pdc = PimsDayCache(date=day1, sensorSubDirRx=pattern)
        for h in pdc.headerFiles:
            m = match_header_filename(h, _HEADER_PATTERN_COLUMBUS_SWAP)
            if m:
                fstart, fstop = pad_fullfilestr_to_start_stop(h)
                if (fstart >= start) and (fstop <= stop):
                    header_files.append(h)
        day1 += timedelta(days=1)
    return header_files



if __name__ == '__main__':
    # 2014-12-05/18:19:19 2015-03-13/14:36:01 sams2_accel_121f0[28].*
    start = parser.parse( sys.argv[1] )
    stop  = parser.parse( sys.argv[2] )
    pattern = sys.argv[3]
    header_files = get_header_files_for_swap(start, stop, pattern)
    print header_files
    print len(header_files)
