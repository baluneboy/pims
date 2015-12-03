#!/usr/bin/env python

import os
import re
import datetime

from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.files.utils import listdir_filename_pattern
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop
from interval import Interval

# return dirname (or None) for given sensor+suffix on day of datetime, dtm
def get_path_to_sensor(sensor, suffix, dtm):
    """return dirname (or None) for given sensor+suffix on day of datetime, dtm"""
    subdirPattern = '.*_accel_' + sensor + suffix + '$'
    dirpath = datetime_to_ymd_path(dtm)
    dirname = listdir_filename_pattern(dirpath, subdirPattern)
    if len(dirname) == 1:
        # we must have unique dir
        return dirname[0]
    else:
        return None

# return header filename (or None) for given sensor+suffix for datetime, dtm
def get_header_file(sensor, suffix, dtm):
    dirname = get_path_to_sensor(sensor, suffix, dtm)
    headers = listdir_filename_pattern(dirname, '.*header')
    f = pad_fullfilestr_to_start_stop
    intervals = [ Interval(f(x)[0], f(x)[1]) for x in headers ]
    bools = [ dtm in i for i in intervals ]
    #bools = Interval(dtm, dtm) in intervals[0]
    #print bools
    return headers
    
#sensor = '121f03'
#suffix = '006'
#dtm = datetime.datetime(2014, 1, 2, 3, 4, 5)
#dirname = get_path_to_sensor(sensor, suffix, dtm)
#print dirname
#print len(get_header_file(sensor, suffix, dtm))
#raise SystemExit
        
def main(argv):
    """describe what this routine does here"""
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parametersOK():
            run(parameters['start'], parameters['stop'], parameters['subdirpat'])          
            return 0
    printUsage()  

if __name__ == '__main__':
    sys.exit(main(sys.argv))