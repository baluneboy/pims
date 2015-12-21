#!/usr/bin/python

import sys
import time
import datetime

#import pywemo
from enum import Enum

class WemoState(Enum):
    UNKNOWN = -1
    OFF     =  0
    ON      =  1


# FIXME init needs to do wrangling so we can easily/robustly address "the light"
# or "the sweat" WITH up to say one minute for device discovery that yields the
# device we want -- this allows for one-minute advance notice in cronjob
#
# a simple wemo control
class SimpleWemoControl(object):
    """a simple wemo control that has following properties:

    Attributes:
        name: A string representing the device's name (e.g. "the light")
        state: An integer representing the device's state (e.g. 0 = OFF, 1 = ON, -1 = UNKNOWN)
        
    Methods:
        turn_on: Turn on this device.
        turn_off: Turn off this device.
        toggle: Toggle this device.
    """

    # return a SimpleWemoControl object based on name 
    def __init__(self, name, retry_seconds):
        """return a SimpleWemoControl object based on name"""
        self.name = name
        self.retry_seconds = retry_seconds
        self.state = WemoState.UNKNOWN # enum: OFF, ON, or UNKNOWN

    # FIXME this needs better getter/setter foundation
    # return device state
    def get_state(self):
        """return the state"""
        return self.state
