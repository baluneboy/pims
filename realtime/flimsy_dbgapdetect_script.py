#!/usr/bin/env python
version = '$Id$'

import os
import sys
import datetime
from dateutil import parser
from pims.database.pimsquery import db_connect
from pims.utils.pimsdateutil import floor_hour
from pims.utils.pimsdateutil import datetime_to_days_ago

# TODO
# - robustness for missing table (or go out and find hosts/tables automagically)
# - iterate over list of sensors
# - better way to get expected packets per second (SAMS/MAMS HiRAP, SampleRate, what else)
# - some form of pivot table to show results (user choice: HTML or CSV form)


# input parameters
defaults = {
'sensor':           '121f03',       # sensor = table name
'packets_per_sec':  '8',            # expected value for this sensor for this gap check period; hirap is 5.21, oss is 0.0625
'host':             'tweek',        # like tweek for 121f03
'min_pct':          '90',           # show periods that do not meet this min_pct requirements
'hours_ago':        '24',           # start checking this many hours ago; if '-' in hours_ago treat as datetime input
'num_minutes':      '30',           # check every num_minutes chunk of time
}
parameters = defaults.copy()


# Info on database gaps given sensor (i.e. table), host, and expected packets per second.
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

    # Get start/stop times (scooched a bit; floor hour mark on start).
    def _get_times(self):
        """Get start/stop times (scooched a bit; floor hour mark on start)."""
        actual_stop = datetime.datetime.now()
        actual_start = actual_stop - datetime.timedelta(hours=self.hours_ago) # user asked for this
        # let's scooch the start time (hour) back a bit
        start = floor_hour( actual_start )
        stop = floor_hour( actual_stop )
        return start, stop

    # Generator to get datetimes for every tdelta_minutes worth of time.
    def _gen_next_span(self):
        """Generator to get datetimes for every tdelta_minutes worth of time."""
        dtm = self.start
        yield(dtm)
        while True:
            yield(dtm)
            dtm += self.tdelta_minutes            

    # Count number of packets expected for a chunk of tdelta_minutes.
    def _count_packets(self, start):
        """Count number of packets expected for a chunk of tdelta_minutes."""
        stop =  start + self.tdelta_minutes
        query = 'select count(*) from %s where time > unix_timestamp("%s") and time < unix_timestamp("%s")' % (self.sensor, start.strftime('%Y-%m-%d %H:%M:%S'), stop.strftime('%Y-%m-%d %H:%M:%S'))
        results = db_connect(query, host=self.host, db='pims')
        return 100.0 * results[0][0] / self.expect_packet_count
        
    # Print gaps that do not fulfill min_pct for a given tdelta_minutes period.        
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

class FuturisticDatabaseGaps(DatabaseGaps):

    def __init__(self, sensor, packets_per_sec, hours_ago=12, num_minutes=10, host='localhost', min_pct=99.9, future_stop=None):
        """Initialize."""
        self.sensor = sensor
        self.packets_per_sec = packets_per_sec
        self.hours_ago = hours_ago
        self.num_minutes = num_minutes
        self.tdelta_minutes = datetime.timedelta(minutes=num_minutes)
        self.expect_packet_count = self.packets_per_sec * self.tdelta_minutes.seconds          
        self.host = host
        self.min_pct = min_pct
        if future_stop:
            fstop = parser.parse(future_stop)
        else:
            fstop = parser.parse('2020-01-01 00:00:01')
        self.start, self.stop = self._get_times(fstop)

    # Get start/stop times (floor hour mark on start, stop IS IN THE FUTURE).
    def _get_times(self, fstop):
        """Get start/stop times (floor hour mark on start)."""
        actual_stop = datetime.datetime.now()
        actual_start = actual_stop - datetime.timedelta(hours=self.hours_ago) # user asked for this
        # let's scooch the start time (hour) back a bit
        start = floor_hour( actual_start )
        # now we change stop according to future_stop
        stop = floor_hour( fstop )
        return start, stop
    
#fdbgaps = FuturisticDatabaseGaps('oss', 0.0625, host='jimmy', min_pct=111, hours_ago=96, num_minutes=60, future_stop='2020-01-01')
#print fdbgaps.get_gaps()
#raise SystemExit
    
# Checking for reasonableness of parameters entered on command line.
def params_okay():
    """Checking for reasonableness of parameters entered on command line."""
    parameters['packets_per_sec'] = float(parameters['packets_per_sec'])
    parameters['min_pct'] = float(parameters['min_pct'])
    if '-' in parameters['hours_ago']:
        parameters['hours_ago'] = 24.0 * float(datetime_to_days_ago(parser.parse(parameters['hours_ago'])))
    else:
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

# Check db for gaps.
def check_db_for_gaps(sensor, pps, host, min_pct, hours_ago, num_minutes):
    """Check db for gaps."""
    dbgaps = DatabaseGaps(sensor, pps, host=host, min_pct=min_pct, hours_ago=hours_ago, num_minutes=num_minutes)
    return dbgaps.get_gaps()
    
# Show gaps in db.
def main(argv):
    """Show gaps in db."""
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
            #print parameters; raise SystemExit
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
    