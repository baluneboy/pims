#!/usr/bin/env python

##############################################################################
# PHASE 1:
# ~/dev/programs/bash/movepads4swap.bash 2014-12-05 2015-03-13
# then manually move ends back up, that is, we want to just...
# ...move F02, F08, F02006, and F08006 PAD files to "beforefixswap" subdir for following GMT range:
# 2014-12-05 18:19:19
# 2015-03-13 14:36:01
# FOR sams2_accel_121f0[28].*

##############################################################################
# PHASE 2:

import os
import re
import sys
from datetime import timedelta
from dateutil import parser

from pims.files.utils import filter_dirnames, filter_filenames
from pims.pad.padcache import PimsDayCache
from pims.pad.parsenames import match_header_filename
from pims.patterns.dirnames import _HEADER_PATTERN_COLUMBUS_SWAP
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop, datetime_to_ymd_path

# identify PAD files that match pattern in GMT range for day within start to stop range
def get_header_files_for_swap(day, start, stop, pattern):
    """identify PAD files that match pattern in GMT range for day within start to stop range"""
    header_files = []
    pdc = PimsDayCache(date=day, sensorSubDirRx=pattern)
    for h in pdc.headerFiles:
        m = match_header_filename(h, _HEADER_PATTERN_COLUMBUS_SWAP)
        if m:
            fstart, fstop = pad_fullfilestr_to_start_stop(h)
            if (fstart >= start) and (fstop <= stop):
                header_files.append(h)
    return header_files

# TODO timeit compare this routine with some subprocess form of...
#      find /misc/yoda/pub/pad/year2015/month01/day01 -type f -name "*header" | grep 121f0[28] | wc -l
#
# find header files for given year/month/day
def find_headers_regexp(ymd_dir, sens_subdir_pat):
    """find header files for given year/month/day matching sensor subdir pattern

    Returns list of header files like:
    >>> sens_subdir_pat = 'sams2_accel_121f0[28].*'
    >>> ymd_dir = '/misc/yoda/pub/pad/year2015/month01/day01'
    
    """
    file_pat = '.*\.header'
    headers = []
    predicate = re.compile(os.path.join(ymd_dir, sens_subdir_pat)).match
    for dirname in filter_dirnames(ymd_dir, predicate):
        file_predicate = re.compile(os.path.join(dirname, file_pat)).match
        for fname in filter_filenames(dirname, file_predicate):
            headers.append(fname)
    return headers

subdirPattern = 'sams2_accel_121f0[28].*'
dirpath = r'/misc/yoda/pub/pad/year2015/month01/day01'
predicate = re.compile(os.path.join(dirpath, subdirPattern)).match
for dirname in filter_dirnames(dirpath, predicate):
    print 'mkdir %s/beforefixswap' % dirname
    print 'mv %s/* %s/beforefixswap/' % (dirname, dirname)
raise SystemExit

def show_headers_tally():
    # NOTE: SWAP TO HAPPEN FROM
    # 2014-12-05/18:19:19  TO
    # 2015-03-13/14:36:01
    # FOR sams2_accel_121f0[28].*

    sens_subdir_pat = 'sams2_accel_121f0[28].*'
    start = parser.parse( '2014-12-05/18:19:19' )
    stop  = parser.parse( '2015-03-13/14:36:01' )    
    day1 = start.date()
    day2 = stop.date()

    hdr_files = []
    while day1 <= day2:
        ymd_dir = datetime_to_ymd_path(day1)
        hdrs = find_headers_regexp(ymd_dir, sens_subdir_pat)
        hdr_files += hdrs
        print day1, len(hdrs), len(hdr_files)
        day1 += timedelta(days=1)
        
show_headers_tally()
raise SystemExit
    
def show_cumulative_list_tally():
    # NOTE: SWAP TO HAPPEN FROM
    # 2014-12-05/18:19:19  TO
    # 2015-03-13/14:36:01
    # FOR sams2_accel_121f0[28].*

    pattern = 'sams2_accel_121f0[28].*'
    start = parser.parse( '2014-12-05/18:19:19' )
    stop  = parser.parse( '2015-03-13/14:36:01' )    
    day1 = start.date()
    day2 = stop.date()

    hdr_files = []
    while day1 <= day2:
        hdrs = get_header_files_for_swap(day1, start, stop, pattern)
        hdr_files += hdrs
        print day1, len(hdr_files)
        day1 += timedelta(days=1)
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
