#!/usr/bin/env python

import datetime

try:
    x = 1.0 / 0.0
except Exception, e:
    print 'an exception happened: %s' % e.message
else:
    print 'the try worked, so this is the else clause'
finally:
    print 'no matter what, we do clean-up with finally clause for DIVIDE BY ZERO DEMO'

print '---------------'

ws_cell_A2_value = datetime.datetime(2016,10,2,12,0,0)
try:
    gmt_start = ws_cell_A2_value.date()
    if gmt_start.day != 1:
        raise Exception('DID NOT GET FIRST DAY OF MONTH')
except Exception, e:
    print 'TRYING TO GET GMT DATE (START OF MONTH), BUT AN EXCEPTION HAPPENED: %s' % e.message
else:
    print 'the try worked okay, so this is the else clause'
finally:
    print 'no matter what, we do clean-up with finally clause for GMT_START DEMO'