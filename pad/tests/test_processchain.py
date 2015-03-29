#!/usr/bin/python

import unittest
import os
import pickle
import numpy as np
from copy import deepcopy
from obspy import UTCDateTime, Trace
from pims.pad.padstream import PadStream
from pims.pad.processchain import PadProcessChain
from test_support import filter_setup, build_ramps, build_sines

class PadProcessChainTestCase(unittest.TestCase):
    """
    Test suite for PadProcessChain.
    """

    def setUp(self):
        # path relative to this module (file) is where we save pickled substream (p) file
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

    def test_get_units(self):
        """Test _get_units method."""
        ppc = PadProcessChain()
        self.assertEqual( 'ug', ppc._get_units() )
        ppc = PadProcessChain(scale_factor=1e3)
        self.assertEqual( 'mg', ppc._get_units() )
        # try to initialize with bad scale_factor
        kwargs = {'scale_factor':999.9}
        self.assertRaises(ValueError, PadProcessChain, **kwargs )

    def test_scale(self):
        """Test data scaling via scale_factor attribute."""
        ppc = PadProcessChain()
        tr = Trace(data=np.ones(9)*17)
        self.assertEqual( 17.0, np.max([tr]) )
        ppc.scale(tr)
        self.assertEqual( 17000000.0, np.max([tr]) )
        ppc = PadProcessChain(scale_factor=1e3)
        tr = Trace(data=np.ones(9)*17)
        self.assertEqual( 17.0, np.max([tr]) )
        ppc.scale(tr)
        self.assertEqual( 17000.0, np.max([tr]) )

    def test_detrend(self):
        """Test data detrend via detrend method on substream."""
        # simple demean (default)
        ppc = PadProcessChain()
        ppc.detrend(self.saved_substream)
        self.assertAlmostEqual( 0.0, np.mean([self.saved_substream[0]]) )
        self.assertAlmostEqual( 0.0, np.mean([self.saved_substream[1]]) )
        self.assertAlmostEqual( 0.0, np.mean([self.saved_substream[2]]) )
        # now remove linear trend
        ppc = PadProcessChain(detrend_type='linear')
        ppc.detrend(self.ramps_substream)
        self.assertAlmostEqual( 0.0, np.mean([self.ramps_substream[0]]) )
        self.assertAlmostEqual( 0.0, np.mean([self.ramps_substream[1]]) )
        self.assertAlmostEqual( 0.0, np.mean([self.ramps_substream[2]]) )        

    def test_filter(self):
        """Test data filtering via filter method on substream."""
        # default 5 Hz LPF
        ppc = PadProcessChain()
        #self.sines_substream.plot()
        ppc.filter(self.sines_substream)
        #self.sines_substream.plot()        
        # After 5 Hz lowpass filtering, x and y traces should be almost equal
        diff = np.abs( self.sines_substream.select(channel='x')[0].data - \
                       self.sines_substream.select(channel='y')[0].data).max()
        self.assertAlmostEqual( 0.0, diff, 0)
        # After 5 Hz lowpass filtering, z trace should be almost equal to zero
        zchk = np.abs(self.sines_substream.select(channel='z')[0].data).max()
        self.assertAlmostEqual( 0.0, zchk, 0)

    def test_apply_interval_func(self):
        """Test apply interval func to data of substream."""
        # check RMS, that is, std(), which is the default
        ppc = PadProcessChain()
        rms = ppc.apply_interval_func(self.saved_substream)
        self.assertEqual( 3, len(rms) )
        self.assertAlmostEqual( 40.3683, rms[0], 3 )
        self.assertAlmostEqual( 19.4536, rms[1], 3 )
        self.assertAlmostEqual( 29.3168, rms[2], 3 )
        # now check sines, which makes for easy RMS check
        ppc = PadProcessChain()
        rms = ppc.apply_interval_func(self.sines_substream)
        self.assertEqual( 3, len(rms) )
        # for sum of 2 sines, RMS is RSS of the 2 components
        rss = np.sqrt(3.0/2.0)
        self.assertAlmostEqual(          rss, rms[0], 3 )
        self.assertAlmostEqual( 1/np.sqrt(2), rms[1], 3 )
        self.assertAlmostEqual(            1, rms[2], 3 )
        # add DC offset to see that Stream's std() has built-in demeaning
        self.sines_substream[2].data = self.sines_substream[2].data + 55.5
        rms = ppc.apply_interval_func(self.sines_substream)
        self.assertEqual( 3, len(rms) )
        self.assertAlmostEqual(          rss, rms[0], 3 )
        self.assertAlmostEqual( 1/np.sqrt(2), rms[1], 3 )
        self.assertAlmostEqual(            1, rms[2], 3 )
        # now calculate rms value that includes the dc offset
        rms_dc = np.sqrt(np.mean(self.sines_substream[2].data**2))
        self.assertAlmostEqual(         55.5, rms_dc, 1 )
        
    #def test_combine_axes(self):
    #    """Test combine_axes of substream."""
    #    # this per-axis input is okay...
    #    ppc = PadProcessChain(axes=['x', 'y','z']) # ...so no error, yay!
    #    ppc.combine_axes(None) # ..BUT, it currently does nothing, boo
    #    # since we only handle per-axis (no combine yet)...
    #    kwargs = { 'axes': ['combined'] } # ...we do get error for this input
    #    self.assertRaises(ValueError, PadProcessChain, **kwargs )

    def test_entire_chain(self):
        """Test entire chain sequence."""
        ppc = PadProcessChain()
        stream = PadStream()
        # 1. apply scale factor to trace as we append packet data (trace then appended to stream)
        #    this happens to ALL data in append_process_packet_data method of PadGenerator object
        #    on per-axis (x,y,z) basis as the data from atxyzs are put in PadStream as Traces
        npts = len(self.sines_substream)
        for i, ax in enumerate(['x', 'y', 'z']):
            # actually for next line, use Trace with atxyzs columns & header, BUT WITHOUT
            # dividing by 1e6 after semi-colon
            tr = self.sines_substream.select(channel=ax)[0]; tr.data /= 1.0e6
            ppc.scale(tr) # instead of tr.normalize( norm=(1.0 / self.scale_factor) )
            # SNIPPED 3 lines for adjusting tr.stats
            # append trace to stream
            stream.append(tr)
        
        # 2. detrend [demean] (currently) substream based on analysis_interval's worth of data
        #    this happens after we have appended enough data for analysis_interval span
        #    in append_process_packet_data method of PadGenerator object...
        # AND we CASCADE at this point with...
        # 3. filter the now detrended substream based on analysis_interval's worth of data
        substream = deepcopy(stream) # FOR THESE STEPS, WE WORK ON substream!
        substream.select(channel='z')[0].data = substream.select(channel='z')[0].data + 55.5
        #substream.plot()
        ppc.detrend(substream)
        ppc.filter(substream)
        #substream.plot()
    
        # 4. apply interval func (RMS) to analysis_interval's worth of data
        #    this happens on per analysis_interval basis in step_callback method of GraphFrame object
        #    and it always happens to each axis regardless of how we want to combine for plotting
        txyzs = []
        for testing_offset, possibly_inf_val in zip([20.0, 0.0, 10.0], [0, np.inf, 0]):
            txyz = tuple()
            meantime = np.mean( [ substream[0].stats.starttime.timestamp, substream[-1].stats.endtime.timestamp] )
            meantime = meantime + testing_offset # GET RID OF THIS IN ACTUAL CODE
            txyz = txyz + ( meantime, )
            rms = ppc.apply_interval_func(substream)
            rms[0] = rms[0] + possibly_inf_val # GET RID OF THIS IN ACTUAL CODE
            if np.any(np.isinf(rms)):
                # replace inf values with nan
                rms[np.where(np.isinf(rms))] = np.nan
                # AND SQUAWK TOO, like this commented line:
                #log.warning( 'INF2NAN had to set %s-axis inf value to nan for time %s' % (ax, unix2dtm(meantime)) )
            txyz = txyz + tuple(rms)
            txyzs.append(txyz)
        # for testing, we gather up a bunch of tuples above in a list, then append here:
        for txyz in txyzs:
            ppc.plot_data_container.append(txyz)
        
        # 5. show per-axis [not implemented yet is our combine_axes method for plotting]
        #    we probably will maintain GraphFrame's data attribute with either "3 columns" or "1 column"
        #    note that this data attribute is a XyzPlotDataSortedList object
        #print ppc.plot_data_container

def view_waveforms():
    tracex, tracey, tracez = build_ramps(5001)
    ramps_substream = PadStream(traces=[tracex, tracey, tracez])
    ramps_substream.plot()
    
#view_waveforms(); raise SystemExit

def view_filter_setup():
    import matplotlib.pyplot as plt    
    t, x, xlow, xhigh = filter_setup()
    plt.plot(t, x)
    plt.show()
    ## Now create a lowpass Butterworth filter with a cutoff of 0.125x Nyquist (125 Hz)
    ## and apply it to x with filtfilt. The result should be approximately xlow, with no phase shift.
    #b, a = signal.butter(9, 0.02)
    #y = signal.filtfilt(b, a, x)
    #print np.abs(y - xlow).max()
    #plt.plot(t, y)
    #plt.show()
    
#view_filter_setup(); raise SystemExit

def suite():
    return unittest.makeSuite(PadProcessChainTestCase, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
