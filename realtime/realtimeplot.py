#!/usr/bin/env python
version = '$Id$'

import os
import sys
import datetime
import logging, logging.config
from pims.realtime.stream import RealtimeStream, RealtimePlotParameters

# Default input parameters:
defaults = {
'sensor':           '121f05',   # sensor designation (this is actually the MySQL db table name)
'plot_type':        'frvt3',    # like gvt3, fgvt3, rvt3, frvt3; "f" prefix for "filtered"
'frange_hz':        '0.2-0.3',  # frequency range for filtering in Hz; [f1 f2) Hz
'plot_minutes':     '10',       # span of plot in minutes
'update_minutes':   '0.5',      # how often to update plot in minutes
}
parameters = defaults.copy()
    
def params_ok(log):
    """Check input parameters."""
    # verify that unique real-time stream is available
    rts = RealtimeStream(parameters['sensor'])
    if not rts.is_unique:
        log.error('Could not identify unique real-time stream for sensor %s.' % parameters['sensor'])
        return False
    
    # verify real-time stream meets frange_hz's upper limit
    rtp = RealtimePlotParameters(plot_type=parameters['plot_type'], frange_hz=parameters['frange_hz'],
        plot_minutes=parameters['plot_minutes'], update_minutes=parameters['update_minutes'])
    if rts.cutoff_hz < rtp.frange_hz[1]:
        log.error('The real-time stream for sensor %s has cutoff (%f Hz) < frange_hz upper limit (%f Hz).' %
                  parameters['sensor'], rts.cutoff_hz, rtp[1])
        return False
        
    # inputs are okay, so log them and continue
    record_inputs(log)
    return True

def record_inputs(log):
    for k,v in parameters.iteritems():
        log.info( k + ':' + str(v) )
    log.info( '=' * 33 )
    
def print_usage():
    """Print short description of how to run this program."""
    print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def launch_plot(log):
    """
    This launches the plot.
    """
    log.info("Attempting to launch plot.")
    log.error('Not implemented yet.')
    
def main(argv):
    """Check inputs, start logging, and launch plot."""
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        # set up logging
        bname = os.path.splitext( os.path.basename(__file__) )[0]
        log_config_file = os.path.join('/home/pims/dev/programs/python/pims/files', bname + '_log.conf')
        logging.config.fileConfig(log_config_file)
        log = logging.getLogger('inputs')
        if params_ok(log):
            try:
                log = logging.getLogger('process')
                launch_plot(log)
            except Exception, e:
                # Log error
                log.error( e.message )
                return -1
            # Message with time when done
            log.debug('Done %s.\n' % datetime.datetime.now() + '-'*99)
            return 0
    print_usage()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
