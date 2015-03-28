#! /usr/bin/env python

"""repeat <shell-command>

This simple program repeatedly (at 1-second intervals) executes the
shell command given on the command line and displays the output (or as
much of it as fits on the screen).  It uses curses to paint each new
output on top of the old output, so that if nothing changes, the
screen doesn't change.  This is handy to watch for changes in e.g. a
directory or process listing.

To end, hit Control-C.
"""

# Author: Guido van Rossum

# Disclaimer: there's a Linux program named 'watch' that does the same
# thing.  Honestly, I didn't know of its existence when I wrote this!

# To do: add features until it has the same functionality as watch(1);
# then compare code size and development time.

# Modified by Ken Hrovat: "Guido...re-use of run...c'mon man!"

import sys
import time
import curses
import subprocess # Guido used popen from os module

# run command # FIXME DANGER using shell=True, user could inject harmful commands!
def run(cmd):
    """run command"""
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    stdout, stderr = proc.communicate()
    if stderr:
        sys.exit(stderr)
    return stdout

_UPDATE_SEC = 3
_NORMAL = curses.A_NORMAL
_REVERSE = curses.A_REVERSE
_BOLD = curses.A_BOLD
_UNDERLINE = curses.A_UNDERLINE

# loop to repeat run of command 
def main():
    """loop to repeat run of command"""
    if not sys.argv[1:]:
        print __doc__
        sys.exit(0)
    cmd = " ".join(sys.argv[1:])
    text = run(cmd)
    w = curses.initscr()
    try:
        while True:
            w.erase()
            try:
                w.addstr(0, 0, "Ctrl-C to quit / update every %ds" % _UPDATE_SEC)
                w.addstr(1, 0, run('date'), _BOLD)
                w.addstr(cmd + '\n', _UNDERLINE)
                w.addstr(text, _NORMAL)
                w.addstr(text, _REVERSE)
            except curses.error:
                pass
            w.refresh()
            time.sleep(_UPDATE_SEC)
            text = run(cmd)
    finally:
        curses.endwin()

if __name__ == "__main__":
    main()
