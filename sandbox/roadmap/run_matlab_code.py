#!/usr/bin/env python

import datetime
from pims.utils.commands import time_run

def run_matlab_roadmap(sensor, day, mfile, abbrev):
    """run cutoff or 10 Hz version of generate_vibratory_roadmap on ike for this day/sensor"""
    cmdstr = 'ssh mr-hankey /home/pims/dev/programs/bash/backfill_roadmap.bash %s "*_accel_*%s" %s %s' % (day.strftime('%Y-%m-%d'), sensor, mfile, abbrev)
    #print cmdstr        
    retcode = time_run(cmdstr, 3600) # timeout of 3600 seconds = 60 minutes
    return retcode

sensor = '121f04'
day = datetime.datetime(2017, 6, 1)
mfile = 'configure_roadmap_spectrogram_10hz'
abbrev = 'ten'
retcode = run_matlab_roadmap(sensor, day, mfile, abbrev)
print retcode