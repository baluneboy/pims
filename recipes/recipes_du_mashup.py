#!/usr/bin/env python

import re
import csv
import datetime
import pandas as pd
from dateutil import parser


PAT = re.compile(r'year(?P<year>\d{4})/month(?P<month>\d{2})/day(?P<day>\d{2})')


def read_kb_pth_from_text(txt_file):
    """return dict with date keys and KB values"""
    my_dict = dict()
    with open(txt_file, 'rt') as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            m = PAT.search(row[1])
            d = datetime.datetime(int(m.group('year')), int(m.group('month')), int(m.group('day'))).date()
            my_dict[d] = row[0]
    return my_dict


txt_files = ['/home/pims/Documents/du_pad.txt',
             '/home/pims/Documents/du_roadmaps.txt',
             '/home/pims/Documents/du_results.txt']

# dd = dict.fromkeys([x.date() for x in pd.date_range('2017-01-01', '2019-01-01')])

keys = [x.date() for x in pd.date_range('2017-01-01', '2019-01-01')]
dd = {key: 0 for key in keys}



for txt_file in txt_files:
    ddict = read_kb_pth_from_text(txt_file)
    for k, v in ddict.iteritems():
        dd[k] += int(v)

for k, v in dd.iteritems():
    print k, v
