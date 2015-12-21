#!/usr/bin/python

import sys
import time
import datetime

#import pywemo
from enum import Enum

class WemoState(Enum):
    OFF     = 0
    ON      = 1
    UNKNOWN = 2

# a simple wemo control
class SimpleWemoControl(object):
    """a simple wemo control that has following properties:

    Attributes:
        name: A string representing the device's name (e.g. "the light")
        state: An integer representing the device's state (e.g. 0 = off, 1 = on, 2 = unknown)
        
    Methods:
        turn_on: Turn on this device.
        turn_off: Turn off this device.
        toggle: Toggle this device.
    """

    # return a SimpleWemoControl object based on name 
    def __init__(self, name):
        """return a SimpleWemoControl object based on name"""
        self.name = name
        self.state = WemoState.UNKNOWN # enum: OFF, ON, or UNKNOWN

    # return device state
    def get_state(self):
        """return the state"""
        if amount > self.state:
            raise RuntimeError('Amount greater than available state.')
        self.state -= amount
        return self.state
