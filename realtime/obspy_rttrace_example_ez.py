#!/usr/bin/env python

# TODO how to read rttrace from db
#from obspy import read
#from StringIO import StringIO
#import urllib2
#example_url = "http://examples.obspy.org/loc_RJOB20050831023349.z"
#stringio_obj = StringIO(urllib2.urlopen(example_url).read())
#st = read(stringio_obj)
#print(st)

# TODO see how "nice/easy" updates happen with rttrace
# TODO see how gaps and skewness affects rttrace and plot updates

#  SEED Conventions
#  Agency.Deployment.Station.Location.Channel
  
#  CHANNEL CHAR 1
#  F (unknown description)		fs >= 1000 and fs < 5000
#  C (unknown description)		fs >=  250 and fs < 1000
#  E (Extremely Short Period)	fs >=   80 and fs <  250
#  S (Short Period)			    fs >=   10 and fs <   80
#  
#  CHANNEL CHAR 2
#  N (Accelerometer)
#  
#  CHANNEL CHAR 3
#  A B C (SSA's X, Y, Z)
#  1 2 3 (sensor's X, Y, Z)
#  
#  NASA.ISS.SAMS.05.CNA for SAMS, SE-05,  500 sps, X-axis of SSA
#  NASA.ISS.SAME.06.CNB for SAMS, ES-06,  500 sps, Y-axis of SSA
#  NASA.ISS.MAMS.HI.FNC for MAMS, HiRAP, 1000 sps, Z-axis of SSA
#  NASA.ISS.SAMS.02.CN3 for SAMS, SE-02,  500 sps, X-axis of sensor

import numpy as np
from obspy.realtime import RtTrace
from obspy import read
from obspy.realtime.signal import calculateMwpMag
import matplotlib.pyplot as plt

def read_example_trace_SAC():
    """Read first trace of example SAC data file and extract contained time offset and epicentral distance of an earthquake"""
    data_trace = read('/path/to/II.TLY.BHZ.SAC')[0]
    ref_time_offset = data_trace.stats.sac.a
    epicentral_distance = data_trace.stats.sac.gcarc
    return data_trace, ref_time_offset, epicentral_distance 

def read_example_trace():
    """Read first trace of example data file"""
    st = read('/home/pims/dev/programs/python/pims/sandbox/data/slist_for_example.ascii')
    st.detrend('demean')
    data_trace = st[0]
    return data_trace

def split_trace_into3(data_trace):
    """Split given trace into a list of three sub-traces"""
    traces = data_trace / 3
    return traces

def assemble_rttrace_register2procs(data_trace, ref_time_offset):
    """Assemble real time trace and register two processes"""
    rt_trace = RtTrace()
    return rt_trace, rt_trace.registerRtProcess('integrate'), rt_trace.registerRtProcess('mwpIntegral', mem_time=240,
                                                                    ref_time=(data_trace.stats.starttime + ref_time_offset),
                                                                    max_time=120, gain=1.610210e+09)

def assemble_rttrace_register1proc(data_trace):
    """Assemble real time trace and register one process"""
    rt_trace = RtTrace()
    return rt_trace, rt_trace.registerRtProcess('scale', factor=0.1)

def append_and_autoprocess_packet(rt_trace, traces):
    """Append and auto-process packet data into RtTrace"""
    for tr in traces:
        processed_trace = rt_trace.append(tr, gap_overlap_check=True)

def postprocess_Mwp(rt_trace, epicentral_distance):    
    """Some post processing to get Mwp"""
    peak = np.amax(np.abs(rt_trace.data))
    mwp = calculateMwpMag(peak, epicentral_distance)
    return peak, mwp

def demoSAC():
    """
    from http://docs.obspy.org/packages/autogen/obspy.realtime.rttrace.RtTrace.html#obspy.realtime.rttrace.RtTrace
    
    >>> demoSAC()    
    12684 301.506 30.0855
    3 Trace(s) in Stream:
    II.TLY.00.BHZ | 2011-03-11T05:47:30.033400Z - 2011-03-11T05:51:01.384085Z | 20.0 Hz, 4228 samples
    II.TLY.00.BHZ | 2011-03-11T05:51:01.434086Z - 2011-03-11T05:54:32.784771Z | 20.0 Hz, 4228 samples
    II.TLY.00.BHZ | 2011-03-11T05:54:32.834771Z - 2011-03-11T05:58:04.185456Z | 20.0 Hz, 4228 samples
    1 2
    0.136404 8.78902911791
    
    """
    
    # 1. Read first trace of example SAC data file and extract contained time offset and epicentral distance of an earthquake:
    data_trace, ref_time_offset, epicentral_distance = read_example_trace_SAC()
    print len(data_trace), ref_time_offset, epicentral_distance

    # 2. Split given trace into a list of three sub-traces:
    traces = split_trace_into3(data_trace)
    print traces
    
    # 3. Assemble real time trace and register two processes:
    rt_trace, i1, i2 = assemble_rttrace_register2procs(data_trace, ref_time_offset)
    print i1, i2
    
    # 4. Append and auto-process packet data into RtTrace:
    append_and_autoprocess_packet(rt_trace, traces)
    
    # 5. Some post processing to get Mwp:
    peak, mwp = postprocess_Mwp(rt_trace, epicentral_distance)
    print peak, mwp
    
    # 6. Plot
    rt_trace.plot(color='red', tick_rotation=45, number_of_ticks=6)

def demo_rt_split_scale():
    
    drt = DemoRtSplitScale(scale_factor=0.2, num_splits=11)
    drt.rt_trace.plot(color='red', tick_rotation=45, number_of_ticks=6)

class DemoRtSplitScale(object):
    """Generator for RtTrace using trace split and rt scaling too."""
    
    def __init__(self, scale_factor=0.1, num_splits=3):
        self.scale_factor = scale_factor
        self.num_splits = num_splits
        
        # read example trace (with demean stream first)
        self.data_trace = self.read_example_trace_demean()
        
        # split given trace into a list of three sub-traces:
        self.traces = self.split_trace()
        
        # assemble real time trace and register rt proc (scale by factor)
        self.rt_trace, i1 = self.assemble_rttrace_register1proc()
    
        # append and auto-process packet data into RtTrace:
        self.append_and_autoprocess_packet()
    
    def read_example_trace_demean(self):
        """Read first trace of example data file"""
        st = read('/home/pims/dev/programs/python/pims/sandbox/data/slist_for_example.ascii')
        st.detrend('demean')
        data_trace = st[0]
        return data_trace

    def split_trace(self):
        """split given trace into a list of three sub-traces"""
        traces = self.data_trace / self.num_splits
        return traces

    def assemble_rttrace_register1proc(self):
        """assemble real time trace and register one process"""
        rt_trace = RtTrace()
        return rt_trace, rt_trace.registerRtProcess('scale', factor=self.scale_factor)

    def append_and_autoprocess_packet(self):
        """append and auto-process packet data into RtTrace"""
        for tr in self.traces:
            self.rt_trace.append(tr, gap_overlap_check=True)

if __name__ == "__main__":
    #import doctest
    #doctest.testmod(verbose=True)
    demo_rt_split_scale()
