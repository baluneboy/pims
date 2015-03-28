#!/usr/bin/env python
"""Get approx. duration from file timestamps for resample outputs."""

import os
import re
import sys
import datetime
import subprocess
from scipy import stats
from dateutil import parser
from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop

# ls to get file full_time in list
def list_full_time(subdir):
    """ls to get file full_time in list"""
    # LIKE ls --full-time -alrth /PATH/*header
    if not os.path.exists(subdir):
        raise OSError('%s does not exist' % subdir)
    cmd = 'ls --full-time -alrth ' + os.path.join(subdir,'*.header')
    process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = process.communicate()
    splitout = out.split('\n')[:-1] # split on newlines & get rid of very last trailing newline
    return splitout

# return True if bad timestring in either start or stop part of filename
def bad_timestr(fullfilestr):
    """return True if bad timestring in either start or stop part of filename"""
    d1, d2 = pad_fullfilestr_to_start_stop(fullfilestr)
    if not d1:
        print 'bad start part in %s' % fullfilestr
        return True
    if not d2:
        print 'bad stop part in %s' % fullfilestr
        return True
    return False

# print list of subdir, file_timestamp, file_duration
def process(subdir):
    """print list of subdir, file_timestamp, file_duration"""
    listfiles = list_full_time(subdir)
    for line in listfiles:
        s = line.split(' ')
        d = s[5]
        t = s[6][0:8]
        fullfilestr = s[8]
        d1, d2 = pad_fullfilestr_to_start_stop(fullfilestr)
        delta = d2-d1
        print '%s\t%s\t%d' % (subdir, parser.parse(d + ' ' + t), delta.seconds)

# iterate over day directory (sams2 subdirs that end with 006 for now)
def main(daydir):
    """iterate over day directory (sams2 subdirs that end with 006 for now)"""
    # get directories
    subdirs = [ i for i in os.listdir(daydir) if os.path.isdir(os.path.join(daydir, i)) ]
    sams2_subdirs = [ i for i in subdirs if i.startswith('sams2_accel_') ]
    sams2006_subdirs = [ i for i in sams2_subdirs if i.endswith('006') ]    
    check_dirs = [ os.path.join(daydir, sd) for sd in sams2006_subdirs ]
    for sams2dir in check_dirs:
        process(sams2dir)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        d2 = datetime.datetime.now().date() - datetime.timedelta(days=2)
        daydir = datetime_to_ymd_path(d2)
        main(daydir)
    elif len(sys.argv) == 3:
        d1 = datetime.datetime.now().date() - datetime.timedelta(days=int(sys.argv[1]))
        d2 = datetime.datetime.now().date() - datetime.timedelta(days=int(sys.argv[2]))
        d = d1
        while d < d2:
            d += datetime.timedelta(days=1)
            daydir = datetime_to_ymd_path(d)
            main(daydir)
