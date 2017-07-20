#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter


def demo_fit(example=1):
    r"""Smooth data with a Savitzky-Golay filter.

    Example 1
    ---------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savgol_filter(y, 31, 4)

    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()

    Example 2
    ---------
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x) + np.random.random(100) * 0.2
    yhat = savgol_filter(y, 51, 3)  # window size 51, polynomial order 3

    plt.plot(x, y, label='Noisy Signal')
    plt.plot(x, yhat, color='red', label='Filtered Signal')
    plt.legend()
    plt.show()

    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """

    if example==1:
        t = np.linspace(-4, 4, 500)
        y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
        ysg = savgol_filter(y, 31, 4)

        plt.plot(t, y, label='Noisy signal')
        plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
        plt.plot(t, ysg, 'r', label='Filtered signal')
        plt.legend()
        plt.show()
    elif example==2:
        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(x) + np.random.random(100) * 0.2
        yhat = savgol_filter(y, 51, 3)  # window size 51, polynomial order 3

        # TODO find out why Filtered Signal does not have "near zero" mean close to Original Signal's zero mean
        plt.plot(x, y, label='Noisy Signal')
        plt.plot(x, np.sin(x), label='Original Signal')
        plt.plot(x, yhat, color='red', label='Filtered Signal')
        plt.legend()
        plt.show()
    else:
        raise Exception('there is no example #%d' % example)

if __name__ == '__main__':
    demo_fit(example=2)
