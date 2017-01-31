#!/usr/bin/env python
version = '$Id$'

def action1( *args, **kwargs ):
    return 'This is action1 news.'

def action2( *args, **kwargs ):
    s = kwargs['ARG1']
    d = int(kwargs['ARG2'])
    return 'This is action2 with %s and %d; btw %d + 2 = %d' % ( s, d, d, d+2 )
    
def showargs( **kwargs ):
    s = ''
    for x in kwargs.keys():
        s += "%s = %s\n" % ( x, str(kwargs[x]) )
    return s