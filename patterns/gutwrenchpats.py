#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import inspect

###############################################################################
# handbook (hb) dir pattern
# -----------------------------------------------------------------------------
# like /path/to/SUBDIR where SUBDIR convention is:
# hb_vib_crew_Exercise_Device_2017-01-08
# 1  2   3    4               5  
# ┬  ┬   ┬    ┬               ┬
# │  │   │    │               │
# │  │   │    │               │
# │  │   │    │               └──── 5: date (YYYY-mm-dd)
# │  │   │    └──────────────────── 4: title (underscore-delimited titlecase)
# │  │   └───────────────────────── 3: category {crew|vehicle|equipment}
# │  └───────────────────────────── 2: regime {vib|qs}
# └──────────────────────────────── 1: id {hb|HB}
###############################################################################
_GUTWRENCH_HBDIR_PATTERN = (
    "(?P<thepath>.*)/"                          # the path to start slash
    "(?P<id>hb|HB)_"                            # enum for id underscore
    "(?P<regime>vib|qs)_"                       # enum for regime underscore
    "(?P<category>crew|vehicle|equipment)_"     # enum for category underscore
    "(?P<title>(?:[A-Z][^\s_]*[\s_]?)+)_"       # underscore-delim title case underscore
    "(?P<date>\d{4}-\d{2}-\d{2})\Z"             # YYYY-mm-dd digits for ymd h
    )


###############################################################################
# roadmap day (map) dir pattern
# -----------------------------------------------------------------------------
# like /path/to/SUBDIR where SUBDIR convention is:
# map_Exercise_Device_2017-01-08
# 1   2               3
# ┬   ┬               ┬
# │   │               │
# │   │               │
# │   │               │
# │   │               │
# │   │               └───────────── 3: date (YYYY-mm-dd)
# │   └───────────────────────────── 2: title (underscore-delimited titlecase)
# └───────────────────────────────── 1: id {map|MAP}
_GUTWRENCH_MAPDIR_PATTERN = (
    "(?P<thepath>.*)/"                          # the path to start slash
    "(?P<id>map|MAP)_"                          # enum for id underscore
    "(?P<title>(?:[A-Z][^\s_]*[\s_]?)+)_"       # underscore-delim title case underscore
    "(?P<date>\d{4}-\d{2}-\d{2})\Z"             # YYYY-mm-dd digits for ymd h
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
    print __all__