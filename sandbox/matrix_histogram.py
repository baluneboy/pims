#!/usr/bin/env python

import sys
import time

for top in ['one', 'two', 'three']:
    for i in xrange(0, 101, 10):
        print '\r%s >> Downloading File [ %d%% ]' % (top, i),
        sys.stdout.flush()
        time.sleep(0.5)
    print

