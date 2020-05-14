#!/usr/bin/python

import os
import numpy as np
from scipy import io, signal
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    # y = lfilter(b, a, data)
    y = signal.filtfilt(b, a, data)
    return y


def run_example():
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import freqz

    # Sample rate and desired cutoff frequencies (in Hz).
    fs = 500.0
    lowcut = 5.15
    highcut = 5.65

    # Plot the frequency response for a few different orders.
    plt.figure(1)
    plt.clf()
    for order in [2, 3]:
        b, a = butter_bandpass(lowcut, highcut, fs, order=order)
        w, h = freqz(b, a, worN=2000)
        plt.plot((fs * 0.5 / np.pi) * w, abs(h), label="order = %d" % order)

    plt.plot([0, 0.5 * fs], [np.sqrt(0.5), np.sqrt(0.5)],
             '--', label='sqrt(0.5)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain')
    plt.grid(True)
    plt.legend(loc='best')

    # Filter a noisy signal.
    T = 10.0
    nsamples = int(T * fs)
    t = np.linspace(0, T, nsamples, endpoint=False)
    a = 0.02
    f0 = 5.25
    x = 0.1 * np.sin(2 * np.pi * 1.2 * np.sqrt(t))
    x += 0.01 * np.cos(2 * np.pi * 312 * t + 0.1)
    x += a * np.cos(2 * np.pi * f0 * t + .11)
    x += 0.03 * np.cos(2 * np.pi * 2000 * t)
    plt.figure(2)
    plt.clf()
    plt.plot(t, x, label='Noisy signal')

    my_order = 3
    y = butter_bandpass_filter(x, lowcut, highcut, fs, order=my_order)
    plt.plot(t, y, label='Filtered signal (%g Hz, order=%d)' % (f0, my_order))
    plt.xlabel('time (seconds)')
    plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('tight')
    plt.legend(loc='upper left')

    plt.show()


def load_filter_coeffs(mat_file):
    """return tuple (b, a, fsNew) from matlab mat-file"""
    matdict = io.loadmat(mat_file)
    a = matdict['aDen']
    b = matdict['bNum']
    fsNew = matdict['fsNew']
    # need ravel method to "unnest" numpy ndarray
    return a.ravel(), b.ravel(), fsNew.ravel()[0]


def pad_lowpass_create(fcNew, fsOld):
    # FIXME with actual creation, but for now, just verify via file load
    # SEE OCTAVE IMPLEMENTATION AT ~/dev/programs/octave/pad/padlowpasscreate.m
    dir_mats = '/home/pims/dev/programs/octave/pad/filters/testing'
    strFsOld = '%.1f' % fsOld
    strFcNew = '%.1f' % fcNew
    fname = 'padlowpassauto_%ssps_%shz.mat' % (strFsOld.replace('.', 'd'), strFcNew.replace('.', 'd'))
    filter_mat_file = os.path.join(dir_mats, fname)
    # if this next line errors, then LET IT ERROR because we have not implemented FIXME yet
    a, b, fsNew = load_filter_coeffs(filter_mat_file)
    return a, b, fsNew


def pad_lowpass_filtfilt(x, fcNew, fsOld):
    """return low-pass filtered data"""
    a, b, fsNew = pad_lowpass_create(fcNew, fsOld)
    y = signal.filtfilt(b, a, x)
    return y


def lowpass_filter_viafile(filter_mat_file, infile, outfile, fsOld):
    """read infile, load filter coeffs from filter_mat_file, apply filtfilt, & write filtered/resampled data to outfile"""
    # load filter coeffs from file
    a, b, fsNew = load_filter_coeffs(filter_mat_file)
    
    # read input data file
    data = np.fromfile(infile, 'float32')
    
    # reshape as XYZ columns to apply columnwise filtfilt    
    data = np.reshape(data, [-1, 3])
    
    # apply filter
    y = signal.filtfilt(b, a, data, axis=0)
    
    # resample
    numin = y.shape[0]
    numout = numin * fsNew / fsOld
    yout = signal.resample(y, numout)
    
    # flatten columns so we can write proper order to outfile
    yout = yout.flatten(order='C')
    
    # write to outfile (see numpy help on tofile for possible pitfalls)
    yout.astype('float32').tofile(outfile)

def demo():
    # ---------------------------------------------------------------------------------------------------
    # USE THE LEGACY MAT FILE
    # ---------------------------------------------------------------------------------------------------    
    filt_mat_file = '/home/pims/dev/programs/octave/pad/filters/testing/padlowpassauto_500d0sps_6d0hz.mat'
    #filt_mat_file = '/home/pims/dev/programs/octave/pad/filters/testing/padlowpassauto_500sps_5hz.mat'    
    a, b, fsNew = load_filter_coeffs(filt_mat_file)
    print(b)
    print(a)
    print(fsNew)


def demo2():
    a, b, fsNew = pad_lowpass_create(6.0, 500.0)
    print(b, a, fsNew)


def demo3():
    filt_mat_file = '/home/pims/dev/programs/octave/pad/filters/testing/padlowpassauto_500d0sps_6d0hz.mat'
    infile = '/home/pims/dev/programs/python/pims/sandbox/data/fin.dat'
    outfile = '/tmp/fo.dat'
    lowpass_filter_viafile(filt_mat_file, infile, outfile)


def demo_spectrogram():

    fs = 10e3
    N = 1e5
    amp = 2 * np.sqrt(2)
    noise_power = 0.01 * fs / 2
    time = np.arange(N) / float(fs)
    mod = 500 * np.cos(2 * np.pi * 0.25 * time)
    carrier = amp * np.sin(2 * np.pi * 3e3 * time + mod)
    noise = np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
    noise *= np.exp(-time / 5)
    x = carrier + noise

    f, t, Sxx = signal.spectrogram(x, fs)
    plt.pcolormesh(t, f, Sxx)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()


def demo_sams_spectrogram():
    from ugaudio.load import padread

    filename = 'D:/pad/year2020/month04/day27/sams2_accel_121f08006/2020_04_27_09_06_28.344+2020_04_27_09_37_14.421.121f08006'
    a = padread(filename)
    y = a[:, 2]
    fs = 142.0
    nperseg = 4096
    f, t, Sxx = signal.spectrogram(y, fs, nperseg=nperseg, noverlap=nperseg/2)

    print(np.log10(Sxx))
    return

    plt.pcolormesh(t, f, np.log10(Sxx))
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()


if __name__=="__main__":
    #demo()
    #demo2()
    # demo3()
    # run_example()
    demo_sams_spectrogram()
