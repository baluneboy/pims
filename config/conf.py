#!/usr/bin/env python

import os
import sys
from configobj import ConfigObj, flatten_errors
from validate import Validator

class ConfigError(AttributeError): pass

class GeneralConfig(object):
    
    def __init__(self, config_file, validator_file):
        self.config_file = config_file
        self.validator_file = validator_file
        self.config = self.verify_files()
        
    def verify_files(self):
        if not os.path.isfile(self.config_file):
            raise IOError('The config_file "%s" is not a file.' % self.config_file)
        if not os.path.isfile(self.validator_file):
            raise IOError('The validator_file "%s" is not a file.' % self.validator_file)
            
        config = ConfigObj( self.config_file, configspec=self.validator_file )
        validator = Validator()
        results = config.validate(validator)
        if results != True:
            for (section_list, key, _) in flatten_errors(config, results):
                if key is not None:
                    raise ConfigError( 'The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list)) )
                else:
                    raise ConfigError( 'The following section was missing:%s ' % ', '.join(section_list) )
        return config

def get_config(config_file='/home/pims/dev/programs/python/config/mysql.cfg'):
    validator_file = config_file.replace('.cfg', '.ini')
    gc = GeneralConfig(config_file, validator_file)
    config = gc.config
    return config

def get_db_params(app_name):
    cfg = get_config()
    config_dict = cfg['apps'][app_name]
    schema = config_dict['schema']
    uname = config_dict['uname']
    pword = config_dict['pword']
    return schema, uname, pword

def demo(app_name):
    _SCHEMA, _UNAME, _PASSWD = get_db_params(app_name)
    print _SCHEMA, _UNAME, _PASSWD
    
if __name__ == "__main__":
    demo('pimsquery')
    #demo('packetgrouper')