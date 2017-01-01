#!/usr/bin/env python

"""Class containers for config file sections."""

import sys, inspect
from collections import OrderedDict
from pims.gutwrench.base import ConfigSection
   
    
class HeadingSection(ConfigSection):
    
    def get_required_param_names(self):
        return ['source', 'regime', 'category']

    
class OutputSection(ConfigSection):
    
    def get_required_param_names(self):
        return ['target', 'topdir']

    
class GmtSpanSection(ConfigSection):
    
    def get_required_param_names(self):
        return ['gmtstart_dtm', 'gmtstop_dtm']


class SensorSection(ConfigSection):
    
    def get_required_param_names(self):
        return []


class PageMapSection(ConfigSection):
    
    def get_required_param_names(self):
        return []


def get_section_classes():
    # get section class members in this module (this file)
    return inspect.getmembers(sys.modules[__name__], inspect.isclass)


# try to create a section object (from one of classes in this module) based on config output section camel-case name
def get_section(config_handler, section_str):
    """try to create a section object (from one of classes in this module) based on config output section camel-case name"""
        
    try:
        config = config_handler.config
        section_classes = get_section_classes()
        # get section from class members in this module (this file)
        section_class = [t[1] for t in section_classes if t[0] == section_str]
        if len(section_class) == 0:
            raise Exception('No section match for _str = %s' % section_str)
        elif len(section_class) != 1:
            raise Exception('More than one (non-unique) match for section class [somehow].')
        else:
            section_class = section_class[0]
            section_obj = section_class(config_handler)
    except Exception, e:
        print "registered classes =", section_classes
        print 'Using config from %s' % config_handler.cfg_file
        print "Could not get section object for %s." % section_str
        raise e
    
    # if match found, return section class; otherwise, return None
    return section_obj


# set variable that gives all classes via "from pims.gutwrench.sections import *"
__all__ = [t[0] for t in get_section_classes()]
__all__.append('get_section')


def demo_sect():
    from pims.gutwrench.config import PimsConfigHandler
    from pims.gutwrench.targets import get_target

    # get config handler based on cfg_file
    cfgh = PimsConfigHandler(base_path='/Users/ken/temp/gutone', cfg_file='gutwrench.ini')
    
    # load config from config file
    cfgh.load_config()
        
    # get target based on output section of config file using target parameter there
    print 'processing %s' % cfgh.cfg_file
    target = get_target(cfgh)
    print target
    
    target.pre_process()

def demo_dynamic_instance():
    from pims.gutwrench.pages import RoadmapAxisWholeDayPage
    import importlib
    my_module = importlib.import_module("pims.gutwrench.config")
    MyClass = getattr(my_module, "PimsConfigHandler")
    instance = MyClass(base_path='/Users/ken/temp/gutone', cfg_file='gutwrench.ini')
    print instance.base_path, instance.cfg_file
    
    config_handler = instance
    rawdp = RoadmapAxisWholeDayPage(config_handler, 'one_two_three_four')
    print rawdp

if __name__ == '__main__':
    #demo_sect()
    demo_dynamic_instance()
