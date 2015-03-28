#!/usr/bin/env python
version = '$Id$'

import os
import sys
import datetime
from pims.database.pimsquery import db_connect
from pims.utils.pimsdateutil import floor_ten_minutes

# TODO
# - robustness for missing table (or go out and find hosts/tables automagically)
# - iterate over list of sensors
# - better way to get expected packets per second (SAMS/MAMS HiRAP, SampleRate, what else)
# - some form of pivot table to show results

# input parameters
defaults = {
'sensor':           '121f03',       # sensor = table name
'packets_per_sec':  '8',            # expected value for this sensor for this gap check period
'host':             'tweek',        # like tweek for 121f03
'min_pct':          '90',           # show periods that do not meet this min_pct requirements
'hours_ago':        '24',           # start checking this many hours ago
'num_minutes':      '30',           # check every num_minutes chunk of time
}
parameters = defaults.copy()

class DatabaseGaps(object):
    """
    Info on database gaps given sensor (i.e. table), host, and expected packets per second.
    """
    def __init__(self, sensor, packets_per_sec, hours_ago=12, num_minutes=10, host='localhost', min_pct=99.9):
        """Initialize."""
        self.sensor = sensor
        self.packets_per_sec = packets_per_sec
        self.hours_ago = hours_ago
        self.num_minutes = num_minutes
        self.tdelta_minutes = datetime.timedelta(minutes=num_minutes)
        self.expect_packet_count = self.packets_per_sec * self.tdelta_minutes.seconds          
        self.host = host
        self.min_pct = min_pct
        self.start, self.stop = self._get_times()

    def _get_times(self):
        """Get start/stop times (scooched a bit and round-ten-minutes on start)."""
        actual_stop = datetime.datetime.now()
        actual_start = actual_stop - datetime.timedelta(hours=self.hours_ago) # asked for this
        # let's scooch start back a bit
        start = floor_ten_minutes( actual_start - datetime.timedelta(minutes=15) )
        stop = floor_ten_minutes( actual_stop )
        return start, stop
    
    def _gen_next_span(self):
        """Generator to get datetimes for every tdelta_minutes worth of time."""
        d1 = self.start
        dtm = d1 - self.tdelta_minutes
        while True:
            dtm += self.tdelta_minutes
            yield(dtm)

    def _count_packets(self, start):
        """Count number of packets expected for a chunk of tdelta_minutes."""
        stop =  start + self.tdelta_minutes
        query = 'select count(*) from %s where time > unix_timestamp("%s") and time < unix_timestamp("%s")' % (self.sensor, start.strftime('%Y-%m-%d %H:%M:%S'), stop.strftime('%Y-%m-%d %H:%M:%S'))
        results = db_connect(query, host=self.host, db='pims')
        return 100.0 * results[0][0] / self.expect_packet_count
        
    def get_gaps(self):
        """Print gaps that do not fulfill min_pct for a given tdelta_minutes period."""
        gaps = []
        gen = self._gen_next_span()
        dtm = gen.next()
        while dtm < self.stop:
            dtm = gen.next()
            pct = self._count_packets(dtm)
            if pct < self.min_pct:
                gaps.append( '{0:s}, {1:>6.2f}, {2:s}'.format(str(dtm), pct, self.sensor) )
        return '\n'.join(gaps)

def params_okay():
    """Not really checking for reasonableness of parameters entered on command line."""
    parameters['packets_per_sec'] = float(parameters['packets_per_sec'])
    parameters['min_pct'] = float(parameters['min_pct'])
    parameters['hours_ago'] = float(parameters['hours_ago'])
    parameters['num_minutes'] = float(parameters['num_minutes'])
    return True

def print_usage():
    """Print short description of how to run the program."""
    print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def check_db_for_gaps(sensor, pps, host, min_pct, hours_ago, num_minutes):
    """Check for gaps."""
    dbgaps = DatabaseGaps(sensor, pps, host=host, min_pct=min_pct, hours_ago=hours_ago, num_minutes=num_minutes)
    return dbgaps.get_gaps()
    
def main(argv):
    """Wright script that ultimately checks/shows gaps in db."""
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if params_okay():

            try:
                msg = check_db_for_gaps(
                    parameters['sensor'],
                    parameters['packets_per_sec'],
                    parameters['host'],
                    parameters['min_pct'],
                    parameters['hours_ago'],
                    parameters['num_minutes'],
                    )

            except Exception as e:
                msg = "Exception %s" % e.message
            
            print msg or 'Got nothing.'
            return 0

    print_usage()  

if __name__ == '__main__':
    sys.exit(main(sys.argv))
    