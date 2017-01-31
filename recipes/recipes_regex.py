#!/usr/bin/env python

import re
import datetime
from dateutil import parser

def ymd_tuple_to_string(t):
    """ return 'yyyy_mm_dd' given tuple like ('yyyy','mm','dd') """
    return '%s_%s_%s' % t

def paths_to_ymd_string_list(paths, pattern):
    """ return list like ['yyyy_mm_dd',etc.] given a list of paths that
    presumably have yearYYYY/monthMM/dayDD """
    se = re.compile(pattern).search
    return [ymd_tuple_to_string(m.group(1,2,3)) for p in paths for m in [se(p)] if m]

def demo_paths():
    paths = ['monkey/year2012/month01/day02/after','two/year12345/later','start/year2011/month09/day03/done']
    pattern = 'year(\d{4})/month(\d{2})/day(\d{2})'
    L = paths_to_ymd_string_list(paths,pattern)  
    print L

def get_icu_telem_data(s):
    search_pat = re.compile('(.*)\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(.*)').search
    m = search_pat(s)
    icustr, dtm, temp = m.group(1,2,3)
    return icustr, parser.parse(dtm), float(temp)

def demo_icu():
    s = 'icu-f01\t2013-01-18 13:48:21\t24.4873'
    icu_name, icu_timestamp, icu_out_air_temp = get_icu_telem_data(s)
    print icu_name, icu_timestamp, icu_out_air_temp

def get_data_end_time(fname):
    # see recipes_fileutils.py
    #fname = '/tmp/pad/year2013/month06/day27/sams2_accel_121f02/2013_06_27_17_29_14.984+2013_06_27_17_30_14.983.121f02.header'
    #print get_fulltime_list(fname)
    search_pat = re.compile('.*(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3}).*').search
    m = search_pat(fname)
    data_time = m.group(1)
    return datetime.datetime.strptime(data_time,'%Y_%m_%d_%H_%M_%S.%f')

if __name__ == '__main__':
    #demo_paths()
    demo_icu()
