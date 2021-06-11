"""
Ported by Massimo Vassalli [http://mv.nanoscopy.eu massimo.vassalli@gmail.com]

This file is a helper for the use of the included functions, ported from 
the original example set. Example DNA data was originally distributed with
the Matlab implementation
"""

# Load DNA copy-number data
import numpy as np
import matplotlib.pylab as plt
import warnings

from pwc_jumppenalty import pwc_jumppenalty

y = np.loadtxt('dnagwas.txt')
N = len(y)
x = np.zeros((N, 1))

# Robust jump penalization

# I expect to see RuntimeWarnings in this block
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)
    #x[:, 0] = pwc_jumppenalty(y, square=False)  # robust jump penalization
    x = pwc_jumppenalty(y, square=False)  # robust jump penalization

# Plot
plt.figure()
plt.plot(y, color=[0.6, 0.6, 0.6])
plt.plot(x, 'b-')
plt.title('pwc_jumppenalty for step detection')
plt.ylabel('DNA Noisy and Cleaned Data')
plt.show()
