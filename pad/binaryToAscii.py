#!/usr/bin/env python
# $Id: binaryToAscii.py,v 1.2 2002-02-13 12:42:10 pims Exp $
import sys, struct, string

if len(sys.argv) < 3:
    print """
 binaryToAscii.py converts PIMS PAD files from binary to ASCII
   - output files have the same names as input files with '.ascii' appended
   - PAD acceleration files usually have 4 columns, but other types of PAD
     files may have a different number
   
 usage:
   binaryToAscii.py numberOfColumns filename [filename ...]
     i.e., for one file:
   binaryToAscii.py 4 2001_05_31_00_09_33.969+2001_05_31_00_15_35.160.hirap
     or for all hirap files in a directory:
   binaryToAscii.py 4 *.hirap
"""
    sys.exit()

columns = string.atoi(sys.argv[1])

for filename in sys.argv[2:]: 
    f=open(filename)
    d = f.read()
    f.close()

    sys.stdout = open(filename+'.ascii', 'w')
    for i in range(len(d)/4):
        v = struct.unpack('<f', d[i*4:i*4+4]) # force little Endian float
        print '% 12.9e   ' % v,
        if i%columns == columns-1:
            print
    sys.stdout.close()

"""
This is a program written in the Python language. To run it, you need to
have Python installed on your computer. If your computer did not come with
Python, you can probably download a free version for your computer at:
http://www.python.org

For Windows, the free version of Python that comes with the Cygwin tools
(http://www.cygwin.com) is recommended. The Cygwin tools also include the
'bash' shell, which provides wildcard expansion that the standard Windows
shells do not. This is required for processing more than one file at a time.
"""
