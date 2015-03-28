#!/usr/bin/env python

import numpy as np
from scipy import signal
from tempfile import SpooledTemporaryFile, NamedTemporaryFile
from pims.pad.padlowpasscreate import pad_lowpass_create
from pims.signal.filter import load_filter_coeffs, pad_lowpass_filtfilt, lowpass_filter_viafile
from pylab import figure, plot, xlabel, ylabel, xlim, ylim, title, grid, axes, show

ONE_HUNDRED_MB = 100.0 * 1024.0 * 1024.0

def generate_spooled_temp_filename(prefix):
    prefix += '_%s_%s' % (socket.gethostname(), parameters['timestamp'])
    #tf = SpooledTemporaryFile(max_size=11, mode='w+b', buffering=None, encoding=None, newline=None, suffix='.tmp', prefix=prefix + '_', dir=defaults['padPath'])
    tf = SpooledTemporaryFile(max_size=11, mode='w+b', buffering=None, encoding=None, newline=None, suffix='.tmp', prefix=prefix + '_', dir='/tmp')
    tf.close()
    return tf.name    

def get_dummy_data():
    # create 3-second signal that is the sum of two pure sine waves, with frequencies 2 Hz and 60 Hz, sampled at 500 Hz
    t = np.linspace(0.0, 3.0, 1501)
    xlow = np.sin(2 * np.pi * 2 * t)
    xhigh = np.sin(2 * np.pi * 60 * t)
    x = xlow + xhigh
    return x.astype('float32')

def get_temp_file():
    return SpooledTemporaryFile(max_size=ONE_HUNDRED_MB, dir='/tmp')

def read_tempfile_data(stf):
    stf.seek(0)
    data = stf.read()
    stf.close()
    return data

def filter_tempfile():
    pass
    
def main():
    #stf = SpooledTemporaryFile()
    stf = get_temp_file()
    data = get_dummy_data()
    np.save(stf, data)
    stf.seek(0)
    x = np.load(stf)   
    figure(1)
    plot(x)
    show()

def demo_data():
    return 'x' * 100 * 1024

def demo_name():
    global DEMODATA
    stf = NamedTemporaryFile(dir='/tmp')
    stf.write( DEMODATA )
    stf.seek(0)
    s = stf.read()
    stf.close()

def demo_spool():
    global DEMODATA
    stf = SpooledTemporaryFile(max_size=ONE_HUNDRED_MB, dir='/tmp')
    stf.write( DEMODATA )
    stf.seek(0)
    s = stf.read()
    stf.close()

