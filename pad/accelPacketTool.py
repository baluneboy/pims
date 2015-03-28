#!/usr/bin/env python
# $Id$

# TODO
# - smart defaults and those to look for expected CCSDS pattern (mostly sequence counter)
# - better handling use iterator for pulse mode for TBD display handler

#----------------------------------------------------------
# Notes from PGUID Document KMAC sent me:
#----------------------------------------------------------
#
# START SAMS PACKET #######################################
## Header Part of Packet (44 bytes):
# 16 bytes EHS Primary Header
# 12 bytes     Secondary Header [called PDSS or EHS?]
#  6 bytes CCSDS Primary Header
# 10 bytes CCSDS Secondary Header
# --  --  --  --  --  --  --  --  --  --  --  --  --  --
## Payload Part of Packet (the remaining bytes):
# ~1200 bytes in the "Data Zone"
# END SAMS PACKET #########################################
#
# START HiRAP PACKET ######################################
## Header Part of Packet (60 bytes):
# 16 bytes EXPRESS Header
# 16 bytes EHS Primary Header
# 12 bytes     Secondary Header [called PDSS or EHS?]
#  6 bytes CCSDS Primary Header
# 10 bytes CCSDS Secondary Header
# --  --  --  --  --  --  --  --  --  --  --  --  --  --
## Payload Part of Packet (the remaining bytes):
# 1172 bytes in the "Data Zone" (HiRAP ALWAYS 1172 BYTES)
# END HiRAP PACKET ########################################

import os
import sys
import datetime
import numpy as np
import pandas as pd
from binascii import hexlify, unhexlify
from accelPacket import *

# input parameters
defaults = {
'db_tables':    None,       # use None for defaults
'details':      'False',    # True to get more details; otherwise False
}
parameters = defaults.copy()

# default dict for host look-up
DB_TABLES = {
    '121f02': 'kenny',
    '121f03': 'tweek',
    '121f04': 'mr-hankey',
    '121f05': 'chef',
    '121f08': 'timmeh',    
    'es03':   'ike',    
    'es05':   'ike',    
    'es06':   'butters',
    'hirap':  'towelie', 
}

# hex dump of packet (or header)
def packetDump(packet):
    """hex dump of packet (or header)"""
    hex = ''
    start = 0
    size = 16
    ln = len(packet)
    while start < ln:
        # print line number
        line = '%04x  ' % start
        #print hex representation
        c = 0
        asc = packet[start:min(start+size, ln)]
        for b in asc:
            if c == 8:
                line = line + '  '
            line = line + '%02x ' % ord(b)
            c = c + 1
        line = ljust(line, 58) + '"'
        # print ascii representation, replace unprintable characters with spaces
        for i in range(len(asc)):
            if ord(asc[i])<32 or ord(asc[i]) == 209:
                asc = replace(asc, asc[i], ' ')
        line = line + asc + '"\n'  
        hex = hex + line
        start = start + size
    return hex.rstrip('\n'), ln  

# get CCSDS time from header part of packet
def get_ccsds_time(hdr):
    """get CCSDS time from header part of packet"""
    UTIME1980 = 315964800.0
    b35, b36, b37, b38, b39 = struct.unpack('ccccc', hdr[34:39])
    coarse_hex = b35.encode('hex') + b36.encode('hex') + b37.encode('hex') + b38.encode('hex')
    fine_hex = b39.encode('hex')
    scale = 16 # for hexadecimal
    coarse = int(coarse_hex, scale) + UTIME1980
    fine = float(int(fine_hex, scale)) / (2.0**8)
    #return coarse, fine_hex, fine
    return datetime.datetime.fromtimestamp( coarse + fine )

# get CCSDS sequence counter from header part of packet
def get_ccsds_sequence(hdr):
    """get CCSDS sequence counter from header part of packet"""
    VALUE_MASK = 0x0FFF
    b31, b32 = struct.unpack('cc', hdr[30:32])
    my_hexdata = b31.encode('hex') + b32.encode('hex')
    #print my_hexdata
    scale = 16 # for hexadecimal
    #print int(my_hexdata, scale)
    #print bin(int(my_hexdata, scale))
    #print bin(int(my_hexdata, scale))[2:]
    ##num_of_bits = 16 # total bits
    ##print bin(int(my_hexdata, scale))[2:].zfill(num_of_bits)
    ##print bin(int(my_hexdata, scale) & VALUE_MASK)
    return int(my_hexdata, scale) & VALUE_MASK

