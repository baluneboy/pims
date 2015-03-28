#!/usr/bin/env python
version = '$Id$'

import os
import sys
import time
import samsd

# input parameters
defaults = {
             'output_dir': '/data/samscheck', # output path
             'summary':  [],                  # list summary
             'details':  [],                  # list details
             'config_file': '/home/pims/dev/programs/python/config/mysql.cfg', # config file for queries
             'refresh_minutes': '1',          # how often to refresh
}
parameters = defaults.copy()

def parametersOK():
    """check for reasonableness of parameters"""
    if not os.path.exists(parameters['output_dir']):
        print 'output_dir (%s) does not exist' % parameters['output_dir']
        return False

    if os.path.isfile(parameters['config_file']):
        validator_file = parameters['config_file'].replace('.cfg', '.ini')
    else:
        print 'The config_file "%s" does not exist.' % config_file
        return False

    if os.path.isfile(validator_file):
        parameters['validator_file'] = validator_file
    else:
        print 'The validator_file "%s" does not exist.' % validator_file
        return False

    try:
        parameters['refresh_minutes'] = int(parameters['refresh_minutes'])
    except ValueError as e:
        print 'Expected an integer for refresh_minutes.'
        return False

    return True # all OK, returned False (above) otherwise

class SamsQueryObject():
    
    def __init__(self):
        if parametersOK():
            self.sams_monitor = samsd.SamsMonitor()
            self.config_file = parameters['config_file']
            self.validator_file = parameters['validator_file']
            self.refresh_minutes = parameters['refresh_minutes']
            self.host, self.schema, self.uname, self.pword, self.query_list = samsd.get_config(self.config_file, self.validator_file)
        else:
            print 'something wrong with input parameter(s)'
            sys.exit(-1)
    
def demo_twice(sams_obj):
    print 'Doing demo_twice, first one...'
    samsd.process_config_file(sams_obj.sams_monitor, sams_obj)
    print 'Sleep for 60s...'
    time.sleep(60.0*parameters['refresh_minutes'])
    print 'Second one...'
    samsd.process_config_file(sams_obj.sams_monitor, sams_obj)
    print 'did it twice, so done with test.'
    sys.exit(0)    

if __name__ == '__main__':
    sams_obj = SamsQueryObject()
    demo_twice(sams_obj)
