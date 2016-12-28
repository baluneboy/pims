#!/usr/bin/env python

"""Target classes based on config > output section > target parameter."""

import sys
from dateutil.parser import parse as dtmparse
from pims.gutwrench.sections import HeadingsSection, GmtSpanSection


class RoadmapCanvas(object):
    
    def __init__(self, config_handler):
        self.config_handler = config_handler
        self.config = self.config_handler.config

    def __str__(self):
        s = "This is a %s instance." % self.__class__.__name__
        return s
    
    def pre_process(self):
        print 'do %s pre-processing' % self.__class__.__name__
        
        # get headings section
        head_sect = HeadingsSection(self.config_handler)
        print head_sect
        
        # get gmt span section
        gmt_sect = GmtSpanSection(self.config_handler)
        print gmt_sect
        
        #self.config.write(sys.stdout)
    
    def main_process(self):
        print 'do %s main processing' % self.__class__.__name__
    
    def post_process(self):
        print 'do %s post-processing' % self.__class__.__name__        


# try to create a target object (from one of classes in this module) based on config output section's target parameter
def get_target(config_handler):
    """try to create a target object (from one of classes in this module) based on config output section's target parameter"""
    
    import sys, inspect
    
    # get output section's target parameter as a string
    try:
        config = config_handler.config        
        target_str = config.get('output', 'target')
        # get target from class members in this module (this file)
        class_members = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        target_class = [t[1] for t in class_members if t[0] == target_str]
        if len(target_class) == 0:
            raise Exception('No target match for target_str = %s' % target_str)
        elif len(target_class) != 1:
            raise Exception('More than one (non-unique) match for target class [somehow].')
        else:
            target_class = target_class[0]
            target_obj = target_class(config_handler)
    except Exception, e:
        print 'Using config from %s' % config_handler.ini_file
        print "Could not get target object from config output section's target parameter."
        raise e
    
    # if match found, return target class; otherwise, return None
    return target_obj
