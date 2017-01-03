#!/usr/bin/env python

import abc
from collections import OrderedDict


# An abstract base class for a config file section.
class ConfigSection(object):
    """An abstract base class for a config file section."""

    __metaclass__ = abc.ABCMeta
    
    def __init__(self, config_handler):
        """Initialize object with a config handler object."""
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

    @abc.abstractmethod    
    def get_required_param_names(self):
        """Return list of parameter names that must be in this section."""
        # Ted Wright did not use abc, and just raised exception like the one below
        #raise NotImplementedError('it is responsibility of subclass to return list of required parameter names')

        # use abstractmethod decorator to demand subclass overrides this method; meanwhile, so just return [None]
        return
        
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


class TargetPage(object):
    
    __metaclass__ = abc.ABCMeta   
    
    def __init__(self, config_handler, page_fullstr):
        self.config_handler = config_handler
        self.page_fullstr = page_fullstr
        self.config = self.config_handler.config
        self.page_dict = self.get_page_dict()

    #FIXME how about abstract TargetPageDict class to wrangle things like orientation, relative/absolute page num
    
    @abc.abstractmethod
    def get_page_dict(self):
        """Return page dict from [split?] str that comes in like 'page01_RoadmapWholeDayPage_2016-12-20_121f02'"""
        return

    #@property
    #def num(self):
    #    """page number property (getter)"""
    #    numstr = self._num.replace('page', '')
    #    return int(numstr)
    #
    #@num.setter
    #def num(self, value):
    #    self._num = 'page%02d' % int(value)
    #    
    #@property
    #def day(self):
    #    """page day property (getter)"""
    #    return parse(self._day).date()
    #
    #@day.setter
    #def day(self, value):
    #    if isinstance(value, str):
    #        # FIXME with regexp match/check (expecting fmt like '2016-12-30')
    #        self._day = value
    #    else:
    #        self._day = value.strftime('%Y-%m-%d')

    def __str__(self):
        d = self.page_dict
        #s = "page #%02d for day %s with sensor %s (%s)" % (d['_num'], d['day'], d['sensor'], self.__class__.__name__)
        s = "page #%s for day %s with sensor %s (%s)" % (d['_num'], d['_day'], d['sensor'], self.__class__.__name__)
        return s

    def build(self):
        print 'building %s' % self
     