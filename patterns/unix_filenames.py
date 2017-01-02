#!/usr/bin/env python

UNIX_FILEPAT = ur'^(.*/[^/ \t]*)+/?(.*)(\s*)$'

def match_pattern_demo(test_str, pat=UNIX_FILEPAT):
    """Check for match."""
    import re
    p = re.compile(pat, re.MULTILINE)
    return re.findall(p, test_str)

if __name__ == "__main__":

    test_str = u"""not matching this line
/home/user/Documents/foo.log was written
the file /home/user/Documents/foo.log was written
/home/user/Documents/foo.log
../foo.bar     """
    
    matches = match_pattern_demo(test_str, UNIX_FILEPAT)
    for m in matches:
        print m[0]
