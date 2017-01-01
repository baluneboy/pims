#!/usr/bin/env python

"""Class containers for pages, which come from PageMapSection of '.run' config file."""

"""
For dynamic class assignment, see:
http://code.activestate.com/recipes/285262-create-objects-from-variable-class-names/
and esp. comment by Hamish Lawson:

You can specify the class directly rather than by name. Python classes can be
passed around, so you can refer them to directly rather than by name:

def get_object(cond):
    if cond:
        cls = A
    else:
        cls = B
    return cls()
    
If you need a multiway decision you can use a dictionary that has the candidate
classes as its values.
"""

import sys, inspect
from dateutil.parser import parse
from pims.gutwrench.base import TargetPage


# FIXME can we make this a abstract base class using ABC metaclass pattern (in base.py)?
class RoadmapWholeDayPage(object):
    
    def __init__(self, config_handler, page_fullstr):
        self.config_handler = config_handler
        self.page_fullstr = page_fullstr
        self.config = self.config_handler.config
        _split = page_fullstr.split('_')
        self._num =   _split[0] # use setter/getter because it comes in as like "page01"
        self.name =   _split[1]
        self._day =   _split[2] # use setter/getter because it comes in as string like "2016-12-30"
        self.sensor = _split[3]

    @property
    def page_fullstr(self):
        return self._page_fullstr

    @page_fullstr.setter
    def page_fullstr(self, fullstr):
        self._page_fullstr = fullstr
        
    @property
    def num(self):
        """page number property (getter)"""
        numstr = self._num.replace('page', '')
        return int(numstr)

    @num.setter
    def num(self, value):
        self._num = 'page%02d' % int(value)
        
    @property
    def day(self):
        """page day property (getter)"""
        return parse(self._day).date()

    @day.setter
    def day(self, value):
        if isinstance(value, str):
            # FIXME with regexp match/check (expecting fmt like '2016-12-30')
            self._day = value
        else:
            self._day = value.strftime('%Y-%m-%d')

    def __str__(self):
        s = "page #%02d for day %s with sensor %s (%s)" % (self.num, self.day, self.sensor, self.__class__.__name__)
        return s

    def build(self):
        print 'building %s' % self


class RoadmapAxisWholeDayPage(TargetPage):
    
    def get_page_dict(self):
        d = dict()
        # split str that comes in like 'page01_RoadmapWholeDayPage_2016-12-20_121f02'
        _split = self.page_fullstr.split('_')
        d['_num'] =   _split[0] # use setter/getter because it comes in as like "page01"
        d['name'] =   _split[1]
        d['_day'] =   _split[2] # use setter/getter because it comes in as string like "2016-12-30"
        d['sensor'] = _split[3]
        return d
    
    #def __str__(self):
    #    d = self.page_dict
    #    #s = "page #%02d for day %s with sensor %s (%s)" % (d['_num'], d['day'], d['sensor'], self.__class__.__name__)
    #    s = "page #%s for day %s with sensor %s (%s)" % (d['_num'], d['_day'], d['sensor'], self.__class__.__name__)
    #    return s


def get_page_classes():
    # get page class members in this module (this file)
    return inspect.getmembers(sys.modules[__name__], inspect.isclass)


# try to create a page object (from one of classes in this module) based on PageMapSection page camel-case name
def get_page(config_handler, page_fullstr):
    """try to create a page object (from one of classes in this module) based on PageMapSection page camel-case name"""
    
    try:
        page_str = page_fullstr.split('_')[1]
        config = config_handler.config
        page_classes = get_page_classes()
        # get page from class members in this module (this file)
        page_class = [t[1] for t in page_classes if t[0] == page_str]
        if len(page_class) == 0:
            raise Exception('No page match for %s' % page_str)
        elif len(page_class) != 1:
            raise Exception('More than one (non-unique) match for page class [somehow?].')
        else:
            page_class = page_class[0]
            page_obj = page_class(config_handler, page_fullstr)
    except Exception, e:
        print "registered classes =", page_classes
        print 'Using config from %s' % config_handler.cfg_file
        print "Could not get page object for %s." % page_str
        raise e
    
    # if match found, return page class; otherwise, return None
    return page_obj


# set variable that gives all classes via "from pims.gutwrench.sections import *"
__all__ = [t[0] for t in get_page_classes()]
__all__.append('get_page')


def demo_sect():
    from pims.gutwrench.config import PimsConfigHandler
    from pims.gutwrench.targets import get_target

    # get config handler based on cfg_file
    cfgh = PimsConfigHandler('/Users/ken/temp/gutone', cfg_file='gutwrench.run')
    
    # load config from config file
    cfgh.load_config()
        
    # get target based on output page of config file using target parameter there
    print 'processing %s' % cfgh.cfg_file
    target = get_target(cfgh)
    print target
    
    target.main_process()


if __name__ == '__main__':
    demo_sect()
