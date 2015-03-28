#!/usr/bin/env python

from sys import stdin, stdout, stderr

# NOTE: isatty() is True when object is connected to a tty device

# TRY THESE ON COMMAND LINE:
# python note_isatty.py | cat
# echo 'hello' | python note_isatty.py
# echo 'hello' | python note_isatty.py 2>&1 | cat

print "stdin piped", not stdin.isatty()
print "stdout piped", not stdout.isatty()
print "stderr piped", not stderr.isatty()