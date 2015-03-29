#!/usr/bin/python

import unittest
import os
import pickle
import numpy as np
from copy import deepcopy
from obspy import UTCDateTime, Trace
from pims.pad.padstream import PadStream
from test_support import build_ramps, build_sines

class PlotsTestCase(unittest.TestCase):
    """
    Test suite for PadProcessChain.
    """

    def setUp(self):
        # we saved a pickled substream (p) file in pims/pad/tests/substream.p
        pickled_substream = os.path.join( os.path.dirname(__file__), 'substream.p')
        self.saved_substream = pickle.load( open(pickled_substream, 'rb') )
        # create normally-distributed random stream w/ mu, sigma known
        self.mu, self.sigma = 8.76, 0.54 # mean and standard deviation
        header = {'network': 'KH', 'station': 'BANG',
                  'starttime': UTCDateTime(2001, 5, 3, 23, 59, 59, 999000),
                  'npts': 5001, 'sampling_rate': 500.0,
                  'channel': 'x'}        
        tracex = Trace(data=np.random.normal(self.mu, self.sigma, 5001).astype('float64'),
                       header=deepcopy(header))
        header['channel'] = 'y'
        tracey = Trace(data=np.random.normal(self.mu, self.sigma, 5001).astype('float64'),
                       header=deepcopy(header))
        header['channel'] = 'z'
        tracez = Trace(data=np.random.normal(self.mu, self.sigma, 5001).astype('float64'),
                       header=deepcopy(header))
        self.valid_substream = PadStream(traces=[tracex, tracey, tracez])
        # create linear ramp random stream, per-axis (x,y,z)
        tracex, tracey, tracez = build_ramps(5001)
        self.ramps_substream = PadStream(traces=[tracex, tracey, tracez])
        # create two-sinusoid waveform for x, xlow for y, and xhigh for z
        tracex, tracey, tracez = build_sines()
        self.sines_substream = PadStream(traces=[tracex, tracey, tracez])
        
    def test_is_valid_substream(self):
        """Valid substream!?"""
        self.assertEqual( True, self.saved_substream.is_valid_substream() )
        self.assertEqual( True, self.valid_substream.is_valid_substream() )
        tracex = self.valid_substream[0]
        tracez = self.valid_substream[2]
        tracey = self.valid_substream[1]
        wrong_order_stream = PadStream(traces=[tracex, tracez, tracey])
        self.assertNotEqual( True, wrong_order_stream )
        
def suite():
    return unittest.makeSuite(PlotsTestCase, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
