#!/usr/bin/env python

import os
import glob
import sys
import shutil
from recipes_fileutils import fileAgeDays

MAXDAYS = 5
MAXRMSDAYS = 31

# return True if file age in days > MAXDAYS (or MAXRMSDAYS for "*rms.jpg")
def isVeryOld(f):
    """
    return True if file age in days > MAXDAYS (or MAXRMSDAYS for "*rms.jpg")
    """
    if f.endswith('rms.jpg'):
        dmax = MAXRMSDAYS
    else:
        dmax = MAXDAYS
    return fileAgeDays(f) > dmax

# return True if file age in days > 2
def isOld(f):
    """return True if file age in days > 2"""
    return fileAgeDays(f) > 2

# move file to recent folder
def moveToRecent(f):
    """move file to recent folder"""
    shutil.move(f, '/misc/yoda/www/plots/user/buffer/recent/')

# remove very old file
def removeVeryOld(f):
    """remove very old file"""
    os.remove(f)

# process path with disposition based on criteria 
def processPath(wildPath, criteria, disposition):
    """process path with disposition based on criteria"""
    count = 0
    for f in glob.glob(wildPath):
        if criteria(f):
            disposition(f)
            count += 1
    return count

# move old files and remove very old files
def main():
    """move old files and remove very old files"""
    numMoved = processPath('/misc/yoda/www/plots/user/buffer/*.jpg', isOld, moveToRecent)
    numRemoved = processPath('/misc/yoda/www/plots/user/buffer/recent/*.jpg', isVeryOld, removeVeryOld)
    return 'moved %d files and removed %d files' % (numMoved, numRemoved)

if __name__ == '__main__':
    print main()
    sys.exit(0)
