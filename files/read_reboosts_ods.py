#!/usr/bin/env python

import os
import pyexcel as pe
from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.files.utils import get_immediate_subdirs


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# strSuffix = 'Progress_69P_Reboost_2018-06-23';
# strTig = '23-Jun-2018 08:15:00';
# strDur = '00:03:28';
# popmainreboost(strSuffix, strTig, strDur);
#


def get_tig(t):
    """strTig = '12-May-2018 22:07:00';"""
    return t


def get_dur(d):
    """strDur = '00:02:52';"""
    return d


sheet = pe.get_sheet(file_name='/home/pims/Documents/reboosts.ods')
row_count = 0
for row in sheet:
    if row_count > 0:  # skip first (header) row
        if row[0] is '':  # skip if first column in this row is empty
            row_count += 1
            continue
        date_str = row[0].strftime('%Y-%m-%d')
        ymd_path_str = datetime_to_ymd_path(row[0])
        if os.path.exists(ymd_path_str):
            subdirs = get_immediate_subdirs(ymd_path_str)
            accel_systems = set([s.split('_')[0] for s in subdirs])
            if 'sams2' in accel_systems:
                tig = get_tig(row[4])
                dur = get_dur(row[5])
                print '[*] Row: %03d Date: %s %s TIG: %s, DUR: %s' % (row_count, date_str, ymd_path_str, tig, dur)
            else:
                print '[ ] Row: %03d Date: %s %s DOES NOT HAVE sams2' % (row_count, date_str, ymd_path_str)
        else:
            print '[ ] Row: %03d Date: %s %s DOES NOT EXIST' % (row_count, date_str, ymd_path_str)
    row_count += 1
