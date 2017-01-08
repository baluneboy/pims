#!/usr/bin/env python

import re
import pytest

from pims.patterns.gutwrenchpats import _GUTWRENCH_HBDIR_PATTERN

my_regex = re.compile(_GUTWRENCH_HBDIR_PATTERN)

@pytest.mark.parametrize('test_str', [
'/some/path/to/hb_vib_crew_The_Exercise_Devices_2017-01-07',
'/some/path/to/hb_vib_vehicle_The_Exercise_Devices_2017-01-07',
'/some/path/to/hb_vib_equipment_The_Exercise_Devices_2017-01-07',
'/some/path/to/HB_vib_crew_The_Exercise_Devices_2017-01-07',
'/some/path/to/HB_vib_vehicle_The_Exercise_Devices_2017-01-07',
'/some/path/to/HB_vib_equipment_The_Exercise_Devices_2017-01-07',
'/some/path/to/hb_qs_crew_The_Exercise_Devices_2017-01-07',
'/some/path/to/hb_qs_vehicle_The_Exercise_Devices_2017-01-07',
'/some/path/to/hb_qs_equipment_The_Exercise_Devices_2017-01-07',
'/some/path/to/HB_qs_crew_The_Exercise_Devices_2017-01-07',
'/some/path/to/HB_qs_vehicle_The_Exercise_Devices_2017-01-07',
'/some/path/to/HB_qs_equipment_The_Exercise_Devices_2017-01-07',
])

def test_my_regex(test_str):
     assert my_regex.match(test_str) is not None
