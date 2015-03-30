#!/usr/bin/python

import unittest
import datetime
from interval import Interval, IntervalSet

from pims.pad.loose_pad_intervalset import LoosePadIntervalSet
from pims.utils.pimsdateutil import start_stop_to_pad_fullfilestr, datetime_to_doytimestr, floor_minute, ceil_minute
from pims.pad.pad_gaps_and_intervals import get_loose_interval_set_from_header_filenames

# TODO
# - consolidate common code in various test methods in suite under setUp method
# - for setUp concoct an array of PAD header files to tease out nooks and crannies of "close enough" spackle over gaps
# - intra-file gaps of say 1sec, 1.5sec, 2sec
# - variable maxgapsec parameter to test spackling
# - test this on a real set of PAD header files from yoda

class LoosePadIntervalSetTestCase(unittest.TestCase):
    """
    Test suite for pims.pad.LoosePadIntervalSet.
    """

    def setUp(self):
        # create some convenient (fake) pad header files
        ##self.fake_pad_headers = [
        ##    '/misc/yoda/pub/pad/2015_03_14_00_05_47.252+2015_03_14_00_15_47.267.121f05.header',
        ##    '/misc/yoda/pub/pad/2015_03_14_00_15_48.867+2015_03_14_00_25_00.000.121f05.header'
        ##    ]
        pass

    def _get_fake_headers(self):
        start = datetime.datetime(2015, 1, 1, 0, 0, 0)
        stop =  datetime.datetime(2015, 1, 1, 1, 0, 0)
        this_day_interval = Interval( start, start + datetime.timedelta(days=1) )
        this_day_interval_set = IntervalSet( (this_day_interval,) )        
        minutes_per_file = 60.0
        sec_between_files = 0.5
        headers = []
        t1 = start
        while t1 <= stop:
            t2 = t1 + datetime.timedelta(minutes=minutes_per_file)
            headers.append(start_stop_to_pad_fullfilestr(t1, t2, pad_path='/tmp/pad', subdir_prefix='fake_accel_', sensor='123f00', joiner='-'))
            t1 += datetime.timedelta(seconds=sec_between_files)
        return headers, this_day_interval_set

    def test_close_enough(self):
        """
        Tests the close_enough method of the LoosePadIntervalSet object.
        """
        d1 = datetime.datetime(2015,1,1,0,0,0)
        d2 = d1 + datetime.timedelta(seconds=12.345)
        d3 = d2 + datetime.timedelta(seconds=1.6)           # 1.6 sec
        d4 = d3 + datetime.timedelta(seconds=0.5)
        d5 = d4 + datetime.timedelta(seconds=1.5)           # 1.5 sec
        d6 = d5 + datetime.timedelta(seconds=86400.123456)  # over a day
        r1 = Interval(d1, d2)
        r2 = Interval(d3, d4)
        r3 = Interval(d5, d6)
        s = LoosePadIntervalSet()
        self.assertEqual( False, s.close_enough(r1, r2) ) # False
        self.assertEqual( True,  s.close_enough(r2, r3) ) # True
        self.assertEqual( False, s.close_enough(r1, r3) ) # False
        self.assertEqual( False, s.close_enough(r3, r1) ) # False
        self.assertEqual( True,  s.close_enough(r3, r2) ) # True
    
    def test_get_fill(self):
        """
        Tests the _get_fill method of the LoosePadIntervalSet object.
        """
        d1 = datetime.datetime(2015,1,1,0,0,0)
        d2 = d1 + datetime.timedelta(seconds=12.345)
        d3 = d2 + datetime.timedelta(seconds=1.6)
        d4 = d3 + datetime.timedelta(seconds=0.5)
        d5 = d4 + datetime.timedelta(seconds=60.0)
        d6 = d5 + datetime.timedelta(seconds=86400.123456)
        r1 = Interval(d1, d2)
        r2 = Interval(d3, d4)
        r3 = Interval(d5, d6)        
        s = LoosePadIntervalSet()
        i23 = s._get_fill(r2, r3)
        self.assertEqual( i23.lower_bound, datetime.datetime(2015, 1, 1, 0, 0, 14, 445000))
        self.assertEqual( i23.upper_bound, datetime.datetime(2015, 1, 1, 0, 1, 14, 445000))
        i32 = s._get_fill(r3, r2)
        self.assertEqual( i32.lower_bound, datetime.datetime(2015, 1, 1, 0, 0, 14, 445000))
        self.assertEqual( i32.upper_bound, datetime.datetime(2015, 1, 1, 0, 1, 14, 445000))

    def test_add(self):
        """
        Tests the add method of the LoosePadIntervalSet object.
        """
        d0 = datetime.datetime(2014,12,31,23,59,58)
        d1 = datetime.datetime(2015,1,1,0,0,0)
        d2 = d1 + datetime.timedelta(seconds=12.345)
        d3 = d2 + datetime.timedelta(seconds=1.6)
        d4 = d3 + datetime.timedelta(seconds=0.5)
        d5 = d4 + datetime.timedelta(seconds=60.0)
        d6 = d5 + datetime.timedelta(seconds=86400.123456)
        r1 = Interval(d1, d2)
        r2 = Interval(d3, d4)
        r3 = Interval(d5, d6)        
        s = LoosePadIntervalSet()
        s.add(d0)
        self.assertEqual( s[0].lower_bound, datetime.datetime(2014, 12, 31, 23, 59, 58) )
        s.add(r1)
        self.assertEqual( s[1].lower_bound, datetime.datetime(2015, 1, 1, 0, 0) )
        self.assertEqual( s[1].upper_bound, datetime.datetime(2015, 1, 1, 0, 0, 12, 345000) )
        s.add(r2)
        self.assertEqual( s[2].lower_bound, datetime.datetime(2015, 1, 1, 0, 0, 13, 945000) )
        self.assertEqual( s[2].upper_bound, datetime.datetime(2015, 1, 1, 0, 0, 14, 445000) )
        s.add(r3)
        self.assertEqual( s[3].lower_bound, datetime.datetime(2015, 1, 1, 0, 1, 14, 445000) )
        self.assertEqual( s[3].upper_bound, datetime.datetime(2015, 1, 2, 0, 1, 14, 568456) )

    def test_fake_headers(self):
        """
        Tests the fake headers with nice gaps.
        """
        fake_pad_headers, this_day_interval_set = self._get_fake_headers()
        sensor_list_gaps = IntervalSet()
        header_files_all_sensors = fake_pad_headers
        header_files = [ x for x in header_files_all_sensors if x.endswith('122f00' + '.header') ]
        sensor_day_interval_set = get_loose_interval_set_from_header_filenames(header_files, 0.1) # maxgapsec = 0.1
        # now, the set of gaps are these
        sensor_gaps_interval_set = this_day_interval_set - sensor_day_interval_set
        sensor_day_total_gap_minutes = 0
        for gap in sensor_gaps_interval_set:
            sensor_day_total_gap_minutes += (gap.upper_bound - gap.lower_bound).total_seconds() / 60.0
            sensor_list_gaps.add(gap)
        self.assertEqual( sensor_day_total_gap_minutes, 22.345 )

def suite():
    return unittest.makeSuite(LoosePadIntervalSetTestCase, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
