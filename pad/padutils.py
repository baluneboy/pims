#!/usr/bin/env python

import os
import re
import datetime

from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.files.utils import listdir_filename_pattern, glob_padheaders, mkdir_p, move_pad_pair
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop
from pims.files.filter_pipeline import FileFilterPipeline, DateRangePadFile
from interval import Interval


def sensor_subdir(sensor):
    """return string for sensor subdir name given sensor designation"""
    if sensor.startswith('121f0'):
        return 'sams2_accel_' + sensor
    elif sensor.startswith('es'):
        return 'samses_accel_' + sensor
    else:
        return 'unknown'


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


def get_header_file(sensor, suffix, dtm):
    """return header filename (or None) for given sensor+suffix for datetime, dtm"""
    dirname = get_path_to_sensor(sensor, suffix, dtm)
    headers = listdir_filename_pattern(dirname, '.*header')
    #f = pad_fullfilestr_to_start_stop
    #intervals = [ Interval(f(x)[0], f(x)[1]) for x in headers ]
    #bools = [ dtm in i for i in intervals ]
    ##bools = Interval(dtm, dtm) in intervals[0]
    ##print bools
    return headers


def pad_quarantiner():
    """TODO implement PAD quarantiner routine to...SEE
    /home/pims/dev/programs/python/pims/pad/readme_padquarantine.txt
    THEN after quarantined, packetWriter from mr-hankey, then do all again for MAMS OSS and HiRAP"""

    ymdpat = r'year2017/month04/day0[89]'
    
    #quarantines = [
    #    ('121f02', datetime.datetime(2017,  4,  8,  8, 33, 30, 673000), datetime.datetime(2017,  4,  9, 20, 34, 50, 758000)),
    #    ('121f03', datetime.datetime(2017,  4,  8,  8, 33, 30, 499000), datetime.datetime(2017,  4,  9, 20, 21, 24, 913000)),
    #    ('121f04', datetime.datetime(2017,  4,  8,  8, 33, 30, 510000), datetime.datetime(2017,  4,  9, 19, 49,  4, 344000)),
    #    ('121f05', datetime.datetime(2017,  4,  8,  8, 33, 30, 527000), datetime.datetime(2017,  4,  9, 20, 33, 34, 653000)),
    #    ('121f08', datetime.datetime(2017,  4,  8,  8, 31, 28, 546000), datetime.datetime(2017,  4,  9, 20, 34, 49, 438000)),
    #    ]

    quarantines = [
        ('hirap',     datetime.datetime(2017,  4,  8,  8, 35, 49, 234000), datetime.datetime(2017,  4,  9, 23, 59, 59, 999000)),
        ('ossbtmf',   datetime.datetime(2017,  4,  8, 10, 36,  8, 000000), datetime.datetime(2017,  4,  9, 23, 59, 59, 999000)),
        ]

    for sensor, start, stop in quarantines:
        subdirpat = r'*ams*_accel_%s*' % sensor
        header_files = glob_padheaders(ymdpat, subdirpat)
        print '\nFound %d matching header files for %s*' % (len(header_files), sensor)
        
        # Initialize processing pipeline (no file list as input yet)
        ffp = FileFilterPipeline(DateRangePadFile(start, stop))
        print ffp
        
        # Apply processing pipeline input #1 (now ffp is callable)
        bad_dirs = []
        quarantined_hdr_files = []
        for f in ffp(header_files):
            quarantined_hdr_files.append(f)
            quarantined_dir = os.path.join( os.path.dirname(f), 'quarantined' )
            if quarantined_dir not in bad_dirs:
                mkdir_p(quarantined_dir)
            move_pad_pair(f, quarantined_dir)
            
        print '%d file pairs for %s* were quarantined' % (len(quarantined_hdr_files), sensor)


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
    #sys.exit(main(sys.argv))
    pad_quarantiner()