# general query
class GeneralQuery(object):
    """general query"""
    
    def __init__(self, host, table, query_suffix):
        self.host = host
        self.table = table
        self.query_suffix = query_suffix
        self.set_querystr()

    def __str__(self):
        return '%s (%s) on %s' % (self.__class__.__name__, self.querystr, self.host)

    def set_querystr(self):
        self.querystr = 'SELECT * FROM %s %s;' % (self.table, self.query_suffix)       

    def get_results(self):
        return sqlConnect(self.querystr, self.host)

# default query has limit of 1 and desc time order
class DefaultQuery(GeneralQuery):
    """default query has limit of 1 and desc time order"""
    
    def __init__(self, host, table):
        super(DefaultQuery, self).__init__(host, table, query_suffix='ORDER BY time DESC LIMIT 1')

# SAMS SE half-sec foursome query
class SamsSeHalfSecFoursomeQuery(GeneralQuery):
    """
    SAMS SE half-sec foursome query has limit of 12
    -- should show 3 examples of KMAC's pattern of 4 pkts/half-sec = 4 pkts per CCSDS counter foursome
    ---> ccsds_time clusters of 4 with same time and with clusters a half second apart
    ---> ccsds_sequence_counter foursomes with monotonically decreasing (by exactly one) within each foursome
    """

    def __init__(self, host, table):
        super(SamsSeHalfSecFoursomeQuery, self).__init__(host, table, query_suffix = 'ORDER BY time DESC LIMIT 12')

# SAMS TSH one-sec eightsome query
class SamsTshOneSecEightsomeQuery(GeneralQuery):
    """
    SAMS TSH one-sec eightsome query has limit of 24
    -- should show 2 examples of TSH pattern of 8 pkts/sec = 8 pkts per CCSDS counter eightsome
    ---> ccsds_time clusters of 4 or 8 with same time and with clusters a multiple of 4msec apart
    ---> ccsds_sequence_counter eightsomes with monotonically decreasing (by exactly one) within each eightsome
    """

    def __init__(self, host, table):
        super(SamsTshOneSecEightsomeQuery, self).__init__(host, table, query_suffix = 'ORDER BY time DESC LIMIT 24')

# "start, length" query has ascending order with special limit to imply "start at rec" and "give me this many records"
class StartLenAscendQuery(GeneralQuery):
    """Like SELECT * FROM 121f04 ORDER BY time ASC LIMIT 2, 3; # ASC & LIMIT imply start at rec (2+1) and give me 3 results"""

    def __init__(self, host, table, start, length):
        suffix = 'ORDER BY time ASC LIMIT %d, %d' % ( (start-1) , length ) # zero is 1st rec
        super(StartLenAscendQuery, self).__init__(host, table, query_suffix = suffix)

