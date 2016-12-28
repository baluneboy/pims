#!/usr/bin/env python

"""Get and handle configuration, usually from gutwrench.ini file."""

import os
import sys
import ConfigParser
from filesystem_tree import FilesystemTree


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


class ConfigHandler(object):
    
    def __init__(self, base_path, ini_file='gutwrench.ini'):
        self.base_path = base_path
        self.set_ini_file(ini_file)
        self.file_tree = self.get_file_tree()
        self.files = self.get_files()
        self.config = ConfigParser.SafeConfigParser()
        
    @property
    def base_path(self):
        #print('Getting base_path')
        return self._base_path

    @base_path.setter
    def base_path(self, some_path):
        if not os.path.exists(some_path):
            raise IOError("base_path (%s) does not exist" % some_path)        
        #print('Setting base_path to %s' % some_path)
        self._base_path = some_path
        
    def get_file_tree(self):
        #print('get_file_tree')
        return FilesystemTree(root=self.base_path)

    def get_files(self):
        #print('get_files')
        ft = self.get_file_tree()
        return os.listdir(ft.root)

    def set_ini_file(self, ini_file):
        ft = self.get_file_tree()
        files = self.get_files()
        if not ini_file in files:
           print('the ini file (%s) does not exist -> create one' % ini_file)
           self.create_ini_file(ft, ini_file)
        self.ini_file = ft.resolve(ini_file)

    def load_config(self):
        self.config.read(self.ini_file)
    
    def OLDget_target_str(self):
        target_str = None
        try:
            target_str = self.config.get('output', 'target')
        except Exception, e:
            print 'an exception happened: %s' % e.message
        return target_str
    
    def create_ini_file(self, ft, ini_file):
        ft.mk((ini_file, '''
        # auto-generated gutwrench.ini
        
        [headings]
        source   = An Interesting Experiment
        regime   = vibratory
        category = equipment
        
        [output]
        target = roadmap_canvas
        topdir = /misc/yoda/www/plots/user/handbook/source_docs
        
        [gmtspan]
        gmtstart = 2016-12-20 16:00
        gmtstop  = 2016-12-25
        
        [sensors]
        sensor_1 = 121f02
        sensor_2 = 121f03
        sensor_3 = 121f05
        sensor_4 = 121f08
        
        [ancillary]
        ini_last_modified = 2016-12-27 13:26
        expression = %(bar)s is %(baz)s!
        baz = yummy
        
        [resources]
        host = jimmy
        port = 8080
        # NOTE YOU CAN DO SUBSTITUTION LIKE THIS POORLY FORMATTED URL
        url = http://%(host)s:%(port)s/
        '''))
