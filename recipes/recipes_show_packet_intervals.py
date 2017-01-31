#!/usr/bin/env python
version = '$Id$'

import csv
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator, MinuteLocator
import numpy as np
import datetime
from interval import Interval, IntervalSet
from recipes_itertools import grouper
from dateutil import parser, relativedelta

# input parameters
defaults = {
'dir':           '/tmp',               # a path of interest
'infile':        'intervals2.csv',     # input csv
'fs':            None                  # sample rate (sa/sec)
}
parameters = defaults.copy()

# a constant used by grouper to handle case when there are "unpaired" on/off records (odd #)
BAD_REC = Interval( datetime.datetime(1970, 1, 1, 0, 0, 0), datetime.datetime(1970, 1, 1, 0, 0, 0) )

def convert_relativedelta_to_seconds(rdelta):
    return rdelta.days*86400.0 + rdelta.hours*3600.0 + rdelta.minutes*60.0 + rdelta.seconds + rdelta.microseconds/1.0e6

class PacketIntervalSet(IntervalSet):
    
    def append_interval(self, start, sec):
        t2 = start + datetime.timedelta(seconds=sec)
        self.add( Interval(start,t2) )

def packet_gaps(grp):
    i1 = grp[0]
    i2 = grp[1]
    dtm1 = i1.upper_bound
    dtm2 = i2.lower_bound
    seconds = convert_relativedelta_to_seconds( relativedelta.relativedelta(dtm2, dtm1) )
    if seconds > parameters['max_gap_sec']:
        print seconds, dtm1, dtm2, "GAP TOO BIG"
    else:
        print seconds, dtm1, dtm2, "okay gap"
    #print prefix, cat1, sub1, str(dtm1), sub2, str(dtm2), '%5.3f' % hours
    #writer.writerow([prefix, cat1, sub1, str(dtm1), sub2, str(dtm2), '%5.3f' % hours])

def getDemoData():
    """ example data """
    from StringIO import StringIO

    # a file-like object to read from via numpy
    a = StringIO("""
    Start processing 4799 packets (299925 records, 600.0094s) starting at 2013_06_15_16_25_12.082; vecmag(max,mean,std) = (5339.4, 1407.2, 599.1) ug done.
    Start processing 4800 packets (299999 records, 600.0096s) starting at 2013_06_15_16_35_12.093; vecmag(max,mean,std) = (16349.0, 1380.5, 598.5) ug done.
    Start processing 4800 packets (299999 records, 600.0072s) starting at 2013_06_15_16_45_12.105; vecmag(max,mean,std) = (11685.5, 1408.1, 601.1) ug done.
    Start processing 4799 packets (299926 records, 600.0116s) starting at 2013_06_15_16_55_12.114; vecmag(max,mean,std) = (5075.1, 1382.7, 583.5) ug done.
    Start processing 4800 packets (299999 records, 600.0092s) starting at 2013_06_15_17_05_12.128; vecmag(max,mean,std) = (4932.1, 1397.8, 588.1) ug done.
    Start processing 4799 packets (299925 records, 599.8615s) starting at 2013_06_15_17_15_12.139; vecmag(max,mean,std) = (5316.4, 1403.5, 591.4) ug done.
    Start processing 4800 packets (299999 records, 600.0092s) starting at 2013_06_15_17_25_12.002; vecmag(max,mean,std) = (5032.0, 1396.9, 590.6) ug done.
    Start processing 4800 packets (299999 records, 600.0096s) starting at 2013_06_15_17_35_12.013; vecmag(max,mean,std) = (4859.4, 1385.1, 584.3) ug done.
    Start processing 4800 packets (299999 records, 600.0092s) starting at 2013_06_15_17_45_12.025; vecmag(max,mean,std) = (4637.3, 1420.4, 601.1) ug done.
    Start processing 4799 packets (299971 records, 600.0094s) starting at 2013_06_15_17_55_12.036; vecmag(max,mean,std) = (4864.1, 1398.3, 592.7) ug done.
    Start processing 4799 packets (299925 records, 600.0094s) starting at 2013_06_15_18_05_12.048; vecmag(max,mean,std) = (4679.2, 1422.6, 604.9) ug done.
    Start processing 4800 packets (299999 records, 600.0094s) starting at 2013_06_15_18_15_12.059; vecmag(max,mean,std) = (8620.7, 1390.8, 592.5) ug done.
    """)
    
    # Converts str into a datetime object.
    conv4 = lambda s:s.lstrip('(')
    conv6 = lambda s:s.rstrip('s)')
    conv9 = lambda s:datetime.datetime.strptime(s,'%Y_%m_%d_%H_%M_%S.%f;')    

    # Use numpy to read the data in. 
    data = np.genfromtxt(a, converters={4: conv4, 6: conv6, 9:conv9}, names=['zero','one','packets','three','records','five','seconds','seven','eight','starts','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen'], dtype=None)
    packets, records, seconds, starts = data['packets'], data['records'], data['seconds'], data['starts']
    
    recs = [int(i) for i in records]
    secs = [float(i) for i in seconds]
    
    # Return info
    return packets, recs, secs, starts

def get_data(f):
    """ get data """
    
    # Converts str into a datetime object.
    conv4 = lambda s:s.lstrip('(')
    conv6 = lambda s:s.rstrip('s)')
    conv9 = lambda s:datetime.datetime.strptime(s,'%Y_%m_%d_%H_%M_%S.%f;')    

    # Use numpy to read the data in. 
    data = np.genfromtxt(f, converters={4: conv4, 6: conv6, 9:conv9}, names=['zero','one','packets','three','records','five','seconds','seven','eight','starts','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen'], dtype=None)
    packets, records, seconds, starts = data['packets'], data['records'], data['seconds'], data['starts']
    
    recs = [int(i) for i in records]
    secs = [float(i) for i in seconds]
    
    # Return info
    return packets, recs, secs, starts

def parametersOK():
    """check for reasonableness of parameters entered on command line"""    
    if not os.path.exists(parameters['dir']):
        print 'the path (%s) does not exist' % parameters['dir']
        return 0

    infile = os.path.join(parameters['dir'], parameters['infile'])
    if not os.path.exists(infile):
        print 'the input file (%s) does not exist' % infile
        return 0
    parameters['infile'] = infile

    parameters['max_gap_sec'] = 2.0 * ( 1.0 / float(parameters['fs']) )

    print 'dir:',           parameters['dir']
    print 'infile:',        parameters['infile']
    print 'max_gap_sec:',   parameters['max_gap_sec']
    print '=' * 44

    return 1 # all OK; otherwise, return 0 above

def process_text_file(infile):
    r = PacketIntervalSet()
    packets, records, seconds, starts = get_data(infile)
    for pkt,rec,sec,start in zip(packets,records,seconds,starts):
        r.append_interval(start, sec)
    for g in grouper(2, r, BAD_REC):
        packet_gaps(g)        
    #return r

def printUsage():
    """print short description of how to run the program"""
    print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])
    
def main(argv):
    """describe what this routine does here"""
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parametersOK():
            r = process_text_file(parameters['infile'])
            #for i in r:
            #    print i
            return 0
    printUsage()  

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
