#!/usr/bin/python

import sys
import time
import datetime

#import pywemo
from enum import Enum

from pims.lib.autogetset import getter_setter_gen, auto_attr_check

# class to workaround no built-in enum type
class WemoState(Enum):
    """class to workaround no built-in enum type"""
    UNKNOWN = -1
    OFF     =  0
    ON      =  1


# FIXME init needs to do wrangling so we can easily/robustly address "the light"
# or "the sweat" WITH up to say one minute for device discovery that yields the
# device we want; we want to allow for one-minute advance notice in cronjob
#
# a robust wemo control
@auto_attr_check
class RobustWemoControl(object):
    """a robust wemo control, which has the following properties:

    Attributes:
        name: A string representing the device's name (e.g. "the light", or "the sweat").
        retry: An integer representing the number of seconds to retry when getting expected device by name.
        state: An Enum representing the device's state: WemoState.OFF, WemoState.ON, or WemoState.UNKNOWN.
        
    Methods:
        turn_on: Turn on this device.
        turn_off: Turn off this device.
        toggle: Toggle this device.
    """
    
    # these attributes are automatically type-checked 
    name = str
    retry = int

    # return a RobustWemoControl object based on name 
    def __init__(self, name, retry=3):
        """return a RobustWemoControl object based on name"""
        self.name = name
        self.retry = retry
        self.state = None # can be: None, WemoState.OFF, .ON, or .UNKNOWN
    
    # return a string representing this object 
    def __str__(self):
        """return a string to represent this RobustWemoControl object"""
        s = '%s named "%s" (retry = %ds)' % (self.__class__.__name__, self.name, self.retry)
        if self.state:
            s += ' has %s' % self.state
        else:
            s += ' has not been discovered yet'        
        return s
    
    
if __name__ == "__main__":
    rwc = RobustWemoControl('the light')
    #rwc.state = WemoState.ON
    print rwc
