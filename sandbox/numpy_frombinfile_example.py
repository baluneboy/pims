#!/usr/bin/env python

import numpy as np

fname = '/Users/ken/Downloads/2014_10_17_06_54_14.883-2014_10_17_06_54_44.573.121f03006'
with open(fname, "rb") as f: 
    A = np.fromfile(f, dtype=np.float32)
B = np.reshape(A, (-1, 4))
print B