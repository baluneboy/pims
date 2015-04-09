#!/usr/bin/env python

import pymatlab
session = pymatlab.session_factory()

hdr = '/data/pad/year2015/month04/day01/sams2_accel_121f04/2015_04_01_01_30_01.719-2015_04_01_01_36_00.019.121f04.header'
side = 'right'
overlap_sec = 120.5;

cmd = "C = padtrim('%s', '%s', %f);" % (hdr, side, overlap_sec)
session.run(cmd)
count = session.getvalue('C');
del session
print count