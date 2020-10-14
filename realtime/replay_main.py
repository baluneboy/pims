#!/usr/bin/env python

import os
import sys
import logging
import logging.config
import glob
import datetime
from dateutil import parser
from datetimeranger import DateRange
import pandas as pd
from pims.utils.commands import timeLogRun
from pims.files.utils import listdir_filename_pattern
from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.database.pimsquery import get_db_count, get_last_gmt
from pims.realtime.replay_helper import get_host_sensor_pairs
from pims.files.filter_pipeline import FileFilterPipeline, DateRangePadFile, MatchSensorPad
from pims.utils.pimsdateutil import start_stop_to_pad_fullfilestr


_TWO_DAYS_AGO = str(datetime.datetime.now().date() - datetime.timedelta(days=2))


# input parameters
defaults = {
'gap_start':    '2020-01-01 11:22:30', # like '2020-01-01 11:22:30'
'gap_stop':     '2020-01-01 11:22:33', # like '2020-01-01 11:22:33'
}
parameters = defaults.copy()


def params_ok():
    """check for reasonableness of parameters entered on command line"""
    # parse start/stop
    try:
        parameters['gap_start'] = parser.parse( parameters['gap_start'] )
        parameters['gap_stop'] = parser.parse( parameters['gap_stop'] )
    except ValueError, e:
        log.error('Bad input trying to parse date got ValueError: "%s"' % e.message )
        return False

    return True


def print_usage():
    """print short description of how to run the program"""
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])


def show_counts(start, stop, host_sensor_pairs):
    schema = 'pims'
    print '-' * 95, '\ncount records from each db table in gap range from %s to %s:\n' % (start, stop), '-' * 95
    for t in host_sensor_pairs:
        host, sensor = t[0], t[1]
        c = get_db_count(host, schema, sensor, start, stop)
        print c, sensor


def show_pad_boundaries(gstart, gstop, host_sensor_pairs):
    schema = 'pims'
    print '-' * 95, '\ncount records from each db table in gap range from %s to %s:\n' % (gstart, gstop), '-' * 95
    for t in host_sensor_pairs:
        host, sensor = t[0], t[1]
        c = get_db_count(host, schema, sensor, gstart, gstop)
        print c, sensor


def get_last_times(host_sensor_pairs):
    print '-' * 33, '\nmax(time) from each db table:\n', '-' * 33
    for t in host_sensor_pairs:
        host, sensor = t[0], t[1]
        max_time = get_last_gmt(host, 'pims', sensor=sensor)
        print max_time, sensor


def get_files(sensor, dstart, dstop):
    prefix = 'sams*_accel_'
    my_dir_pat = os.path.dirname(start_stop_to_pad_fullfilestr(dstart, dstop, subdir_prefix=prefix, sensor=sensor))
    wild_path = os.path.join(my_dir_pat, '*header')
    return glob.glob(wild_path)


def main(argv):
    """describe what this routine does here"""
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if 2 != len(pair):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if params_ok():
            try:
                host_sensor_pairs = get_host_sensor_pairs()

                # fnames = get_files('121f02', parameters['gap_start'], parameters['gap_stop'])
                # print fnames[0]
                # print fnames[-1]
                #
                # prev_day = parameters['gap_start'] - datetime.timedelta(days=1)
                # next_day = parameters['gap_stop'] + datetime.timedelta(days=1)
                #
                # sensor, start, stop = '121f02', prev_day.date(), next_day.date()
                # ffp = FileFilterPipeline(DateRangePadFile(start, stop), MatchSensorPad(sensor))
                # fnames = []
                # for d in pd.date_range(start=prev_day.date(), end=next_day.date(), freq='D'):
                #     print d
                #     filenames = glob.glob(wild_path)
                #     for f in ffp(filenames):
                #         print f

                get_last_times(host_sensor_pairs)
                raw_input('%s\nNow replay data from CU, then press Enter to continue...' % ('-' * 95, ))
                show_counts(parameters['gap_start'], parameters['gap_stop'], host_sensor_pairs)
                show_pad_boundaries(parameters['gap_start'], parameters['gap_stop'], host_sensor_pairs)
                print 'done'
            except Exception, e:
                return -1
            return 0
    print_usage()  


if __name__ == '__main__':
    sys.exit(main(sys.argv))
