#!/usr/bin/env python

"""Get and handle configuration, usually from gutwrench.ini (or .run) file."""

import os
import sys
import ConfigParser
from dateutil.parser import parse
from filesystem_tree import FilesystemTree
import warnings


#################################################################
# Any config file suffix (types) should be added to globals here:
#          SUFFIX     CALLABLE
#-----------------------------
globals()['float'] =  float
globals()['dtm']   =  parse
#################################################################

def show_config(config):
    config.write(sys.stdout)
    # Set the third, optional argument of get to 1 if you wish to use raw mode.
    print config.get('ancillary', 'expression', 1)  # -> "%(bar)s is %(baz)s!" NO INTERPOLATION
    print config.get('sensors', 'sensor_1', 0)  # -> "Python is fun!"
    print config.get('resources', 'URL', 0) # -> WITH INTERPOLATION
    
    # The optional fourth argument is a dict with members that will take
    # precedence in interpolation.
    print config.get('ancillary', 'expression', 0, {'bar': 'Documentation',
                                                    'baz': 'evil'})
    print config.get('ancillary', 'expression', 0, {'bar': 'Documentation'})


class PimsConfigParser(ConfigParser.SafeConfigParser):
    
    def get_formatted_option(self, section, option):
        
        # check for special option (parameter) with underscored suffix
        if '_' in option:
            func_str = option.split('_')[-1]
        else:
            # assuming the value is of type str here
            return self.get(section, option)
            
        # if possible, format this option using suffix as func_str for func method to call on it
        try:
            func = globals()[func_str] # or should this be locals() instead of globals()?
            value = self._get(section, func, option)
        except Exception, e:
            print 'an exception happened trying %s(%s)' % (func_str, option)
            print 'so fall back to just using str to format parameter in config'
            value = self.get(section, option)
        
        return value       


class SafeFilesystemTree(FilesystemTree):
    
    def remove(self):
        msg = 'we will not remove the filesystem tree at root = %s' % self.root
        warnings.warn(msg)


class ConfigHandler(object):
    
    def __init__(self, base_path='/tmp', cfg_file='gutwrench.ini'):
        self.base_path = base_path
        self.set_cfg_file(cfg_file)
        self.ext = self.get_ext()
        self.file_tree = self.get_file_tree()
        self.files = self.get_files()
        self.config = PimsConfigParser()
        
    @property
    def base_path(self):
        return self._base_path

    @base_path.setter
    def base_path(self, some_path):
        if not os.path.exists(some_path):
            raise IOError("base_path (%s) does not exist" % some_path)        
        self._base_path = some_path
        
    def get_file_tree(self):
        return SafeFilesystemTree(root=self.base_path)

    def get_files(self):
        ft = self.get_file_tree()
        return os.listdir(ft.root)

    def get_ext(self):
        return self.cfg_file.split('.')[-1]

    def set_cfg_file(self, cfg_file):
        ft = self.get_file_tree()
        files = self.get_files()
        if not cfg_file in files:
        #   print('the ini file (%s) does not exist -> create one' % cfg_file)
        #   self.create_cfg_file(ft, cfg_file)
            raise Exception('the config file (%s) does not exist' % cfg_file)
        self.cfg_file = ft.resolve(cfg_file)

    def load_config(self):
        self.config.read(self.cfg_file)
        
    def create_cfg_file(self, ft, cfg_file):
        ft.mk((cfg_file, '''
        # auto-generated configuration file
        
        # NOTE: this is where you can create default file as needed
        #
        # NOTE: if param name has underscore suffix that matches globals
        #       in ~/dev/programs/python/pims/gutwrench/config.py, then
        #       those parameter values will be cast to that type; other-
        #       wise they fallback to strings
        
        [HeadingSection]
        t1_dtm   = 2016-12-20 16:00
        x2_float = 17.23
        
        [ResourceSection]
        host = jimmy
        port = 1234
        # NOTE YOU CAN DO SUBSTITUTION LIKE THIS POORLY FORMATTED URL
        url = http://%(host)s:%(port)s/
        '''))


class PimsConfigHandler(ConfigHandler):

    def set_cfg_file(self, cfg_file):
        """handle pims config files with extension: {ini|run}"""
        
        _ok_exts = ['ini', 'run']
        
        # FIXME make ext a property (robust setter/getter that matches init sequence)
        
        # get extension and check it
        if not cfg_file.split('.')[-1] in _ok_exts:
            okstr = ','.join(_ok_exts)
            raise Exception('%s ONLY HANDLES CONFIG FILES ENDING WITH ONE OF THESE: %s' % (self.__class__.__name__, okstr))
        
        # FIXME the base class can properly handle this whole file tree business better
        ft = self.get_file_tree() # use method (not property), so we "refresh" tree
        files = self.get_files()
        if not cfg_file in files:
            raise Exception('the config file (%s) does not exist' % cfg_file)
        
        # resolve full path
        cfg_file = ft.resolve(cfg_file)
        
        # verify we will not clobber ".run" when ".ini" is set as cfg_file
        self.verify_no_clobber(cfg_file)
        
        # finally, set cfg_file attribute
        self.cfg_file = cfg_file
    
    def verify_no_clobber(self, cfg_file):
        ext = cfg_file.split('.')[-1]
        # if cfg_file endswith "ini", then check that ".run" file does NOT exist yet
        if ext == 'ini':
            run_fname = cfg_file.replace('.ini', '.run')
            if os.path.basename(run_fname) in self.get_files():
                raise Exception('running ini, but run file exists already %s (NO CLOBBER)' % run_fname)
    
    def create_cfg_file(self, ft, cfg_file):
        ft.mk((cfg_file, '''
        # auto-generated gutwrench.ini
        
        # NOTE: if param name has underscore suffix that matches globals
        #       in ~/dev/programs/python/pims/gutwrench/config.py, then
        #       those parameter values will be cast to that type; other-
        #       wise they fallback to strings
        
        [HeadingSection]
        source   = An Interesting Experiment
        regime   = vibratory
        category = equipment
        t1_dtm   = 2016-12-20 16:00
        x2_float = 17.23
        
        [OutputSection]
        target = RoadmapCanvasTarget
        topdir = /misc/yoda/www/plots/user/handbook/source_docs
        
        [GmtSpanSection]
        # NOTE: gmtstart_dtm <= t < gmtstop_dtm (closed lower bound, open upper)
        gmtstart_dtm = 2016-12-20 00:00
        gmtstop_dtm  = 2016-12-22 00:00
        
        [SensorSection]
        sensor01 = 121f02
        sensor02 = 121f03
        sensor03 = 121f05
        sensor04 = 121f08
        
        [AncillarySection]
        lastmodified_dtm = 2016-12-27 13:26
        expression = %(bar)s is %(baz)s!
        baz = yummy
        
        [ResourceSection]
        host = jimmy
        port = 1234
        # NOTE YOU CAN DO SUBSTITUTION LIKE THIS POORLY FORMATTED URL
        url = http://%(host)s:%(port)s/
        '''))
