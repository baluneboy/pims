#!/usr/bin/env python

"""
Run these tests after patterns change AND AFTER adding updates/new a test_*.py file.

    #------------------------------------------------
    for alternate test examples using unittest, see:
    ~/dev/programs/python/ugaudio/tests
    #------------------------------------------------

# THIS IS HOW TO RUN THE TESTS
cd /home/pims/dev/programs/python/pims/patterns/tests
python -B -m pytest # ALL FOUND IN THIS DIR

# OR, FOR JUST ONE FILE:
cd /home/pims/dev/programs/python/pims/patterns/tests
python -B -m pytest test_probepats.py
"""

import re
import pytest

from pims.patterns.dailyproducts import _SENSOR_DIR_PATTERN

my_regex = re.compile(_SENSOR_DIR_PATTERN)


@pytest.mark.parametrize('test_str', [
     '/misc/yoda/pub/pad/year2020/month05/day01/sams2_accel_121f03',
     '/misc/yoda/pub/pad/year2020/month10/day20/samses_accel_es20',
     '/home/pims/data/pad/year2020/month04/day01/sams2_accel_121f03',
     '/home/pims/data/pad/year2020/month11/day22/samses_accel_es20',
])


def test_any_pad_sensor_path(test_str):
     assert my_regex.match(test_str) is not None
     bad_str = test_str.replace('year', 'BEER')
     assert my_regex.match(bad_str) is None


import datetime
import pathlib
from pims.files.utils import get_pad_timestamp_deltas

BIGDELTA = datetime.timedelta(days=100*999.99)
sensors = ['121f02', '121f03', '121f04', '121f05', '121f08']
delta_stats = {sensor: [BIGDELTA, -BIGDELTA] for sensor in sensors}

for day in ['01', '02', '03']:
     for sensor in sensors:
          dir_obj = pathlib.Path('/tmp/pad/year2020/month12/day' + day + '/sams2_accel_' + sensor)
          hdr_files_by_alphanum = sorted(list(x for x in dir_obj.iterdir() if x.is_file() and str(x).endswith('.header')))
          tup = get_pad_timestamp_deltas(hdr_files_by_alphanum)
          if tup[0] < delta_stats[sensor][0]:
               delta_stats[sensor][0] = tup[0]
          if tup[1] > delta_stats[sensor][1]:
               delta_stats[sensor][1] = tup[1]

for k, v in delta_stats.items():
     print(k, *v)
