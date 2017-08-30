#!/usr/bin/env python

import sys
from pims.realtime.flimsy_dbgapdetect_script import main

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'    
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    UNDERLINE = '\033[4m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

print bcolors.OKBLUE + "OKBLUE goes here" + bcolors.ENDC
print bcolors.OKGREEN + "OKGREEN goes here" + bcolors.ENDC
print bcolors.WARNING + "WARNING goes here" + bcolors.ENDC
print bcolors.FAIL + "FAIL goes here" + bcolors.ENDC
print bcolors.UNDERLINE + "UNDERLINE goes here" + bcolors.ENDC
print bcolors.BOLD + "BOLD goes here" + bcolors.ENDC

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) < 2:
        argv.append('host=tweek')
        argv.append('sensor=121f03')
        argv.append('hours_ago=24')
        argv.append('num_minutes=60')
        argv.append('min_pct=111')
    main(argv)
    print 'FIXME dbgaps should just be some derivative using beautiful soup on what is used to get https://pims.grc.nasa.gov/plots/user/sams/dbpims.html'

#~/dev/programs/python/pims/realtime/flimsy_dbgapdetect_script.py host=tweek sensor=121f03 hours_ago=24 min_pct=111 num_minutes=60