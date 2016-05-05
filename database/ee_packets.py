#!/usr/bin/env python

# SEE /misc/manbearpig/home/pims/dev/programs/python/pims/realtime/dbstatus_activesensors.py

import sys
import time
import datetime

from pims.utils.pimsdateutil import dtm2unix
from pims.database.pimsquery import get_ee_table_list, delete_older_ee_packets
from pims.database.pimsquery import get_dbstatusish_details_for_ee, get_sensor_location_from_kyle

EEPKT_HOST = 'jimmy'
EEPKT_RATE = 1.0

def prune(table_list):
    for t in table_list:
        delete_older_ee_packets(t)

def dbstat(host, table_list):
    for t in table_list:
        count, tmin, tmax = get_dbstatusish_details_for_ee(t, host=host)
        age = time.time() - dtm2unix(tmax)
        loc = get_sensor_location_from_kyle(t, datetime.datetime.now())     
        return t, count, tmin, tmax, age, EEPKT_RATE, loc
    
def main(argv):
    """switchyard: {prune | dbstat}"""
    
    if len(argv) == 1:
        print 'no arguments, so quit'
        return 1
    
    # arg1 of prune, delete recs to just keep most recent [for hourly]
    action = argv[1]
    tables = get_ee_table_list()
    if action == 'prune':
        prune(tables)
    elif action == 'dbstat':
        dbstat(EEPKT_HOST, tables)
    else:
        print 'unrecognized argument %s' % action
        return 2
    
    return 0

if __name__ == '__main__':   
    sys.exit(main(sys.argv))