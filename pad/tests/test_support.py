#!/usr/bin/python

import numpy as np
from copy import deepcopy
from obspy import UTCDateTime, Trace, read
from pims.pad.padstream import PadStream
from pims.signal.ramp import ramp
#from scipy import signal

def filter_setup():
    t = np.linspace(0, 10.0, 5001)
    # for xhigh, use a = sqrt(2) so rms = a / sqrt(2) = 1
    xhigh = np.sqrt(2) * np.sin(2 * np.pi * 25 * t) # 25 Hz
    xlow = np.sin(2 * np.pi * 2 * t)                # 2 Hz
    x = xlow + xhigh
    return t, x, xlow, xhigh

def build_sines():
    t, x, xlow, xhigh = filter_setup()
    x = xlow + xhigh
    y = xlow
    z = xhigh
    header = {'network': 'KH', 'station': 'SINE',
              'starttime': UTCDateTime(2011, 12, 10, 6, 30, 00),
              'npts': 5001, 'sampling_rate': 500.0,
              'channel': 'x'}        
    tracex = Trace(data=x, header=deepcopy(header))
    header['channel'] = 'y'
    tracey = Trace(data=y, header=deepcopy(header))
    header['channel'] = 'z'
    tracez = Trace(data=z, header=deepcopy(header))    
    return tracex, tracey, tracez
    
def build_ramps(npts):
    slopes = [11.1, 0, -9.9] # x, y, and z
    intercepts = [-5.0, -3.0, 1.0]
    t = np.linspace(0, 20*np.pi, npts)
    x = ramp(t, slope=slopes[0], yint=intercepts[0], noise=True, noise_amplitude=5)
    y = ramp(t, slope=slopes[1], yint=intercepts[1], noise=True, noise_amplitude=5)
    z = ramp(t, slope=slopes[2], yint=intercepts[2], noise=True, noise_amplitude=5)
    header = {'network': 'KH', 'station': 'RAMP',
              'starttime': UTCDateTime(2011, 12, 10, 6, 30, 00),
              'npts': 5001, 'sampling_rate': 500.0,
              'channel': 'x'}        
    tracex = Trace(data=x, header=deepcopy(header))
    header['channel'] = 'y'
    tracey = Trace(data=y, header=deepcopy(header))
    header['channel'] = 'z'
    tracez = Trace(data=z, header=deepcopy(header))    
    return tracex, tracey, tracez

def view_waveforms():
    tracex, tracey, tracez = build_ramps(5001)
    ramps_substream = PadStream(traces=[tracex, tracey, tracez])
    ramps_substream.plot()
    
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
    
if __name__ == '__main__':
    #view_waveforms(); raise SystemExit
    view_filter_setup(); raise SystemExit