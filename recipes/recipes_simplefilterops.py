#!/usr/bin/env python

# The readlines function is useful when implementing simple filter
# operations. Here are a few examples of such filter operations:

import string
import sys

def findLinesThatStartWith(c):
    """ Finding all lines that start with character c """
    for line in sys.stdin.readlines():
        if line[0] == c:
            print line, # need comma because line contains newline char at end

def extractColumn(n,*args):
    """ Extracting column n of a file (column delimiter 2nd arg or whitespace if none) """
    for line in sys.stdin.readlines():
        if args:
            words = string.split(line,args[0])
        else:
            words = string.split(line)
        if len(words) >= n:
            try:
                print words[n-1]
            except IndexError: # there aren't enough words
                pass

def printFirstLastEvery(f,L,n):
    """ Printing the first X lines, the last Y lines, and every Nth line """
    lines = sys.stdin.readlines()
    sys.stdout.writelines(lines[:f])       # first lines
    sys.stdout.writelines(lines[-(L):])     # last lines
    for lineIndex in range(0, len(lines), n):  # get 0, n, 2n, ...
        sys.stdout.write(lines[lineIndex])     # get the indexed line

def readChars():
    """ read character by character """
    while 1:
        next = sys.stdin.read(1)            # read a one-character string
        if not next:                        # or an empty string at EOF
            break
        print next

def readLin():
    """ read line by line """
    while 1:
        next = sys.stdin.readline()         # read a one-line string
        if not next:                        # or an empty string at EOF
            break
        print next

def countString(fname,s):
    """ (This is not a filter op) Counting the number of times the string occurs in a file """
    text = open(fname).read()
    print string.count(text, s)

if __name__ == "__main__":
    countString(sys.argv[1],'e')