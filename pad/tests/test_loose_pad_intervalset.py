#!/usr/bin/python

import unittest
import datetime
from interval import Interval

from pims.pad.loose_pad_intervalset import LoosePadIntervalSet
from pims.utils.pimsdateutil import start_stop_to_pad_fullfilestr

class LoosePadIntervalSetTestCase(unittest.TestCase):
    """
    Test suite for pims.pad.LoosePadIntervalSet.
    """

    def setUp(self):
        # create some convenient (fake) pad header files
        self.fake_pad_headers = [
            '/misc/yoda/pub/pad/2015_03_14_00_05_47.252+2015_03_14_00_15_47.267.121f05.header',
            '/misc/yoda/pub/pad/2015_03_14_00_15_48.867+2015_03_14_00_25_00.000.121f05.header'
            ]

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

def suite():
    return unittest.makeSuite(LoosePadIntervalSetTestCase, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
