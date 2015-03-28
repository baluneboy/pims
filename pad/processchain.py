#!/usr/bin/python

import numpy as np
from pims.pad.padstream import RssPlotDataSortedList, XyzPlotDataSortedList

class IntervalStat(object):
    """istat = IntervalStat(analysis_interval)

    This class supports interval statistic calculations (like RMS).
    """

    def __init__ (self, analysis_interval):
        self.analysis_interval = analysis_interval

    def __repr__(self):
        return "%g-Second %s" % (self.analysis_interval, self.__class__.__name__)
    
    def plotstr(self):
        raise NotImplementedError('it is subclass responsibility to implement plotstr method')
   
    def get_result(self, obj, meth):
        raise NotImplementedError('it is subclass responsibility to implement get_result method')

class IntervalRMS(IntervalStat):
    
    def get_result(self, obj, meth):
        print obj.span()
        method_to_call = getattr(obj, meth)
        result = method_to_call()
        return result
    
    def plotstr(self):
        return 'intrms'

class PadProcessChain(object):
    """e.g. Scale, Demean, 5 Hz Lowpass, 10-Second Interval RMS, Per-Axis"""

    def __init__(self,
                 scale_factor=1e6,
                 detrend_type='demean',
                 filter_params={'type':'lowpass', 'freq':5, 'zerophase':True},
                 interval_params={'type':IntervalRMS, 'analysis_interval':10},
                 axes='xyz',    # either 'xyz' or 'rss'
                 maxlen=500 ):  # for plot_data_container
        self.scale_factor = scale_factor
        self.analysis_interval = interval_params['analysis_interval']
        self.units = self._get_units()
        self.detrend_type = detrend_type
        self.filter_params = filter_params
        self.interval_func = interval_params['type'](self.analysis_interval)
        self.plot_data_container = self._get_plot_data_container(axes, maxlen)

    def _get_units(self):
        if self.scale_factor == 1e3:
            return 'mg'
        elif self.scale_factor == 1e6:
            return 'ug'
        else:
            raise ValueError('unexpected scale factor of %g (try 1e3 or 1e6)' % self.scale_factor)

    def __repr__(self):
        return "%s for %s:\n(1) scale_factor=%g (%s)\n(2) detrend_type='%s'\n(3) filter_params=%s\n(4) interval_func='%s'\n(5) plot_data_container=%s" % \
            (self.__class__.__name__, self.interval_func.plotstr(),
             self.scale_factor, self.units,
             self.detrend_type,
             str(self.filter_params),
             str(self.interval_func),
             str(self.plot_data_container) )
    
    def _get_plot_data_container(self, axes, maxlen):
        if axes == 'rss':
            return RssPlotDataSortedList( maxlen=maxlen )
        elif axes == 'xyz':
            return XyzPlotDataSortedList( maxlen=maxlen )
        else:
            raise ValueError("unhandled case when axes is not 'xyz' or 'rss'")
        
    # 1. this is how we apply scale factor to trace as we append packet data (trace then appended to stream)
    def scale(self, trace):
        # norm factor is "/=" so invert sf
        trace.normalize( norm=(1.0 / self.scale_factor) )

    # 2. this is how we detrend [demean] (currently) substream based on analysis_interval's worth of data
    def detrend(self, substream):
        substream.detrend(type=self.detrend_type)

    # 3. this is how we filter substream based on analysis_interval's worth of data
    def filter(self, substream):
        substream.filter(self.filter_params['type'],
                         freq=self.filter_params['freq'],
                         zerophase=self.filter_params['zerophase'])
        #substream.filter('bandpass',
        #                 freqmin=112.0, freqmax=116.0,
        #                 zerophase=True)     

    # 4. this is how we apply interval func (RMS) to analysis_interval's worth of data
    def apply_interval_func(self, substream):
        rms = []
        for ax in ['x', 'y', 'z']:
            rms.append( substream.select(channel=ax).std()[0] )
        return np.array(rms)
    
    # 5. finally, we'd either show per-axis or somehow combine for plotting


if __name__=="__main__":
    from pims.pad.padstream import PadStream
    import numpy as np
    from copy import deepcopy
    from obspy import UTCDateTime, Trace, read
    from pims.pad.padstream import PadStream
    
    np.random.seed(815)
    header = {'network': 'BW', 'station': 'BGLD',
              'starttime': UTCDateTime(2007, 12, 31, 23, 59, 59, 915000),
              'npts': 412, 'sampling_rate': 200.0,
              'channel': 'EHE'}
    trace1 = Trace(data=np.random.randint(0, 1000, 412).astype('float64'),
                   header=deepcopy(header))
    header['starttime'] = UTCDateTime(2008, 1, 1, 0, 0, 4, 35000)
    header['npts'] = 824
    trace2 = Trace(data=np.random.randint(0, 1000, 824).astype('float64'),
                   header=deepcopy(header))
    header['starttime'] = UTCDateTime(2008, 1, 1, 0, 0, 10, 215000)
    trace3 = Trace(data=np.random.randint(0, 1000, 824).astype('float64'),
                   header=deepcopy(header))
    header['starttime'] = UTCDateTime(2008, 1, 1, 0, 0, 18, 455000)
    header['npts'] = 50668
    trace4 = Trace(
        data=np.random.randint(0, 1000, 50668).astype('float64'),
       header=deepcopy(header))
    st = PadStream(traces=[trace1, trace2, trace3, trace4])    

    ppc = PadProcessChain(axes='xyz')
    print ppc    
    
    ppc = PadProcessChain(axes='rss')
    print ppc
    
    irms = IntervalRMS(10)
    result = irms.get_result(st, 'std')
    print result
    
