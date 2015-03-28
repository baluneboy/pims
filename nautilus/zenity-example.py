#!/usr/bin/env python

import os
import subprocess
import sys

def showFile(f, curdir):
    cmd = 'zenity --entry --text "' + f + '" --title "' + curdir + '"'
    process = subprocess.Popen(cmd, shell=True)

def main():
    selected = os.environ.get('NAUTILUS_SCRIPT_SELECTED_FILE_PATHS', '').strip().split('\n')
    curdir = os.environ.get('NAUTILUS_SCRIPT_CURRENT_URI', os.curdir).replace('file://', '')
    for s in selected:
        # replace the next line with your code
        showFile(s, curdir)
    return 0

if __name__ == '__main__':
    sys.exit(main())