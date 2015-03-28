#! /usr/bin/env python

"""pmon <update_sec>

To end, hit Control-C.

This simple program repeatedly (every update_sec seconds) executes the pims
monitoring routines on the command line and displays the output (or as much of
it as fits on the screen). It uses curses to paint each new output on top of the
old output, so that if nothing changes, the screen doesn't change. This is handy
to watch for changes.

"""

# Author: Ken Hrovat

import sys
import time
import curses
import subprocess

_NORMAL = curses.A_NORMAL
_REVERSE = curses.A_REVERSE
_BOLD = curses.A_BOLD
_UNDERLINE = curses.A_UNDERLINE

# run command # FIXME DANGER using shell=True, user could inject harmful commands!
def run(cmd):
    """run command"""
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    stdout, stderr = proc.communicate()
    if stderr:
        sys.exit(stderr)
    return stdout

# loop to repeat run of command 
def main():
    """loop to repeat run of command"""
    if not sys.argv[1:]:
        print __doc__
        sys.exit(0)
    update_sec = int(sys.argv[1])
    cmd1 = "date"
    text1 = run(cmd1)
    w = curses.initscr()
    try:
        while True:
            w.erase()
            try:
                w.addstr(0, 0, "Ctrl-C to quit / update every %ds" % update_sec)
                w.addstr(1, 0, run('date'), _BOLD)
                w.addstr(cmd1 + '\n', _UNDERLINE)
                w.addstr(text1, _NORMAL)
                w.addstr(text1, _REVERSE)
            except curses.error:
                pass
            w.refresh()
            time.sleep(update_sec)
            text1 = run(cmd1)
    finally:
        curses.endwin()

if __name__ == "__main__":
    main()
