#!/usr/bin/env python

"""
Tick locating and formatting
============================

See /usr/lib/pymodules/python2.7/matplotlib/ticker.py

This module contains classes to support completely configurable tick
locating and formatting.  Although the locators know nothing about
major or minor ticks, they are used by the Axis class to support major
and minor tick locating and formatting.  Generic tick locators and
formatters are provided, as well as domain specific custom ones..

Tick locating
-------------

The Locator class is the base class for all tick locators.  The
locators handle autoscaling of the view limits based on the data
limits, and the choosing of tick locations.

The Locator subclasses defined here are

:class:`PositiveLinearLocator`
    evenly spaced ticks from zero to max with cushion for
    wide-n-glide GMT xtick labels

You can define your own locator by deriving from Locator.  You must
override the __call__ method, which returns a sequence of locations,
and you will probably want to override the autoscale method to set the
view limits from the data limits.

If you want to override the default locator, use one of the above or a
custom locator and pass it to the x or y axis instance.  The relevant
methods are::

  ax.xaxis.set_major_locator( xmajorLocator )
  ax.xaxis.set_minor_locator( xminorLocator )
  ax.yaxis.set_major_locator( ymajorLocator )
  ax.yaxis.set_minor_locator( yminorLocator )

"""

import numpy as np
from matplotlib import transforms as mtransforms
from matplotlib.ticker import LinearLocator
from pims.gui.plotutils import smart_ylims

class PositiveLinearLocator(LinearLocator):
    """
    Determine the tick locations with bottom tick clamped at zero
    and some cushion below bottom tick to allow for wide-n-glide
    GMT xtick labels

    The first time this function is called it will try to set the
    number of ticks to make a nice tick partitioning.  Thereafter the
    number of ticks will be fixed so that interactive navigation will
    be nice.
    """

    #def __init__(self, numticks=None, presets=None, decimals=2):
    #    """
    #    Use presets to set locs based on lom.  A dict mapping vmin, vmax->locs
    #    """
    #    self.decimals = decimals
    #    #super(PositiveLinearLocator, self).__init__(numticks=numticks, presets=presets) # NEW STYLE
    #    LinearLocator.__init__(self, numticks=numticks, presets=presets) # BUT MPL USES OLD STYLE BASE CLASS

    def raise_if_negative(self, locs):
        'raise a RuntimeError if Locator has negative-valued ticks in locs; otherwise, return locs'
        if min(locs) < 0:
           dmin, dmax = self.axis.get_data_interval()
           raise RuntimeError( 'Locator attempting to generate negative ticks; NOTE: data ranges from %g to %g' % (dmin, dmax) )
        return locs

    def __call__(self):
        'Return the locations of the ticks'

        vmin, vmax = self.axis.get_view_interval()
        vmin, vmax = mtransforms.nonsingular(vmin, vmax, expander = 0.05)
        if vmax<vmin:
            vmin, vmax = vmax, vmin

        if (vmin, vmax) in self.presets:
            return self.presets[(vmin, vmax)]

        if self.numticks is None:
            self._set_numticks()

        if self.numticks==0: return []

        #cushioned_lims = smart_ylims(vmin, vmax)
        ticklocs = np.linspace(vmin, vmax, self.numticks)
        #print cushioned_lims, vmin, vmax, ticklocs
        blessed_ticklocs = self.raise_if_negative(ticklocs)
        return self.raise_if_exceeds(blessed_ticklocs)

    def _set_numticks(self):
        self.numticks = 5  # todo; be smart here; this is just for dev

    def view_limits(self, vmin, vmax):
        'Try to choose the view limits intelligently'

        if vmax<vmin:
            vmin, vmax = vmax, vmin

        if vmin==vmax:
            vmin-=1
            vmax+=1

        exponent, remainder = divmod(math.log10(vmax - vmin), 1)

        if remainder < 0.5:
            exponent -= 1
        scale = 10**(-exponent)
        vmin = math.floor(scale*vmin)/scale
        vmax = math.ceil(scale*vmax)/scale

        return mtransforms.nonsingular(vmin, vmax)

class CushionedLinearLocator(LinearLocator):

    def __call__(self):
        'Return the locations of the ticks'

        vmin, vmax = self.axis.get_view_interval()
        vmin, vmax = mtransforms.nonsingular(vmin, vmax, expander = 0.05)
        if vmax<vmin:
            vmin, vmax = vmax, vmin

        if (vmin, vmax) in self.presets:
            return self.presets[(vmin, vmax)]

        if self.numticks is None:
            self._set_numticks()

        if self.numticks==0: return []

        # swap zero for actual vmin when doing linspace here
        #ticklocs = np.linspace(vmin, vmax, self.numticks) # original
        ticklocs = np.linspace(0, vmax, self.numticks)
        return self.raise_if_exceeds(ticklocs)

    def _set_numticks(self):
        self.numticks = 5  # todo; be smart here; this is just for dev

__all__ = ('PositiveLinearLocator',
           'CushionedLinearLocator',
            )
