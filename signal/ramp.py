#!/usr/bin/python

# Author: Ken Hrovat, 2014
# see /usr/lib/python2.7/dist-packages/scipy/signal/waveforms.py
# for similar work done by: Travis Oliphant

from numpy import asarray, zeros, place, nan, mod, pi, extract, log, sqrt, \
     exp, cos, sin, polyval, polyint, random

def ramp(t, slope=1.0, yint=-1.0, noise=False, noise_amplitude=2.0):
    """
    Return a ramp waveform with some noise.

    The ramp waveform (line) has slope, yint(ercept) on the
    interval 0 to max(t)

    Parameters
    ----------
    t : array_like
        Time.
    slope : float, optional
        slope of the ramp waveform. Default is 1.
    noise : boolean, optional
        include noise riding on the ramp. Default is False.

    Returns
    -------
    y : ndarray
        Output array containing the ramp waveform.

    """
    t = asarray(t)
    y = slope * t + yint
    if noise:
        a, b = -noise_amplitude, noise_amplitude
        n = (b - a) * random.random_sample(len(t),) + a
        y = y + n
    return y

if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    t = np.linspace(0, 20*np.pi, 500)
    plt.plot(t, ramp(t, noise=True, noise_amplitude=5))
    plt.show()

