#!/usr/bin/env python
version = '$Id$'

import sys
from configobj import ConfigObj

def showConfig(filename='/home/pims/dev/programs/python/samslogs/samslogs.cfg'):
    config = ConfigObj(filename)
    files = config['files']
    for f,d in files.items():
        print '-'*33
        print f
        if d['active']:
            del d['active']
            for k,v in d.items():
                print '\t', k
                for s,t in v.items():
                    #print '\t  ', s, ':', t
                    print '\t  %s:' % s, t

if __name__ == '__main__':
    sys.exit(showConfig(sys.argv[1]))
    
#Jan 14 15:02:37 icu-f01 rarpd[19458]: ep1: 0:60:97:94:35:53
#Jan 14 10:59:59 icu-f01 newsyslog[16290]: logfile turned over
#Dec  8 08:59:59 icu-f01 newsyslog[7634]: logfile turned over
#Wed Dec  8 09:00:58 2010: Killed [7619          ], found in file [/usr/local/sams-ii/telemetry_downlinker.pid] which was [117] seconds old.
#Wed Dec  8 09:00:59 2010: Ran command [/usr/local/bin/telemetry_downlinker -d].