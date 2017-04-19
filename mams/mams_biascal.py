#!/usr/bin/env python

import os
import sys
import datetime
from mams_main import query_mams_bias_cal
from pims.files.utils import prepend_tofile

# input parameters
defaults = {
'last':     '10',   # string for integer number of records to query (last means most recent)
'txt_file': '/misc/yoda/www/plots/MAMS/biascal.txt', # output text file
}
parameters = defaults.copy()
   
def parameters_ok():
    """check for reasonableness of parameters"""    

    try:
        parameters['last'] = int( parameters['last'] )
    except Exception, e:
        print 'could not get last input as integer: %s' % e.message
        return False

    if not os.path.exists(parameters['txt_file']):
        print 'txt_file (%s) does not exist' % parameters['txt_file']
        return False
    
    return True # all OK; otherwise, return False somewhere above

def print_usage():
    """print helpful text how to run the program"""
    #FIXME with git keyword sub via following:
    # http://stackoverflow.com/questions/11534655/git-keyword-substitution-like-those-in-subversion
    #print version << BETTER GO AT THIS???
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

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
            df = query_mams_bias_cal(last=parameters['last'])
            a = '#' * 55
            nowstr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            s = '%s\n%s\n%s' % (a, nowstr, a)
            s += '\n%s\n' % str(df)
            if len(df) == parameters['last']:
                prepend_tofile(s, parameters['txt_file'])
                return 0
            else:
                s += '\n*** ONLY GOT %d RECORDS ***' % len(df)
                prepend_tofile(s, parameters['txt_file'])                
                return -1

    print_usage() 

if __name__ == '__main__':
    main(sys.argv)
