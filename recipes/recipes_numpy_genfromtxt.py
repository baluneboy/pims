#!/usr/bin/env python

import numpy as np
import datetime
from StringIO import StringIO
from dateutil import parser, relativedelta

def getDemoData():
    """ example data """
    
    # a file-like object to read from via numpy
    a = StringIO("""
    a 2012-12-31/02:15:22 2012-12-31/22:15:30 OK
    b 2012-12-31/23:45:33 2013-01-01/11:05:40 BAD
    c 2013-01-01/11:25:40 2013-01-01/19:44:55 OK
    """)
    
    # Converts str into a datetime object.
    conv = lambda s:datetime.datetime.strptime(s,'%Y-%m-%d/%H:%M:%S')
    
    # Use numpy to read the data in. 
    data = np.genfromtxt(a, converters={1: conv, 2: conv}, names=['caption','start','stop','state'], dtype=None)
    caption, start, stop, state = data['caption'], data['start'], data['stop'], data['state']
    
    return caption, start, stop, state

def showDemo():
    """
    
    >>> showDemo()
    a 31-Dec-2012/02:15:22 31-Dec-2012/22:15:30 OK
    b 31-Dec-2012/23:45:33 01-Jan-2013/11:05:40 BAD
    c 01-Jan-2013/11:25:40 01-Jan-2013/19:44:55 OK
    
    """
    
    fmt = '%d-%b-%Y/%H:%M:%S'
    # Build y values from the number of start values
    caption, start, stop, state = getDemoData()
    for cap,t1,t2,cond in zip(caption,start,stop,state):
        print cap, t1.strftime(fmt), t2.strftime(fmt), cond

def simpleFail():
    """
    
    >>> simpleFail()
    Actually, this is expected to fail.
    
    """
    print 'hello'

#import csv
#from recipes_itertools import grouper
#
#PWR_ON_CODE = 1129
#PWR_OFF_CODE = 1128
#BAD_REC = ['01-Jan-1970/00:00:00', '-999', '-9999']
#def scan_power_duration(on_off_recs):
#    row1 = on_off_recs[0]
#    row2 = on_off_recs[1]
#    t1 = parser.parse(row1[0])
#    t2 = parser.parse(row2[0])
#    code1 = int(row1[2])
#    code2 = int(row2[2])
#    if row1 is BAD_REC or row2 is BAD_REC or (code1 != PWR_ON_CODE) or (code2 != PWR_OFF_CODE) or (t2 < t1):
#        prefix = 'on/off records BAD '
#        hours = 0.00
#    else:
#        prefix = 'on/off records OKAY'
#        hours = relativedelta.relativedelta(t2, t1).hours
#    print '%s, POWER ON at %s, OFF at %s, %5.2f, hours' % (prefix, t1, t2, hours)
#
#for g in grouper(2, csv.reader(open("results.csv", "rb")), BAD_REC):
#    scan_power_duration(g)

def testdoc():
    import doctest
    return doctest.testmod()

if __name__ == "__main__":
    testdoc() # pass "-v" as input arg to see verbose test output
