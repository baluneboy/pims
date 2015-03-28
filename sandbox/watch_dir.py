#! /usr/bin/env python

import os
import sys
import time

path_to_watch = "/tmp"
before = dict ([(f, None) for f in os.listdir (path_to_watch)])
while True:
    try:
        time.sleep(5)
        after = dict ([(f, None) for f in os.listdir (path_to_watch)])
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]
        if added: print "Added: ", ", ".join (added)
        if removed: print "Removed: ", ", ".join (removed)
        before = after
    except KeyboardInterrupt:
        print '\nuser hit ctrl-c'
        sys.exit(0)