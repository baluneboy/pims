#!/usr/bin/env python

import numpy as np

def herons_area(a, b, c):
    f1 = a + (b + c)
    f2 = c - (a - b)
    f3 = c + (a - b)
    f4 = a + (b - c)
    return (f1 * f2 * f3 * f4) ** 0.5 / 4.0
    
def area(a, b, theta):
    return 0.5 * a * b * np.sin(np.pi * theta / 180.0)

for a in range(179500, 180000):
    angle = a / 1000.0
    print '%.3f, %.4e' % (angle, area(1, 1, angle))
