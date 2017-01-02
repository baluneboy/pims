#!/usr/bin/env python

from pims.files.utils import extract_between_lines_as_list

if __name__ == "__main__":
    print extract_between_lines_as_list('/tmp/file1.txt', 'BEGIN LINE', 'END LINE')
    print extract_between_lines_as_list('/tmp/file1.txt', None, 'END LINE') ###
    print extract_between_lines_as_list('/tmp/file1.txt', 'BEGIN LINE', None)
    print extract_between_lines_as_list('/tmp/file1.txt', None, None)