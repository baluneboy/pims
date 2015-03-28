#!/usr/bin/env python

import sys
import datetime
import numpy as np
from operator import itemgetter
from pims.database.pimsquery import db_connect
from pims.utils.iterabletools import runlength_blocks
from pims.utils.pimsdateutil import timestr_to_datetime

# input parameters
defaults = {
'start':         '2015_01_15_11_25_00', # first data time to process
'stop':          '2015_01_15_11_45_00', # last data time to process
'sensor':        '121f05', # sensor (table)
'host':          'chef', # db host name
'minsec':        '0',    # use integer >= 0 to show: gap_sec, gap_start, gap_stop for just gaps
                         # use inf to show:          gmt, pkt_count
}
parameters = defaults.copy()

# get time (as GMT) from db table (sensor); nominally 8 per second (like packet rate for 200 Hz cut-off)
def get_db_time(sensor, start, stop, host):
    """get time (as GMT) from db table (sensor); nominally 8 per second (like packet rate for 200 Hz cut-off)"""
    r = db_connect('select from_unixtime(time) as GMT from %s where time > unix_timestamp("%s") and time < unix_timestamp("%s")' % (sensor, start, stop), host)
    results = [ i[0] for i in r ]
    return results

# a generator to get datetimes (every second)
def next_second(dtm_start, dtm_stop):
    dtm = dtm_start
    yield(dtm)
    while dtm < dtm_stop:
        dtm += datetime.timedelta(seconds=1)
        yield(dtm)

# get times into list
def stdin_raw_list():
    L = sys.stdin.readlines()
    
    # strip newline char and get rid of GMT header line
    L = [ i.strip() for i in L if not i.startswith('GMT') ]
    L.sort()
    
    raw_list = runlength_blocks(L)
    return raw_list

# FIXME
def parameters_ok():
    """check for reasonableness of parameters entered on command line"""
    parameters['start_dtm'] = timestr_to_datetime(parameters['start'] + '.000') - datetime.timedelta(seconds=1)
    parameters['start'] = parameters['start_dtm'].strftime('%Y_%m_%d_%H_%M_%S')
    parameters['stop_dtm'] = timestr_to_datetime(parameters['stop'] + '.000') + datetime.timedelta(seconds=1)
    parameters['stop'] = parameters['stop_dtm'].strftime('%Y_%m_%d_%H_%M_%S')
    
    # coerce minsec to usable value
    parameters['minsec'] = float(parameters['minsec'])
    
    return True # all OK; otherwise, return False before this line

def print_usage():
    """print short description of how to run the program"""
    print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def process_data(sensor):
    """explain this where the real work is done"""
    pass

def fill_gmt_range(gmt_npkts, start_dtm, stop_dtm):
    delta = stop_dtm - start_dtm
    numsecs = delta.seconds
    gmtfill = [ stop_dtm - datetime.timedelta(seconds=x) for x in range(0, numsecs + 1)]
    idx = list( np.where( [ i not in dict(gmt_npkts) for i in gmtfill ] )[0] )
    x = gmt_npkts + [ (gmtfill[i],0) for i in idx ]
    x.sort()
    return x

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
        if parameters_ok():
            results = get_db_time(parameters['sensor'], parameters['start'], parameters['stop'], parameters['host'])
            results.sort()
            raw_list = runlength_blocks(results)            
            
            # list of tuples (GMT, runlength)
            gmt_npkts = [ (i[2], i[1] - i[0] + 1) for i in raw_list ]
            
            # fill in where GMTs might be missing
            out = fill_gmt_range(gmt_npkts, parameters['start_dtm'], parameters['stop_dtm'])
            
            # get rid of cushion/margin values
            out = out[1:-1]
            
            # branch based on gap minsec duration
            if parameters['minsec'] == float('inf'):
                # show all (GMT,numPkts) values
                print 'gmt,pkt_count'
                for gmt, count in out:
                    print '%s,%d' % (gmt, count)                
            else:
                # show gaps one line per gap
                print 'gap_sec,gap_start,gap_stop'
                counts = [ i[1] for i in out ]
                runblock_counts = runlength_blocks(counts)
                idx_gaps = [ i[0:-1] for i in runblock_counts if i[2] == 0 ]
                #print counts
                #print runblock_counts
                for idx in idx_gaps:
                    gap_start = out[ idx[0] ][0]
                    gap_stop =  out[ idx[1] ][0]
                    delta_sec = (gap_stop - gap_start).seconds
                    gap_sec = 1 if delta_sec == 0 else delta_sec
                    if gap_sec >= parameters['minsec']:
                        print '%d,%s,%s' % (gap_sec, gap_start, gap_stop)

            return 0

    print_usage()  

# mysql --batch -h timmeh -u pims -p pims -pPASSWD -e 'select from_unixtime(time) as GMT from 121f08 where time > unix_timestamp("2015-01-13 00:00:00") and time < unix_timestamp("2015-01-14 00:00:00");' | dbhist.py > /tmp/trash1.txt
if __name__ == "__main__":
    main(sys.argv)
    
