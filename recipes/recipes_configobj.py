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

def process_config(config_file, validator_file):
    gc = GeneralConfig(config_file, validator_file)
    config = gc.config
    # got here valid, so work each section (that is, each "feed" in this example)
    feeds = config['feeds']
    num_stories_each_feed = feeds['num_stories_each_feed']
    del feeds['num_stories_each_feed']
    for fn, dfeed in feeds.items():
        feed_name = fn.replace('_',' ')
        if dfeed['active']:
            voice = dfeed['voice']
            feed_url = dfeed['url']
            print 'Do something with "%s" using %s voice and URL = %s' % (feed_name, voice, feed_url)
        else:
            print 'The "active" flag in config file was False, so skip the feed we call "%s".' % feed_name

def main():
    config_file = 'config_example.cfg'
    validator_file = 'config_example.ini'
    process_config(config_file, validator_file)
    return 0

if __name__ == '__main__':
    sys.exit(main())