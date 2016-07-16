#!/usr/bin/env python

import os
import re
import sys
from shutil import copyfile

# TODO << probably in some other 'fileutils' folder under pims
# - remove dot bak files in /Users/ken/NorthfieldBackups that
#   have filename prefix date field older than 2 months ago

# Regexp for "Cr Hershberger" or maybe "Crist Hershberger" (no quotes)
_PATTERN = r'(?P<first>Cr[^>]*)([^<]+)(?P<last>Hershberger)'

def get_matches(fname, pat):
    matches = set()
    with open(fname, 'r') as f:
        contents = f.read() 
        for match in re.finditer(pat, contents):
            s = match.group(0)
            matches.add(s)
    return matches

def OLDmark_matches(file_old, str_old, file_new):
    with open(file_new, "wt") as fout:
        with open(file_old, "rt") as fin:
            for line in fin:
                str_new = '<mark>' + str_old + '</mark>'
                print str_old, ' to ', str_new
                fout.write(line.replace(str_old, str_new))

def mark_matches(file_old, matches, file_new):
    with open(file_new, "wt") as fout:
        with open(file_old, "rt") as fin:
            contents = fin.read()
            for str_old in matches:
                str_new = '<mark>' + str_old + '</mark>'
                contents = contents.replace(str_old, str_new)
        fout.write(contents)

def demo_test():
    pth = '/tmp'
    files = ['2016-06-22.htm', '2016-06-27.htm', '2016-06-29.htm', '2016-06-28.htm', '2016-07-02.htm']
    files = ['062216.htm']
    for f in files:
        old_file = os.path.join(pth,f)
        new_file = os.path.join(pth + '/new', f)
        matches = get_matches(old_file, _PATTERN)
        print matches
        mark_matches(old_file, matches, new_file)
        print new_file

#demo_test()
#raise SystemExit

if __name__ == "__main__":
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    print 'marking matches in %s ' % new_file,
    matches = get_matches(old_file, _PATTERN)
    if matches:
        mark_matches(old_file, matches, new_file)
    else:
        # just copy old_file to new_file
        copyfile(old_file, new_file)
    print 'done',
