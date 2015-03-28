#!/usr/bin/env python

import math
import numpy as np
import pandas as pd

def smart_ylims(minval, maxval):
    span = maxval - minval
    ymin = np.ceil( minval - 0.1 * span )
    ymax = np.ceil( maxval + 0.1 * span )
    return (ymin, ymax)

def round2multiple(target, n):
    if not isinstance(target, int):
        raise ValueError('target must be int')
    if n > 0:
        return np.ceil(n/float(target)) * target;
    elif n < 0:
        return np.floor(n/float(target)) * target;
    else:
        return n

# read csvfile like for JAXA plot parameters
def read_plot_params(csvfile):
    """read csvfile like for JAXA plot parameters"""
    df = pd.read_csv(csvfile)
    
# nice_number(value, round=False) -> float
def nice_number(value, round=False):
    """nice_number(value, round=False) -> float"""
    exponent = math.floor(math.log(value, 10))
    fraction = value / 10 ** exponent

    if round:
        if fraction < 1.5: nice_fraction = 1.
        elif fraction < 3.: nice_fraction = 2.
        elif fraction < 7.: nice_fraction = 5.
        else: nice_fraction = 10.
    else:
        if fraction <= 1: nice_fraction = 1.
        elif fraction <= 2: nice_fraction = 2.
        elif fraction <= 5: nice_fraction = 5.
        else: nice_fraction = 10.

    return nice_fraction * 10 ** exponent

# nice_bounds(axis_start, axis_end, num_ticks=10) -> (nice_axis_start, nice_axis_end, nice_tick_width)
def nice_bounds(axis_start, axis_end, num_ticks=10):
    """
    nice_bounds(axis_start, axis_end, num_ticks=10) -> tuple
    @return: tuple as (nice_axis_start, nice_axis_end, nice_tick_width)
    """
    axis_width = axis_end - axis_start
    if axis_width == 0:
        nice_tick = 0
    else:
        nice_range = nice_number(axis_width)
        nice_tick = nice_number(nice_range / (num_ticks -1), round=True)
        axis_start = math.floor(axis_start / nice_tick) * nice_tick
        axis_end = math.ceil(axis_end / nice_tick) * nice_tick
    nice_axis_start, nice_axis_end, nice_tick_width = axis_start, axis_end, nice_tick
    return nice_axis_start, nice_axis_end, nice_tick_width

def demo_nice_bounds():
    from wxmplot import PlotApp
    axis_start = 0
    num_ticks = 10
    axis_ends = np.linspace(1, 301, 601)
    nice_axis_ends = []
    nice_tick_widths = []
    for axis_end in axis_ends:
        nb = nice_bounds(axis_start, axis_end, num_ticks=num_ticks)
        #print axis_end, " -> ", nb
        nice_axis_ends.append(nb[1])
        nice_tick_widths.append(nb[2])

    app = PlotApp()
    app.plot(axis_ends, nice_axis_ends, title='WXMPlot Demo', label='AE vs NAE',
             ylabel='nice_axis_ends', xlabel='axis_ends')
    
    app.oplot(axis_ends, nice_tick_widths, y2label='nice_tick_widths', side='right', ymin=0)
    
    app.write_message('Try Help->Quick Reference')
    app.run()
    
if __name__ == "__main__":
    demo_nice_bounds()