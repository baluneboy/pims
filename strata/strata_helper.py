#!/usr/bin/env python

from dateutil import parser
from pims.files.pdfs.pdfjam import flipbook_roadmap

STRATA_MSID_MAP = {
    'UEZE13RT0005U': 'ER8_CYCLE_COUNTER',
    'status'       : 'ER8_CYCLE_COUNTER_STATUS',
    'UEZE13RT1385C': 'STRATA_CURRENT',
    'status.1'     : 'STRATA_CURRENT_STATUS',
    'UEZE13RT1386C': 'POLAR2_CURRENT',
    'status.2'     : 'POLAR2_CURRENT_STATUS',
    'UEZE13RT1554J': 'STRATA_ENABLED',
    'status.3'     : 'STRATA_ENABLED_STATUS',
    'UEZE13RT1874J': 'REBOOT_BIT',
    'status.4'     : 'REBOOT_BIT_STATUS',
    }


def normalize_generic(v, one_list, zero_list):
    """generic normalize to get one/zero instead of on/off or closed/opened"""
    
    if isinstance(v, float) and np.isnan(v):
        return 0
    elif v.lower() in zero_list:
        return 0
    elif v.lower() in one_list:
        return 1
    else:
        return np.nan

def strata_flipbook(day1, day2, sensor='121f04', plotax='spgs', out_dir='/misc/yoda/www/plots/user/strata/roadmap_flipbook'):
    d1 = parser.parse(day1)
    d2 = parser.parse(day2)
    print d1
    print d2
    flipbook_roadmap(d1, d2, sensor, plotax, out_dir)
  
    