def demo_filt():
    from numpy import cos, sin, pi, absolute, arange
    from scipy.signal import kaiserord, lfilter, firwin, freqz
    
    #------------------------------------------------
    # Create a signal for demonstration.
    #------------------------------------------------
    sample_rate = 100.0
    nsamples = 400
    t = arange(nsamples) / sample_rate
    x = cos(2*pi*0.5*t) + 0.2*sin(2*pi*2.5*t+0.1) + \
            0.2*sin(2*pi*15.3*t) + 0.1*sin(2*pi*16.7*t + 0.1) + \
                0.1*sin(2*pi*23.45*t+.8)
    
    #------------------------------------------------
    # Create a FIR filter and apply it to x.
    #------------------------------------------------
    
    # The Nyquist rate of the signal.
    nyq_rate = sample_rate / 2.0
    
    # The desired width of the transition from pass to stop,
    # relative to the Nyquist rate.  We'll design the filter
    # with a 5 Hz transition width.
    width = 5.0/nyq_rate
    
    # The desired attenuation in the stop band, in dB.
    ripple_db = 60.0
    
    # Compute the order and Kaiser parameter for the FIR filter.
    N, beta = kaiserord(ripple_db, width)
    
    # The cutoff frequency of the filter.
    cutoff_hz = 10.0
    
    # Use firwin with a Kaiser window to create a lowpass FIR filter.
    taps = firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
    
    # Use lfilter to filter x with the FIR filter.
    filtered_x = lfilter(taps, 1.0, x)
    
    #------------------------------------------------
    # Plot the FIR filter coefficients.
    #------------------------------------------------
    
    figure(1)
    plot(taps, 'bo-', linewidth=2)
    title('Filter Coefficients (%d taps)' % N)
    grid(True)
    
    #------------------------------------------------
    # Plot the magnitude response of the filter.
    #------------------------------------------------
    
    figure(2)
    clf()
    w, h = freqz(taps, worN=8000)
    plot((w/pi)*nyq_rate, absolute(h), linewidth=2)
    xlabel('Frequency (Hz)')
    ylabel('Gain')
    title('Frequency Response')
    ylim(-0.05, 1.05)
    grid(True)
    
    # Upper inset plot.
    ax1 = axes([0.42, 0.6, .45, .25])
    plot((w/pi)*nyq_rate, absolute(h), linewidth=2)
    xlim(0,8.0)
    ylim(0.9985, 1.001)
    grid(True)
    
    # Lower inset plot
    ax2 = axes([0.42, 0.25, .45, .25])
    plot((w/pi)*nyq_rate, absolute(h), linewidth=2)
    xlim(12.0, 20.0)
    ylim(0.0, 0.0025)
    grid(True)
    
    #------------------------------------------------
    # Plot the original and filtered signals.
    #------------------------------------------------
    
    # The phase delay of the filtered signal.
    delay = 0.5 * (N-1) / sample_rate
    
    figure(3)
    
    # Plot the original signal.
    plot(t, x)
    
    # Plot the filtered signal, shifted to compensate for the phase delay.
    plot(t-delay, filtered_x, 'r-')
    
    # Plot just the "good" part of the filtered signal.  The first N-1
    # samples are "corrupted" by the initial conditions.
    plot(t[N-1:]-delay, filtered_x[N-1:], 'g', linewidth=4)
    
    xlabel('t')
    grid(True)
    
    show()    
    
def demo_filtfilt():
    fs = 500        # sample rate (sa/sec)
    fN = 0.5 * fs   # Nyquist rate is half sample rate (Hz)
    fc = 6          # cut-off frequency (Hz)
    
    # create 3-second signal that is the sum of two pure sine waves, with frequencies 2 Hz and 60 Hz, sampled at 500 Hz
    t = np.linspace(0.0, 3.0, 1501)
    xlow = np.sin(2 * np.pi * 2 * t)
    xhigh = np.sin(2 * np.pi * 60 * t)
    x = xlow + xhigh
    y = pad_lowpass_filtfilt(x, fc, fs)
    xx = xlow
    yy = xhigh
    zz = xx + yy
    arr = np.column_stack((xx,yy,zz))
    print arr
    raise SystemExit

    #------------------------------------------------
    # Plot the original and filtered signals.
    #------------------------------------------------
      
    figure(1)
    
    # Plot the original signal.
    plot(t, x)
    
    # Plot the filtered signal, shifted to compensate for the phase delay.
    plot(t, y, 'w')
    
    xlabel('t')
    grid(True)
    
    show()  

def timeit_tempfiles():
    import timeit
    global DEMODATA
    DEMODATA = demo_data()    
    N = [1000, 2000, 4000, 8000, 16000]
    for num in N:
        ts = timeit.timeit("demo_spool()", setup="from __main__ import demo_spool", number=num)
        tn = timeit.timeit("demo_name()", setup="from __main__ import demo_name", number=num)
        print tn/ts, tn, ts, num

if __name__ == '__main__':
    
    #timeit_tempfiles()
    #demo_spool()
    #demo_filt()    
    #demo_filtfilt()
    #main()

    # ---------------------------------------------------------------------------------------------------
    # USE THE LEGACY MAT FILE
    # ---------------------------------------------------------------------------------------------------    
    #filt_mat_file = '/home/pims/dev/programs/octave/pad/filters/testing/padlowpassauto_500d0sps_6d0hz.mat'
    filt_mat_file = '/home/pims/dev/programs/octave/pad/filters/testing/padlowpassauto_500sps_5hz.mat'
    fin = '/home/pims/dev/programs/python/pims/sandbox/data/fin.dat'
    fout = '/tmp/FOUT.DAT'
    lowpass_filter_viafile(filt_mat_file, fin, fout)
