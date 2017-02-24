#!/usr/bin/env python

import numpy as np

class Site(object):
    
    def __init__(self, a):
        self.a = a
        
    def set_a(self, new_a):
        self.a = new_a
        
v_site = np.vectorize(Site)

init_arr = np.arange(9).reshape((3, 3))

lattice = np.empty((3, 3), dtype=object)
lattice[:,:] = v_site(init_arr)

print lattice