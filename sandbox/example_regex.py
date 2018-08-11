#!/usr/bin/env python

import re


_RTS_DRAWER_PATTERN = "(?P<prefix>.*)_(?P<drawer>d1|d2)_(?P<variable>current|temperature).csv"


def parse_params(csvfile_bname):
    '''return tuple (drawer, variable) parsed from bname to get drawer designation (d1|d2) & variable (current|temp)'''
    m = re.match(_RTS_DRAWER_PATTERN, csvfile_bname)
    if m:
        prefix = m.group('prefix')
        drawer = m.group('drawer')
        variable = m.group('variable')
    else:
        prefix, drawer, variable = None, None, None
    return prefix, drawer, variable


if __name__ == '__main__':

    csvfile_bname = '2018_08_01_d2_current.csv'
    prefix, drawer, variable = parse_params(csvfile_bname)
    print prefix, drawer, variable
