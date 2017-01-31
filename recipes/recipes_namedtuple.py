#!/usr/bin/env python

from collections import namedtuple

ScanLogRecord = namedtuple('ScanLogRecord', 'gmt, person, code')

import csv
for rec in map(ScanLogRecord._make, csv.reader(open("results.csv", "rb"))):
    print rec #.gmt, rec.person, rec.code