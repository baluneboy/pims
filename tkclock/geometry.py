#!/usr/bin/env python

"""geometry

W = width of clock window
D = width of display
H = number of hours to traverse width of display
dt = time step in minutes
k = n*dt = time value after n steps
num = numerator = k * (D - W)
den = denominator = 60 * H

So, the x-value (in px) for right edge of clock window as function of time is:
x(k) = W + ( num / den )

"""

import time
import math
import warnings
import numpy as np
from datetime import datetime
from Tkinter import Tk
from pims.utils.pimsdateutil import sec_since_midnight

# need this to override warnings default "only once/first"
warnings.simplefilter('always', UserWarning)

# tk geometry set with limit checking
class TkGeometryKeeper(object):
    """tk geometry set with limit checking"""
    
    root = Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    def __init__(self, w, h, x, y, sound_on=False):
        self.sound_on = sound_on
        self.set_w( w )
        self.set_h( h )
        self.set_x( x )
        self.set_y( y )

    def __str__(self):
        return '%dx%d+%d+%d' % (self.w, self.h, self.x, self.y)

    # make sure we stay in bounds
    def _get_value_in_range(self, value, min_val, max_val):
        """make sure we stay in bounds"""
        if value < min_val:
            msg = 'value cannot be less than lower limit of %d' % min_val
            val = min_val
        elif value > max_val:
            msg = 'value cannot be more than upper limit of %d' % max_val
            val = max_val
        else:
            msg = None
            val = value
        #if msg and self.sound_on: playsound(440, 1)
        return val, msg

    # set width without going out of bounds
    def set_w(self, w):
        """set width without going out of bounds"""
        val, msg = self._get_value_in_range(w, 0, self.screen_width)
        self.w = val
        if msg: warnings.warn('width ' + msg)

    # set height without going out of bounds
    def set_h(self, h):
        """set height without going out of bounds"""
        val, msg = self._get_value_in_range(h, 0, self.screen_height)
        self.h = val
        if msg: warnings.warn('height ' + msg)
        
    # set x-coordinate without going out of bounds
    def set_x(self, x):
        """set x-coordinate without going out of bounds"""
        val, msg = self._get_value_in_range(x, 0, self.screen_width)
        self.x = val
        if msg: warnings.warn('x-coordinate ' + msg)

    # set y-coordinate without going out of bounds
    def set_y(self, y):
        """set y-coordinate without going out of bounds"""
        val, msg = self._get_value_in_range(y, 0, self.screen_height)
        self.y = val
        if msg: warnings.warn('y-coordinate ' + msg)

# tk geometry set with limit checking with circular x-value generator method
class TkGeometrySlider(TkGeometryKeeper):
    """tk geometry set with limit checking with circular x-value generator method"""
    
    def __init__(self, w, h, x, y, sound_on=False):
        super(TkGeometrySlider, self).__init__(w, h, x, y, sound_on=sound_on)
        self.is_dst = time.localtime().tm_isdst
        if self.is_dst:
            self.startstr = '10:30:00'
        else:
            self.startstr = '11:30:00'
        self.startsec_since_midnight = sec_since_midnight(self.startstr)
        self.hours2cross = 8.5
        self.sec_array = self.build_sec_array()
    
    def build_sec_array(self):
        arr = np.zeros(24*60*60)
        i1 = self.startsec_since_midnight
        sec2cross = self.hours2cross * 60 * 60
        i2 = i1 + sec2cross
        num_pts = i2 - i1
        arr[i1:i2] = np.linspace(0, self.screen_width-self.w, num_pts, endpoint=True )
        return np.rint(arr)
        
    def time2xpos(self, timestr):
        idx = sec_since_midnight(timestr)
        return self.sec_array[idx]

def quick_test():
    w, h = 350, 100
    x, y = 0, 450
    tgi = TkGeometrySlider(w, h, x, y, sound_on=True)
    root = tgi.root
    print sec_since_midnight(hms='23:59:59')
    
if __name__ == "__main__":
    quick_test()