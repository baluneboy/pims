#!/usr/bin/env python

import os
import re
from pims.patterns.dailyproducts import _SENSOR_SUBDIR_PATTERN

class SensorSubdir(object):
    
    """PAD sensor subdir (e.g. sams2_accel_121f03006)

    Returns SensorSubdir object

    >>> a = '/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f03006'
    >>> s = SensorSubdir(a)
    >>> s
    ('sams2', 'accel', '121f03006', '006')
    """
    
    def __init__(self, fullpath):
        self.fullpath = fullpath
        self.basename = os.path.basename(self.fullpath)
        system, category, sensor = self.basename.split('_')
        self.system = system
        self.category = category
        self.sensor = sensor
        self.suffix = self.get_suffix()
        
    def __repr__(self):
        return repr( (self.system, self.category, self.sensor, self.suffix) )
    
    def get_suffix(self):
        if self.sensor.endswith('006'):
            return '006'
        else:
            return ''
    
def demo_sort_by(attr):
    a = '/misc/yoda/pub/pad/year2013/month01/day02/abcd_cpt_121f05006'
    b = '/misc/yoda/pub/pad/year2013/month01/day02/bxf_accel_121f03'
    c = '/misc/yoda/pub/pad/year2013/month01/day02/cAr_bike_121f03006'
    d = '/misc/yoda/pub/pad/year2013/month01/day02/abcd_cpt_121f05'    
    subdirs = [ SensorSubdir(i) for i in [a, b, c, d] ]
    for sd in sorted(subdirs, key=lambda sd: getattr(sd, attr)):
        print sd

attr = 'sensor'; demo_sort_by(attr); raise SystemExit
    
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    