#!/usr/bin/env python

"""Class containers for config file sections."""

from dateutil.parser import parse as dtmparse


class HeadingsSection(object):
    
    def __init__(self, config_handler):
        self.config_handler = config_handler
        self.config = self.config_handler.config

    def __str__(self):
        s = "This is a %s instance." % self.__class__.__name__
        return s


class GmtSpanSection(object):
    
    def __init__(self, config_handler):
        self.config_handler = config_handler
        self.config = self.config_handler.config
        self.gmt_start = dtmparse(self.config.get('gmtspan', 'gmtstart'))
        self.gmt_stop =  dtmparse(self.config.get('gmtspan', 'gmtstop'))     

    def __str__(self):
        s =  "GMT span "
        s += "from %s " % self.gmt_start 
        s += "to %s"   % self.gmt_stop 
        return s
    