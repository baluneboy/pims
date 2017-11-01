#!/usr/bin/env python

"""
Return running packetGrabber info from standard set of South Park machines.
"""
# by Ken Hrovat
# License: MIT

import os
from commands import getoutput

def check_pg(c):
    """return string for packetGrabber command and its PID"""
    cmd = 'ssh %s pgrep -afl packetGrabber | grep bin' % c
    return getoutput(cmd)


#>>> o = getoutput("ssh manbearpig pgrep -afl packetGrabber | grep bin")
#>>> print o
#3129 /usr/local/bin/pims/packetGrabber
#>>> o = getoutput("echo $SPARKS")


if __name__ == '__main__':
    print check_pg('manbearpig')