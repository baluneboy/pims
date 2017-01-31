#!/usr/bin/env python
version = '$Id$'

import recipes_switchyard_actions # actions to perform are defined in this 'helper' module (file)
import os
import sys
import string

# input parameters
defaults = {
'action':        'showargs', # default action
'stringArg':     'hello',    # string argument
'integerArg':    '3',        # integer argument
}
parameters = defaults.copy()
        
def perform( **kwargs ):
    funstr = kwargs['action']
    try:
        func = getattr(recipes_switchyard_actions, funstr)
    except AttributeError:
        print 'NO SUCH FUN CALLED "%s".' % funstr
        return None
    else:
        result = func( **kwargs )
    return result

def parametersOK():
    """check for reasonableness of parameters entered on command line"""
    if not os.path.exists('/tmp'):
        print 'the path (%s) does not exist' % '/tmp'
        return 0
    return 1 # all OK; otherwise, return 0 above here
    
def main(argv):
    """describe what this routine does here"""
    for p in argv: # parse command line
        pair = string.split(p, '=', 1)
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            print 'NOTE: command line args should be space-delimited key=value pairs.'
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parametersOK():
            result = perform(**parameters)
            print result

if __name__ == '__main__':
    
    print "USING COMMAND LINE (INCLUDES parametersOK CHECK):"
    main(sys.argv[1:])

    print "USING FAKE COMMAND LINE ARGS (INCLUDES parametersOK CHECK):"
    fakeCommandLineArgs = ['action=action2', 'ARG1=myString', 'ARG2=2']
    main(fakeCommandLineArgs)
    
    print "\nUSING DIRECT CALL, WHICH DOES NOT INCLUDE parametersOK CHECK:"
    d = { 'action':'action2', 'ARG1':'myString', 'ARG2':44 }
    result = perform(**d)
    print result
    
    print "\nHERE'S WHAT HAPPENS WHEN ACTION IS NOT HANDLED:"
    d = { 'action':'action9', 'ARG1':'myString', 'ARG2':44 }
    result = perform(**d)
    print result    