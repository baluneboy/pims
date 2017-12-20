#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt


def find_nearest_index(array, value):
    """Return index where array's value(s) is/are nearest to value."""    
    idx = (np.abs(array - value)).argmin()
    return idx


def find_nearest(array, value):
    """Return array's value(s) nearest to value."""
    idx = find_nearest_index(array, value)
    return array[idx]


def plumblines(hLine, yvals, **kwargs):
    """ Add plumb lines with annotations to axes.

    Call signature::

      plumblines(hLine, yvals, **kwargs)

    Draw a horizontal and vertical line segment that 'plumbs' each of yvals.
    Also, annotate with red dots on curve whos handle is hLine and annotate
    with (xval, yval) too.
    Plot axes xmin will be left end of each horizontal segment and ymin will
    be bottom end of each vertical segment.

    Return a tuple: reddots, horlines, verlines, anns of
    reddots, horlines and verlines are :class:`~matplotlib.lines.Line2D` instances
    anns are :class:`~matplotlib.axes.annotate` instances.
    
    Also, kwargs can be used to control the line properties.
    e.g.,

    * draw thick red lines::

        >>> reddots, horlines, verlines, anns = plumblines(hLine, yvals, linewidth=4, color='r')

    Valid kwargs are :class:`~matplotlib.lines.Line2D` properties that are
    applied to plumb line objects (with the exception of 'transform')

    """

    # get some properties of line object
    ax = hLine.axes
    yd = hLine.get_ydata()
    xd = hLine.get_xdata()

    # plumb lines' mins will be lower bound of axes limits
    ymin, ymax = ax.get_ybound()
    xmin, xmax = ax.get_xbound()

    # iterate over yvals, use interpolation to draw plumb lines, dots and annotations
    reddots, horlines, verlines, anns, xvals = [], [], [], [], []
    for y in yvals:
        x = np.interp(y, yd, xd)  # we swap x and y here for interpolating the way we want it
        verlines.append(plt.vlines(x, ymin, y, colors='r', linestyles='--', label='', hold=None, **kwargs))
        horlines.append(plt.hlines(y, xmin, x, colors='r', linestyles='--', label='', hold=None, **kwargs))
        reddots.append(plt.plot(x, y, 'ro'))
        anns.append(ax.annotate('(%0.2fmg, %d%%)' % (x, y), xy=(x + 0.3, y - 5), textcoords='data',
                    horizontalalignment='left', verticalalignment='middle',
                    weight='bold', color='r'))
        xvals.append(x)

    return reddots, horlines, verlines, anns, xvals


def demo1():
    from scipy import signal
    
    # plot some dummy data (a ramp portion of sawtooth)
    t = np.linspace(0, 0.1, 500)
    s = signal.sawtooth(2 * np.pi * 5 * t) + 1.0
    
    # note tuple unpacking on LHS to get hLine out of list that gets returned    
    hLine, = plt.plot(t, s)
    
    # set axis lims BEFORE plumb lines
    plt.axis([-0.01, 0.11, -0.01, 1.1])
    
    # draw typical plumb lines with annotation
    yvals = [0.5, 0.95, ]  # one set of annotations for each of these values
    reddots, horlines, verlines, anns = plumblines(hLine, yvals)
    
    # now one thick blue one too
    new_yvals = [0.2, ]
    reddots, horlines, verlines, anns = plumblines(hLine, new_yvals, linewidth=4, color='b')
    
    # arrow
    plt.gca().annotate('95th percentile', xy=(0.01, 0.3), xytext=(0.03, 0.15),
                arrowprops=dict(facecolor='black', shrink=0.05))    
    
    plt.grid()
    plt.show()


def demo():
    from scipy import signal
    
    # plot some dummy data (a ramp portion of sawtooth)
    t = np.linspace(0, 25, 500)
    s = np.linspace(0, 100, 500)
    
    # note tuple unpacking on LHS to get hLine out of list that gets returned    
    hLine, = plt.plot(t, s)
    
    # set axis lims BEFORE plumb lines
    plt.axis([-1, 26, -1, 111])
    
    # draw typical plumb lines with annotation
    yvals = [50, 95, ]  # one set of annotations for each of these values
    reddots, horlines, verlines, anns = plumblines(hLine, yvals)
    
    plt.grid()
    plt.show()


if __name__ == '__main__':
    #demo1()
    demo()
    