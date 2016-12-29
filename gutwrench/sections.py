#!/usr/bin/env python

"""Class containers for config file sections."""

import sys, inspect
from collections import OrderedDict

# FIXME make this a robust abstract base class using ABC metaclass pattern
class ConfigSection(object):
    
    def __init__(self, config_handler):
        self.config_handler = config_handler
        self.config = self.config_handler.config
        self.all_param_names = self.get_all_param_names()
        self.required_param_names = self.get_required_param_names()
        self.verify_required_params()
        self.params_dict = self.get_params()

    def __str__(self):
        #s = "%s\n" % self.__class__.__name__
        s = ""
        for k, v in self.params_dict.iteritems():
            s += "%s: %s\n" % (k, v)
        return s
    
    def get_required_param_names(self):
        raise NotImplementedError('it is responsibility of subclass to return list of required parameter names')
        
    def verify_required_params(self):
        
        is_subset = set(self.required_param_names).issubset(set(self.all_param_names))
        if not is_subset:
            print 'your %s is missing at least one of these required parameter(s):' % self.__class__.__name__,
            print self.required_param_names
            raise Exception('missing required configuration parameter(s)')
    
    def get_all_param_names(self):
        return self.config.options(self.__class__.__name__)
    
    def get_params(self):
        params_dict = OrderedDict()
        section = self.__class__.__name__
        for name, value in self.config.items(section):
            params_dict[name] = self.config.get_formatted_option(section, name)
        return params_dict


class HeadingSection(ConfigSection):
    
    def get_required_param_names(self):
        return ['source', 'regime', 'category']

    
class GmtSpanSection(ConfigSection):
    
    def get_required_param_names(self):
        return ['gmtstart_dtm', 'gmtstop_dtm']

class SensorSection(ConfigSection):
    
    def get_required_param_names(self):
        return []

class PageMapSection(ConfigSection):
    
    def get_required_param_names(self):
        return []

# get section class members in this module (this file)
section_classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)


# try to create a section object (from one of classes in this module) based on config output section camel-case name
def get_section(config_handler, section_str):
    """try to create a section object (from one of classes in this module) based on config output section camel-case name"""
        
    try:
        config = config_handler.config        
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
        print 'Using config from %s' % config_handler.ini_file
        print "Could not get section object for %s." % section_str
        raise e
    
    # if match found, return section class; otherwise, return None
    return section_obj


# set variable that gives all classes via "from pims.gutwrench.sections import *"
__all__ = [t[0] for t in section_classes]
__all__.append('get_section')


def demo_sect():
    from pims.gutwrench.config import ConfigHandler
    from pims.gutwrench.targets import get_target

    # get config handler based on ini file
    cfgh = ConfigHandler('/Users/ken/temp/gutone', ini_file='gutwrench.ini')
    
    # load config from config (ini) file
    cfgh.load_config()
        
    # get target based on output section of config (ini) file using target parameter there
    print 'processing %s' % cfgh.ini_file
    target = get_target(cfgh)
    print target
    
    target.pre_process()



if __name__ == '__main__':
    demo_sect()