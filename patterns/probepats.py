#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys, inspect

###############################################################################
# roadmap PDF full path pattern
# -----------------------------------------------------------------------------
# like 2017_01_01_16_00_00.000_121f03one_spgs_roadmaps142.pdf
# where filename convention is:
# 2017_01_01_16_00_00.000_121f03one_spgs_roadmaps142.pdf
# 1                       2         3  4         5  
# ┬                       ┬         ┬  ┬         ┬
# │                       │         │  │         │
# │                       │         │  │         │
# │                       │         │  │         └── 5: digits for new sample rate
# │                       │         │  └──────────── 4: axis (single char like x,y,z,s)
# │                       │         └─────────────── 3: plot type (like spg)
# │                       └───────────────────────── 2: sensor (like 121f03one or 121f05)
# └───────────────────────────────────────────────── 1: YMDhms (underscore delim start which 1/3 of day)
###############################################################################
_ROADMAP_PDF_BLANKS_PATTERN = (
    "(?P<year>\d{4})_(?P<month>\d{2})_(?P<day>\d{2})_"             # underscore-delimited YMD
    "(?P<hour>\d{2})_(?P<minute>\d{2})_(?P<second>\d{2}\.\d{3})_"  # underscore-delimited hms
    "(?P<sensor>SENSOR)_"                                          # SENSOR placeholder underscore
    "(?P<plot>PLOT)(?P<axis>AXIS)_"                                # PLOT placeholder AXIS placeholder underscore
    "roadmaps(?P<fsnew>.*)\.pdf\Z"                                 # roadmaps fsNew dot pdf end of string
)

_ROADMAP_PDF_FILENAME_PATTERN = _ROADMAP_PDF_BLANKS_PATTERN.replace('SENSOR', '.*').replace('PLOT', '.*').replace('AXIS', '\w')


###############################################################################
# ossbtmf roadmap PDF full path pattern
# -----------------------------------------------------------------------------
# like 2016_07_01_00_ossbtmf_roadmap.pdf
# where filename convention is:
# 2016_07_01_00_ossbtmf_roadmap.pdf
# 1             2       3       4    
# ┬             ┬       ┬       ┬    
# │             │       │       │    
# │             │       │       │    
# │             │       │       │    
# │             │       │       └─────── 4: extension
# │             │       └─────────────── 3: roadmap
# │             └─────────────────────── 2: sensor
# └───────────────────────────────────── 1: YMDh
###############################################################################
_OSSBTMF_ROADMAP_PDF_FILENAME_PATTERN = (
    "(?P<year>\d{4})_(?P<month>\d{2})_(?P<day>\d{2})_"             # underscore-delimited YMD
    "(?P<hour>\d{2})_"                                             # hh
    "(?P<sensor>ossbtmf)_"                                         # SENSOR placeholder underscore
    "roadmap\.pdf\Z"                                               # roadmap dot pdf end of string
)


# /misc/yoda/www/plots/batch/year2017/month12/day13
# 2017_12_13_00_00_00_ossbtmf_gvt3_historical_time-shifted_quasi-steady_estimate.csv    
###############################################################################
_QUASISTEADY_ESTIMATE_PDF_PATTERN = (
    "(?P<year>\d{4})_(?P<month>\d{2})_(?P<day>\d{2})_"             # underscore-delimited YMD
    "(?P<hour>\d{2})_(?P<minute>\d{2})_(?P<second>\d{2})_"         # underscore-delimited hms
    "(?P<sensor>ossbtmf)_"                                         # SENSOR placeholder underscore
    "(?P<plot>gvt)(?P<axis>3)_"                                    # PLOT placeholder AXIS placeholder underscore
    "historical_time-shifted_quasi-steady_estimate\.pdf\Z"         # roadmaps fsNew dot pdf end of string
)


def is_underscore_pattern(text):
    """return boolean (True) for match of 'underscore pattern' string"""
    if not isinstance(text, str): return False
    ismatch = False
    pattern = '\A_[\w_]*_PATTERN\Z' # <<<<< YOUR VAR NAMES FOR PATTERNS MUST MATCH THIS
    if re.search(pattern, text):
        ismatch = True
    return ismatch


def _get_underscore_pattern_varnames(predicate=is_underscore_pattern):
    """return list of underscore patterns from this module"""
    tup_list = inspect.getmembers(sys.modules[__name__])
    var_names = [ tup[0] for tup in tup_list ]
    uscore_pats = [ x for x in var_names if isinstance(x, str) and predicate(x) ]
    return uscore_pats


__all__ = _get_underscore_pattern_varnames()

if __name__ == '__main__':
    print(__all__)