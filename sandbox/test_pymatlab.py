#!/usr/bin/env python

import pymatlab
session = pymatlab.session_factory()

hdr1 = '/data/pad/year2015/month04/day01/sams2_accel_121f04/2015_04_01_00_31_00.108-2015_04_01_00_41_00.115.121f04.header'
side1 = 'left'
overlap_sec1 = 10.543;

hdr2 = '/data/pad/year2015/month04/day01/sams2_accel_121f04/2015_04_01_00_41_00.117+2015_04_01_00_51_00.125.121f04.header'
side2 = 'right'
overlap_sec2 = 20.111;

hdr3 = '/data/pad/year2015/month04/day01/sams2_accel_121f04/2015_04_01_00_51_00.127+2015_04_01_01_01_00.134.121f04.header'
side3 = 'left'
overlap_sec3 = 30.456;

tups = [
    (hdr1, side1, overlap_sec1),
    (hdr2, side2, overlap_sec2),
    (hdr3, side3, overlap_sec3),    
    ]

for hdr, side, overlap_sec in tups:
    cmd = "C = padtrim('%s', '%s', %f);" % (hdr, side, overlap_sec)
    session.run(cmd)
    count = session.getvalue('C');
    print count, hdr
    
del session