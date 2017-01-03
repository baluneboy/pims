#!/usr/bin/env python

import os
import sys
from pims.lib.niceresult import NiceResult
from pims.gutwrench.config import PimsConfigHandler
from pims.gutwrench.targets import get_target

# input parameters
defaults = {
'base_path':    '/Users/ken/temp/gutone',   # path of interest
'cfg_file':     'gutwrench.ini',            # config file {.ini|.run}
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
       
    # get config handler based on cfg_file
    cfgh = PimsConfigHandler(parameters['base_path'], cfg_file=parameters['cfg_file'])
   
    # emit start message
    print 'start processing %s' % cfgh.cfg_file
    
    # load cfg_file
    cfgh.load_config()
           
    # get target based on output section of cfg_file using target parameter there
    target = get_target(cfgh)
    
    if target:
        print 'got target = %s' % target.__class__.__name__

        if cfgh.ext == 'ini':
            # do target pre-processing
            pre_msg = target.pre_process()
            status_msg = 'done with pre-processing, ' + pre_msg
            
        elif cfgh.ext == 'run':
            # do target main-processing
            main_msg = target.main_process()
            status_msg = 'done with main-processing, ' + main_msg
        
        elif cfgh.ext == 'post':
            # do target post-processing
            post_msg = target.post_process()
            status_msg = 'done with post-processing, ' + post_msg    
        
        else:
            # unhandled extension on cfg_file
            status_msg = 'nothing to do when config file extension is "%s"' + cfgh.ext
        
        return status_msg
        
    else:
        
        raise Exception('no target found in OutputSection of config %s' % cfgh.cfg_file)


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
            print result
            return 0 # zero for unix success
        
    print_usage()  

# run main with cmd line args and return exit code
if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))
