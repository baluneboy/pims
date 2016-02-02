#!/usr/bin/env python

from pims.files.utils import get_lines_between

def rotate_file(preamble, new_text, filename='/misc/yoda/www/plots/user/sams/status/devicetimes.txt'):
    is_success = False
    old_text = get_lines_between('middle', 'end', filename, include_newlines=True)
    try:
        with open(filename, 'w') as modified:
            modified.write(preamble + '\nbegin\n' + old_text + '\nmiddle\n' + new_text +'\nend')
        is_success = True
    except:
        print 'FAILED to properly write to %s' % filename
    return is_success    

def weak_demo():
    is_success = rotate_file('PREAMBLE', 'NEW_TEXT')
    print is_success