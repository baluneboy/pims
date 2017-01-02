#!/usr/bin/env python

import glob, sys

if __name__ == '__main__':
    s = sys.argv[1]
    if '*' not in s:
        raise ValueError, "<<< DOUBLE-QUOTES OR ASTERISK NOT DETECTED IN INPUT >>>"
    wildPath = sys.argv[1]
    results = glob.glob(wildPath)
    for i in results:
        print i
    sys.exit(0)
