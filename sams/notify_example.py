#!/usr/bin/env python
version = '$Id$'

import os
import sys
import time
import datetime
from dateutil import parser, relativedelta
import subprocess

def growl(title, msg, timeout_msec, icon_file):
    if not os.path.isfile(icon_file): icon_file = '/home/pims/dev/programs/python/samslogs/icons/warning.png'
    cmd = 'notify-send -t %d --icon=%s %s "%s"' % (timeout_msec, icon_file, title, msg)
    subprocess.call([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

msg = 'one\ntwo\nthree\nfour\nfive\nsix'
growl('title', msg, 200, icon_file='nada')

# This is where pims.pth should be on jimmy:
# /usr/local/lib/python2.6/dist-packages/pims.pth
#
# NOT USED (YET) or on chef, cartman, others?
# /usr/local/lib/python2.7/site-packages/pims.pth
