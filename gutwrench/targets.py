#!/usr/bin/env python

"""Target classes based on config > output section > target parameter."""

import sys
from collections import OrderedDict
from dateutil import relativedelta
from dateutil.parser import parse as dtmparse
from pims.gutwrench.sections import *

class RoadmapCanvasTarget(object):
    
    def __init__(self, config_handler):
        self.config_handler = config_handler
        self.config = self.config_handler.config
        self.all_section_names = self.get_all_section_names()
        self.required_section_names = self.get_required_section_names()
        self.verify_required_sections()
        self.required_sections = self.get_required_sections()
        self.run_file = None

    def __str__(self):
        s = "target is %s" % self.__class__.__name__
        return s
    
    def get_required_section_names(self):
        return ['HeadingSection', 'GmtSpanSection', 'SensorSection']
        
    def verify_required_sections(self):        
        is_subset = set(self.required_section_names).issubset(set(self.all_section_names))
        if not is_subset:
            print 'your config file is missing at least one of these required section(s):',
            print self.required_section_names
            raise Exception('missing required configuration section(s)')
    
    def get_all_section_names(self):
        # these came from entire config file
        return self.config.sections()
        
    def get_required_sections(self):
        required_sections = OrderedDict()
        for sect_name in self.required_section_names:
            required_sections[sect_name] = get_section(self.config_handler, sect_name)
        return required_sections

    def show_required_sections(self):
        print 'showing required sections:\n' + '-' * 36
        for name, sect in self.required_sections.iteritems():
            print name
            print sect        
    
    def pre_process(self):
        print 'pre-processing for %s\n' % self.__class__.__name__
        
        #self.show_required_sections()
        
        if 'PageMapSection' in self.all_section_names:
            raise Exception('PageMapSection of config exists already: %s' % self.config_handler.ini_file)
            
        else:
            print 'create and fill PageMapSection of config and rewrite file\n'
            
            # get outer (GMT Day) loop info
            day1 = self.required_sections['GmtSpanSection'].params_dict['gmtstart_dtm'].date()
            day2 = self.required_sections['GmtSpanSection'].params_dict['gmtstop_dtm'].date()
            delta = day2 - day1
            num_days = delta.days
            
            # FIXME how do we use sections.py for PageMapSection
            # FIXME this target class has to have an add section method too
            
            # add section that maps pages
            page_num = 1 # start of page numbering for this section
            new_sect_name = 'PageMapSection'
            self.config.add_section(new_sect_name)
            day = day1
            for d in range(0, num_days):
                daystr = day.strftime('%Y-%m-%d')
                for sensor_key, sensor in self.required_sections['SensorSection'].params_dict.iteritems():
                    new_param_name = 'page%02d' % page_num
                    new_param_value = 'RoadmapWholeDayPage_' + daystr + '_' + sensor
                    self.config.set(new_sect_name, new_param_name, new_param_value)
                    page_num += 1
                day += relativedelta.relativedelta(days = 1)
            
            # FIXME this should write to like gutwrench.run
            
            # write to screen
            #self.config.write(sys.stdout)
            
            # write to new "dot run" file
            run_fname = self.config_handler.ini_file.replace('.ini', '.run')
            with open(run_fname, 'wt') as f:
                self.config.write(f)
    
    def main_process(self):
        print 'main processing for %s\n' % self.__class__.__name__
    
    def post_process(self):
        print 'post-processing for %s\n' % self.__class__.__name__


# try to create a target object (from one of classes in this module) based on config output section's target parameter
def get_target(config_handler):
    """try to create a target object (from one of classes in this module) based on config output section's target parameter"""
    
    import sys, inspect
    
    # get output section's target parameter as a string
    try:
        config = config_handler.config        
        target_str = config.get('OutputSection', 'target')
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
