#!/usr/bin/env python

from pylive import live_plotter_xy
import numpy as np
import warnings

warnings.filterwarnings("ignore", ".*GUI is implemented")

size = 100
x_vec = np.linspace(0,1,size+1)[0:-1]
y_vec = np.random.randn(len(x_vec))
line1 = []
while True:
    rand_val = np.random.randn(1)
    y_vec[-1] = rand_val
    line1 = live_plotter_xy(x_vec,y_vec,line1)
    y_vec = np.append(y_vec[1:],0.0)
