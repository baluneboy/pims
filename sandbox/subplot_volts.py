#!/usr/bin/env python

"""Example illustrating the use of plt.subplots().

This function creates a figure and a grid of subplots with a single call, while
providing reasonable control over how the individual plots are created.  For
very refined tuning of subplot creation, you can still use add_subplot()
directly on a new figure.
"""

import numpy as np
import matplotlib.pyplot as plt

"""
EE_FIELD  maps2 VARNAME isa MTYPE
----------------------------------
SE 0 Temp X --> se0tempx    TEMPS
SE 0 Temp Y --> se0tempy    TEMPS
SE 0 Temp Z --> se0tempz    TEMPS
SE 0 +5V    --> se0p5v      VOLTS
HEAD 0 +15V --> se0p15v     VOLTS
HEAD 0 -15V --> se0n15v     VOLTS
SE 1 Temp X --> se1tempx    TEMPS
SE 1 Temp Y --> se1tempy    TEMPS
SE 1 Temp Z --> se1tempz    TEMPS
SE 1 +5V    --> se1p5v      VOLTS
HEAD 1 +15V --> se1p15v     VOLTS
HEAD 1 -15V --> se1n15v     VOLTS
Base Temp   --> basetemp    TEMPS
PC104 +5V   --> pc104p5v    VOLTS
Ref +5V     --> refp5v      VOLTS
Ref 0V      --> ref0v       VOLTS

"""

class FigureVolts(object):
    
    def __init__(self, nrows, ncols, save_file):
        self.nrows = nrows
        self.ncols = ncols
        self.save_file = save_file
        self.figsize = (10, 7.5)
        self.dpi = 300
        self.fig, self.axarr = plt.subplots(nrows, ncols, sharex='col', sharey='row', figsize=self.figsize, dpi=self.dpi)

    def add_subplot(self, r, c, x, y, title):
        self.axarr[r, c].plot(x, y)
        self.axarr[r, c].set_title(title)
    
    def save(self):
        self.fig.savefig(self.save_file, dpi=self.dpi, orientation='landscape', transparent=False)

# Simple data to display in various forms
x = np.linspace(0, 2 * np.pi, 400)
y = np.sin(x ** 2)

plt.close('all')

# return RxC array of subplots in 2-d array
# rows share y-ticks, columns share x-ticks
nrows, ncols = 4, 9
save_file = '/tmp/volts.png'
fv = FigureVolts(nrows, ncols, save_file)
for r in range(nrows):
    for c in range(ncols):
        fv.add_subplot(r, c, x, y, 'V%d%d' % (r, c) )

# hide x ticks for top plots and y ticks for right plots
plt.setp([a.get_xticklabels() for a in fv.axarr[0, :]], visible=False)
plt.setp([a.get_yticklabels() for a in fv.axarr[:, 1]], visible=False)

# make subplots a bit farther from each other
# DEFAULTS ARE:
# left  = 0.125  # the left side of the subplots of the figure
# right = 0.9    # the right side of the subplots of the figure
# bottom = 0.1   # the bottom of the subplots of the figure
# top = 0.9      # the top of the subplots of the figure
# wspace = 0.2   # the amount of width reserved for blank space between subplots,
#                # expressed as a fraction of the average axis width
# hspace = 0.2   # the amount of height reserved for white space between subplots,
                 # expressed as a fraction of the average axis height
fv.fig.subplots_adjust(left=0.1, hspace=0.25, wspace=0.15)

#plt.show()

fv.save()
