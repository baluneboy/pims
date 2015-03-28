#!/usr/bin/env python
"""
An animated spectrogram, so take that LabVIEW!
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def getTimeInSeconds(fs, tmin, tmax):
    """generate time array (in seconds) based on sample rate (fs) and min/max"""
    dt = 1.0/fs
    return np.arange(tmin, tmax, dt)

def getSignal(t):
    """this has to be made '3d' for xyz accel signal, but for now..."""
    s1 = np.sin(2*np.pi*100*t)
    s2 = 2*np.sin(2*np.pi*500*t)
    # create a transient "chirp" (zero s2 signal before/after chirp)
    mask = np.where(np.logical_and(t>10, t<12), 1.0, 0.0)
    s2 = s2 * mask
    # add some noise into the mix
    nse = 0.01*np.random.randn(len(t))/1.0
    s = s1 + s2 + nse
    return s # the signal

def specgram(t, fs, Nfft, No):
    """spectrogram"""
    y = getSignal(t)
    Pxx, fbins, tbins, im = plt.specgram( y, Fs=fs, NFFT=Nfft, noverlap=No, cmap=plt.get_cmap('jet') )
    return im

fig = plt.figure()

def init():
    """initialize animation"""
    global fig, ax, t, fs, Nfft, No, tzero_text
    fs, Nfft, No = 2000, 1024, 512
    t = getTimeInSeconds(fs, 0.0, 20.0)     
    ax = fig.add_subplot(111) #, autoscale_on=False, xlim=(-2, 2), ylim=(-2, 2))
    tzero_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)
    im = specgram(t, fs, Nfft, No)
    return im, tzero_text

def animate(i):
    """perform animation step, return tuple of things that change"""
    global fig, ax, t, fs, Nfft, No, tzero_text
    t += 100.0/fs
    tzero_text.set_text('t[0] = %.3fs' % t[0])
    im = specgram(t, fs, Nfft, No)
    return im, tzero_text

def main():
    ani = animation.FuncAnimation(fig, animate, init_func=init, interval=50, blit=True) # interval in msec
    plt.show()    

if __name__ == '__main__':
    main()
