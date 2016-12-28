#!/usr/bin/env python

import ConfigParser


def load_config(ini_file):
    config = ConfigParser.ConfigParser()
    config.read(ini_file)
    return config


def show_config(config):
    # Set the third, optional argument of get to 1 if you wish to use raw mode.
    print config.get('ancillary', 'expression', 1)  # -> "%(bar)s is %(baz)s!" NO INTERPOLATION
    print config.get('sensors', 'sensor_1', 0)  # -> "Python is fun!"
    print config.get('path', 'url', 0) # -> WITH INTERPOLATION
    
    # The optional fourth argument is a dict with members that will take
    # precedence in interpolation.
    print config.get('ancillary', 'expression', 0, {'bar': 'Documentation',
                                                    'baz': 'evil'})
    print config.get('ancillary', 'expression', 0, {'bar': 'Documentation'})
    

if __name__ == '__main__':
    ini_file = '/Users/ken/dev/programs/python/pims/gutwrench/gutwrench.ini'
    config = load_config(ini_file)
    show_config(config)
    