#!/usr/bin/env python

import datetime
from pims.pad.grygier_counter import get_day_files


class TestGetDayFiles(object):
    """class to test get_day_files function"""

    def setup_method(self, method):
        """setup for general use in test methods of this class"""
        self.d = datetime.datetime(2019, 2, 1)
        self.sensor = '121f03006'
        self.fs = 142
        self.mindur = 5
        self.is_rev = True

    def test_feb_one(self):
        """test 2019-02-01"""
        files = get_day_files(self.d, self.sensor, self.fs, mindur=self.mindur, is_rev=self.is_rev)
        assert len(files) == 49  # for Feb. 1, 2019 with 121f03006
        assert files[0] == '/misc/yoda/pub/pad/year2019/month02/day01/sams2_accel_121f03006/' \
                           '2019_02_01_23_26_31.613+2019_02_01_23_57_17.690.121f03006'
        assert files[-1] == '/misc/yoda/pub/pad/year2019/month02/day01/sams2_accel_121f03006/' \
                            '2019_02_01_00_02_23.257-2019_02_01_00_33_09.334.121f03006'