# packet inspector for having good look at accel db packets
class PacketInspector(object):
    """packet inspector for having good look at accel db packets"""
    
    def __init__(self, host, table, query, details=True):
        self.host = host
        self.table = table
        self.query = query
        self.details = details
        self.results = None

    def __str__(self):
        s = '%s: use %s' % (self.__class__.__name__, self.query)
        if self.details:
            s += ' with details.'
        else:
            s += ' without details.'
        return s

    def do_query(self):
        self.results = self.query.get_results()

    def get_results_dataframe(self):
        # create raw dataframe
        df = pd.DataFrame( list(self.results), columns='t,p,k,h'.split(','))
        
        # put data in more desirable form
        df['ccsds_time'] = df['h'].map(get_ccsds_time)
        df['ccsds_sequence'] = df['h'].map(get_ccsds_sequence)
        df['db_time'] = df['t'].map(datetime.datetime.fromtimestamp)
        df['pkt_hex'] = df['p'].map(hexlify)
        df['hdr_hex'] = df['h'].map(hexlify)
        df['pkt_time'] = df['p'].map(self.get_pkt_time)
        df['pkt_type'] = df['k'].map(int)
        df['pkt_obj'] = df['p'].map(guessPacket)
        df['pkt_len'] = df['p'].map(len)
        df['hdr_len'] = df['h'].map(len)
        df['host'] = self.host
        df['table'] = self.table
        
        # drop unwanted columns from original raw dataframe
        df = df.drop(['t','p','k','h'], 1)
        
        # sort order
        df.sort(['ccsds_sequence', 'ccsds_time'], ascending=[True, True], inplace=True)
        
        return df

    def get_pkt_time(self, pkt):
        
        if self.table.startswith('121f0'):
            sec, usec = struct.unpack('II', pkt[36:44])
        
        elif self.table.startswith('es0'):
            sec, usec = struct.unpack('!II', pkt[64:72]) # ! for network byte order
        
        elif self.table == 'hirap':
            century = BCD(pkt[0])
            year =    BCD(pkt[1]) + 100*century
            month =   BCD(pkt[2])
            day =     BCD(pkt[3])
            hour =    BCD(pkt[4])
            minute =  BCD(pkt[5])
            second =  BCD(pkt[6])
            millisec = struct.unpack('h', pkt[8:10])[0]
            millisec = millisec & 0xffff
            return HumanToUnixTime(month, day, year, hour, minute, second, millisec/1000.0)
        
        else:
            return None
        
        return datetime.datetime.fromtimestamp( sec + usec/1000000.0 )

    # FIXME this is where we left off with non-class version of code
    #       include method to get this into DataFrame too?
    def display_results_awkwardly(self):
        # NOTE:
        # results[0] is time
        # results[1] is packet blob
        # results[2] is type
        # results[3] is header blob
        print self
        for t, p, k, h in self.results:
    
            # get CCSDS header time and sequence counter
            #ccsds_coarse_time, ccsds_fine_time_hex, ccsds_fine_time = get_ccsds_time(h)
            #ccsds_time_human = UnixToHumanTime(ccsds_coarse_time + ccsds_fine_time)
            ccsds_time = get_ccsds_time(h)
            ccsds_time_human = UnixToHumanTime(ccsds_time)
            ccsds_sequence_counter = get_ccsds_sequence(h)
            
            # FIXME for details and one-liner type output, how about hex(pkt), hex(hdr), and min/mean/max for t, x, y, z
            if self.details:
                print '='*88
                print 'The 4 columns in %s table are:' % self.table
                print '(1) time: %s' % UnixToHumanTime( t )
                print '(2) type: %d' % k
                
                phex, plen = packetDump(p)
                print '(3) packet (hex dump of %d bytes)' % plen
                print '-'*80
                print phex
                print '-'*80
                
                hhex, hlen = packetDump(h)
                print '(4) header (hex dump of %d bytes)' % hlen
                print '-'*80
                print hhex
                print '-'*80
                
                # NOTE:
                # the code above should work regardless of bogus records that might
                # trip up the code below that depends on recognizable packet content
                
                # guess packet and print details parsed from the packet blob
                pkt = guessPacket(p)
                if pkt.type == 'unknown':
                    print '??? UNKNOWN PACKET TYPE'
                    print '======================='
                    print 'db column time:', UnixToHumanTime( t ), '(%.4f)' % t
                    print '   packet time:'
                    print 'packet endTime:'
                    print '          name:'
                    print '          rate:'
                    print '       samples:'
                    #print 'measurementsPerSample:', pkt.measurementsPerSample()
                    utime = None
                    pkt_time_human = 'unknown'
                else:
                    print 'db column time:', UnixToHumanTime( t ), '(%.4f)' % t
                    print '   packet time:', UnixToHumanTime( pkt.time() )
                    print 'packet endTime:', UnixToHumanTime( pkt.endTime() )
                    print '          name:', pkt.name()
                    print '          rate:', pkt.rate()
                    print '       samples:', pkt.samples()
                    #print 'measurementsPerSample:', pkt.measurementsPerSample()
                    utime = pkt.time()
                    pkt_time_human = UnixToHumanTime( utime )
                    for t,x,y,z in pkt.txyz():
                        print "tsec:{0:>9.4f}  xmg:{1:9.4f}  ymg:{2:9.4f}  zmg:{3:9.4f}".format(t, x/1e-3, y/1e-3, z/1e-3)

            else:
                utime = self.get_pkt_time(p)
                if utime:
                    pkt_time_human = UnixToHumanTime(utime)
                else:
                    pkt_time_human = 'NoHandler4ThisTableName'
    
            # FIXME put this above details and improve handling of details versus utimes form of output
            print 'ccsds_time:%s, ccsds_sequence_counter:%05d, pkt_time:%s, table:%s' % (ccsds_time_human, ccsds_sequence_counter, pkt_time_human, self.table)

