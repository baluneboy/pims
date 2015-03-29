#!/usr/bin/env python

from commands import getoutput
from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop

# ls /misc/yoda/pub/pad/year2015/month01/day24/*_accel_121f02006/*.header | tail -1

# get newest PAD header file for given (date, sensor)
def newest_pad_header_file(dtm, sensor):
    """get newest PAD header file for given (date, sensor)
    
    >>> import datetime
    >>> d = datetime.datetime(2014,9,12,12,13,14,0)
    >>> sensor = '121f02006'
    >>> print newest_pad_header_file(d, sensor)
    /misc/yoda/pub/pad/year2014/month09/day12/sams2_accel_121f02006/2014_09_12_23_26_32.312-2014_09_12_23_56_32.319.121f02006.header
    """
    sensor_path = datetime_to_ymd_path(dtm) + '/*_accel_%s/*.header' % sensor
    cmdstr = 'ls ' + sensor_path + ' | tail -1'
    return getoutput(cmdstr)

# get newest pad header file endtime for given (date, sensor)
def newest_pad_header_file_endtime(dtm, sensor):
    """get newest pad header file endtime for given (date, sensor)
    
    >>> import datetime
    >>> d = datetime.datetime(2014,9,12,12,13,14,0)
    >>> sensor = '121f02006'
    >>> print newest_pad_header_file_endtime(d, sensor)
    2014-09-12 23:56:32.319000
    """
    newest = newest_pad_header_file(dtm, sensor)
    if newest.endswith('No such file or directory'):
        return None
    t1, t2 = pad_fullfilestr_to_start_stop(newest)
    return t2

def testdoc(verbose=True):
    import doctest
    return doctest.testmod(verbose=verbose)

if __name__ == "__main__":
    testdoc(verbose=True)