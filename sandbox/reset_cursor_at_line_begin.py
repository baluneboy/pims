#!/usr/bin/env python
"""
The \r is the carriage return. You need the comma at the end of the print
statement to avoid automatic newline. Finally sys.stdout.flush() is needed to
flush the buffer out to stdout.
"""
import sys, time

for i in xrange(0, 101, 10):
  print '\r>> You have finished %3d%%' % i,
  sys.stdout.flush()
  time.sleep(1)
print