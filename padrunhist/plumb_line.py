#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


def find_nearest_index(array, value):
    idx = (np.abs(array - value)).argmin()
    return idx


def find_nearest(array, value):
    idx = find_nearest_index(array, value)
    return array[idx]


def plumblines(hLine, yvals, **kwargs):
    """
    Add plumb lines with annotations to axes.

    Call signature::

      plumblines(hLine, yvals, **kwargs)

    Draw a vertical line at *x* from *ymin* to *ymax*.  With the
    default values of *ymin* = 0 and *ymax* = 1, this line will
    always span the vertical extent of the axes, regardless of the
    ylim settings, even if you change them, e.g., with the
    :meth:`set_ylim` command.  That is, the vertical extent is in
    axes coords: 0=bottom, 0.5=middle, 1.0=top but the *x* location
    is in data coordinates.

    Return value is the :class:`~matplotlib.lines.Line2D`
    instance.  kwargs are the same as kwargs to plot, and can be
    used to control the line properties.  e.g.,

    * draw a thick red vline at *x* = 0 that spans the yrange::

        >>> axvline(linewidth=4, color='r')

    * draw a default vline at *x* = 1 that spans the yrange::

        >>> axvline(x=1)

    * draw a default vline at *x* = .5 that spans the the middle half of
      the yrange::

        >>> axvline(x=.5, ymin=0.25, ymax=0.75)

    Valid kwargs are :class:`~matplotlib.lines.Line2D` properties that are
    applied to plumb line objects (with the exception of 'transform')

    """

    # get some properties of line object
    ax = hLine.axes
    yd = hLine.get_ydata()
    xd = hLine.get_xdata()

    # plumb lines' mins will be lower bound of axes limits
    ymin = ax.get_ybound()[0]  # ignore 2nd (ymax) element
    xmin = ax.get_xbound()[0]

    # iterate over yvals, use interpolation to draw plumb lines, dots and annotations
    reddots, horlines, verlines, anns = []
    for y in yvals:
        x = np.interp(y, yd, xd)  # we swap x and y here for interpolating the way we want it
        verlines.append(plt.vlines(x, ymin, y, colors='r', linestyles='--', label='', hold=None, **kwargs))
        horlines.append(plt.hlines(y, xmin, x, colors='r', linestyles='--', label='', hold=None, **kwargs))
        reddots.append(plt.plot(x, y, 'ro'))
        anns.append(ax.annotate('(%s, %s)' % (x, y), xy=(x, y), textcoords='data'))

    return reddots, horlines, verlines, anns


# dummy data
t = np.linspace(0, 0.1, 500)
s = signal.sawtooth(2 * np.pi * 5 * t) + 1.0
hLine, = plt.plot(t, s)

# set axis lims first BEFORE plumb lines
plt.axis([0, 0.1, 0, 1])

# draw 2 plumb lines
yvals = [0.5, 0.95, ]
plines = plumblines(hLine, yvals)
plt.grid()
plt.show()