# use parameters to inspect packets in db table
def query_and_display(table, host, details, custom=None):
    """use parameters to inspect packets in db table"""
    
    if custom:
        query = GeneralQuery(host, table, custom)
    else:
        # create query object (without actually running the query)
        if table.startswith('121f0'):
            query = SamsSeHalfSecFoursomeQuery(host, table) # canned query to check for "half-sec foursome"
    
        elif table.startswith('es0'):
            query = SamsTshOneSecEightsomeQuery(host, table) # canned query to check for "one-sec eightsome"
    
        elif table == 'hirap':
            # FIXME is hirap just a case where ccsds_seq is "mostly or nearly contiguous"?
            #query = StartLenAscendQuery(host, table, 1, 245) # does it show pattern at rec ~80, ~160, and ~240?
            #query = GeneralQuery(host, table, 'WHERE time > unix_timestamp("2014-10-09 18:00:00") ORDER BY time ASC LIMIT 2')
            query = GeneralQuery(host, table, 'WHERE time > unix_timestamp("2014-11-01 00:00:00") ORDER BY time ASC LIMIT 13')
    
        else:
            query = DefaultQuery(host, table)
            query = GeneralQuery(host, table, 'WHERE time > unix_timestamp("2014-09-01 18:00:00") ORDER BY time ASC LIMIT 11')
    
    # create packet inspector object using query object as input
    pkt_inspector = PacketInspector(host, table, query=query, details=details)
    
    # now run the query and display results
    pkt_inspector.do_query()
    df = pkt_inspector.get_results_dataframe()
    return df
    #pkt_inspector.display_results_awkwardly()
    
# check for reasonableness of parameters
def params_ok():
    """check for reasonableness of parameters"""    
    
    if parameters['details'].lower() in ['true', 'yes', '1']:
        parameters['details'] = True
    elif parameters['details'].lower() in ['false', 'no', '0']:
        parameters['details'] = False
    else:
        print 'unrecognized input for details = %s, so set details=False' % parameters['details']
        parameters['details'] = False

    if not parameters['db_tables']:
        parameters['db_tables'] = DB_TABLES

    # FIXME ideally, check for tables on hosts in pre-cursory fashion here

    return True # params are OK; otherwise, we returned False above

# print short description of how to run the program
def print_usage():
    """print short description of how to run the program"""
    print 'USAGE:    %s [options]' % os.path.abspath(__file__)
    print 'EXAMPLE1: %s # FOR DEFAULTS' % os.path.abspath(__file__)
    print 'EXAMPLE2: %s 121f03=tweek hirap=towelie details=False # TWO SMALL SETS' % os.path.abspath(__file__)
    print 'EXAMPLE3: %s 121f03=tweek details=True # ONE DETAILED SET' % os.path.abspath(__file__)
    print 'EXAMPLE4: %s details=True # SHOWS MAX INFO' % os.path.abspath(__file__)

# iterate over db query results to show pertinent packet details (and header info when details=True)
def main(argv):
    """iterate over db query results to show pertinent packet details (and header info when details=True)"""
    # parse command line
    args = dict([arg.split('=') for arg in sys.argv[1:]])
    # special handling of details argument
    if 'details' in args:    
        parameters['details'] = args['details']
        del( args['details'] )
    # special handling of custom argument
    if 'custom' in args:
        parameters['custom'] = args['custom']
        del( args['custom'] )
    else:
        parameters['custom'] = None
    db_tables = args
    parameters['db_tables'] = db_tables

    if params_ok():
        print parameters
        sensor_tables = parameters['db_tables']
        
        # FIXME a class that contains multiple PacketInspector objects (to add, sort, etc. those)
        df_cat = pd.DataFrame()
        for sensor, host in sensor_tables.iteritems():
            df_cat = pd.concat( [df_cat, query_and_display(sensor, host, parameters['details'], parameters['custom'])] )
            
        # sort by CCSDS sequence, then CCSDS time
        df_cat.sort(['ccsds_sequence', 'ccsds_time'], ascending=[True, True], inplace=True)
        df_cat.reset_index(inplace=True, drop=True)
        
        df_cat['ccsds_sequence_delta'] = (df_cat['ccsds_sequence']-df_cat['ccsds_sequence'].shift()).fillna(np.NaN)
        df_cat['ccsds_time_delta'] = (df_cat['ccsds_time']-df_cat['ccsds_time'].shift()).fillna(np.NaN)
        
        # FIXME to get sec delta, SOMEHOW need to convert via pd.Timestamp( np.datetime64('2012-05-01T01:00:00.000000') )
        #print pd.Timestamp( np.datetime64('2012-05-01T01:00:00.000000') )
        #df_cat['ccsds_sec_delta'] = df_cat['ccsds_time_delta'].map(tdelta2sec)
        
        print df_cat

        return 0

    print_usage()  

# ----------------------------------------------------------------------
# EXAMPLES:
# accelPacketTool.py 121f02=kenny 121f03=tweek details=False
# accelPacketTool.py details=True
# accelPacketTool.py details=False
# ----------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit( main(sys.argv) )
