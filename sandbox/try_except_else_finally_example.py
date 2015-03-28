#!/usr/bin/env python

try:
    x = 1.0 / 0.0
except Exception, e:
    print 'an exception happened: %s' % e.message
else:
    print 'the try worked, so this is the else clause'
finally:
    print 'no matter what, we do clean-up with finally clause'
