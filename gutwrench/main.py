#!/usr/bin/env python

import os
import sys
from pims.lib.niceresult import NiceResult
from pims.gutwrench.config import ConfigHandler
from pims.gutwrench.targets import get_target

# input parameters
defaults = {
'base_path':    '/Users/ken/temp/gutone',   # path of interest
'ini_file':     'gutwrench.ini',            # ini (config) file
}
parameters = defaults.copy()


# check for reasonableness of parameters
def parameters_ok():
    """check for reasonableness of parameters"""    

    if not os.path.exists(parameters['base_path']):
        print 'base path (%s) does not exist' % parameters['base_path']
        return False
    
    return True # all OK; otherwise, return False somewhere above


# print helpful text how to run the program
def print_usage():
    """print helpful text how to run the program"""
    #FIXME with git keyword sub via following:
    # http://stackoverflow.com/questions/11534655/git-keyword-substitution-like-those-in-subversion
    #print version << BETTER GO AT THIS???
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

    
# process data with parameters here (after we checked them earlier)
def process_data(params):
    """process data with parameters here (after we checked them earlier)"""
       
    # get config handler based on ini file
    cfgh = ConfigHandler(parameters['base_path'], ini_file=parameters['ini_file'])
    
    # load config from config (ini) file
    cfgh.load_config()
        
    # get target based on output section of config (ini) file using target parameter there
    print 'processing %s' % cfgh.ini_file
    target = get_target(cfgh)
    if target:
        print 'got target = %s' % target.__class__.__name__

        # do target pre-processing
        target.pre_process()
        
        # do target main processing
        target.main_process()
        
        # do target post-processing
        target.post_process()


# describe main routine here
def main(argv):
    """describe main routine here"""
    
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parameters_ok():
            nr = NiceResult(process_data, parameters)
            nr.do_work()
            result = nr.get_result()
            return 0 # zero for unix success
        
    print_usage()  

# run main with cmd line args and return exit code
if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))