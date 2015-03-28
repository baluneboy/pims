#!/usr/bin/env python
# Adapted from following version (except passwords were removed):
# $Id: accelPacket.py,v 1.41 2004-08-27 19:13:32 pims Exp $

from string import *
import struct
from MySQLdb import *
from _mysql_exceptions import *
from time import *
from commands import *
from syslog import *
import exceptions
import datetime
import numpy as np

from pims.utils.pimsdateutil import unix2dtm
from pims.config.conf import get_db_params
from pims.pad.padpro import PadInterval, PadIntervalSet

# Get sensitive authentication credentials for internal MySQL db query
SCHEMA, UNAME, PASSWD = get_db_params('pimsquery')

class BCDConversionException(exceptions.Exception):
    def __init__(self, args=None):
        if args:
            self.args = args

class WrongTypeOfPacket(exceptions.Exception):
    def __init__(self, args=None):
        if args:
            self.args = args

# plugable 0-argument function to be called when idling. It can return true to stop idling. 
addIdleFunction = None
def addIdle(idleFunction):
    global addIdleFunction
    addIdleFunction = idleFunction 
def idleWait(seconds = 0):
    for i in range(seconds):
        if addIdleFunction:
            if addIdleFunction():
                return 1
        sleep(1)
    else: # always execute at least once
        if addIdleFunction:
            return addIdleFunction()
    return 0

# plugable function to be called to log something
addLogFunction = None
def addLog(logFunction):
    global addLogFunction
    addLogFunction = logFunction
    
# write message to syslog, console and maybe more
def printLog(message):
    print message
    syslog(LOG_WARNING|LOG_LOCAL0, message)
    if addLogFunction:
        addLogFunction(message)
    
# convert "Unix time" to "Human readable" time
def UnixToHumanTime(utime, altFormat = 0):
    try:
        fraction = utime - int(utime)
    except OverflowError, err:
        t = 'Unix time %s too long to convert, substituting 0' % utime
        printLog(t)
        fraction = utime = 0
    # handle special case of -1 (not handled correctly by 'date')
    if int(utime == -1):
        return (1969,12,31,23,59,59)
    cmd = 'date -u -d "1970-01-01 %d sec" +"%%Y %%m %%d %%H %%M %%S"' % int(utime)
    try:
        result = getoutput(cmd)
        s = split(result)
        s[5] = atoi(s[5]) + fraction
    except ValueError, err:
        t = 'date conversion error\ndate command was: %sdate command returned: %s' % (cmd, result)
        printLog(t)
        raise ValueError, err
    if altFormat == 0:
        return "%s_%s_%s_%s_%s_%06.3f" % tuple(s)
    elif altFormat == 1:
        return "%s/%s/%s %s:%s:%06.3f" % tuple(s)
    else: # altformat == 2
        s[0:5]=map(atoi, s[0:5])
        return tuple(s)

# convert "Human readable" to "Unix time" time
def HumanToUnixTime(month, day, year, hour, minute, second, fraction = 0.0):
    cmd = 'date -u -d "%d/%d/%d %d:%d:%d UTC" +%%s' % tuple((month, day, year, hour, minute, second))
    result = 0
    try:
        result=int(getoutput(cmd)) + fraction
    except ValueError, err:
        t = 'date conversion error\ndate command was: %sdate command returned: %s' % (cmd, result)
        printLog(t)
        raise ValueError, err
    return result
    
# byte to BCD conversion
def BCD(char):
    byte = ord(char)
    tens = (byte & 0xf0) >> 4
    ones = (byte & 0x0f)
    if (tens > 9) or (ones > 9):
        raise BCDConversionException, 'tens: %s, ones:%s' % (tens, ones)
    return tens*10+ones

# escape characters that are special to XML 
def xmlEscape(s):
    s=join(split(s, '&'), '&amp;')
    s=join(split(s, '<'), '&lt;')
    s=join(split(s, '>'), '&gt;')
    s=join(split(s, '"'), '&quot;')
    s=join(split(s, '\''), '&apos;')
    return s

# SQL helper routines ---------------------------------------------------------------
# create a connection (with possible defaults), submit command, return all results
# try to do all connecting through this function to handle exceptions
def sqlConnect(command, shost='localhost', suser=UNAME, spasswd=PASSWD, sdb=SCHEMA):
    sqlRetryTime =30
    repeat = 1
    while repeat:
        try:
            con = Connection(host=shost, user=suser, passwd=spasswd, db=sdb)
            cursor = con.cursor()
            cursor.execute(command)
            results = cursor.fetchall()
            repeat = 0
            cursor.close()
            con.close()
        except MySQLError, msg:
            t = UnixToHumanTime(time(), 1) + '\n' + msg[1] + '\nMySQL call failed, will try again in %s seconds' % sqlRetryTime
            printLog(t)
            if idleWait(sqlRetryTime):
                return []

    return results

# -----------------------------------------------------------------------------------

# try to create a packet of the appropriate type
def guessPacket(packet, showWarnings=0):
    subtypes = [sams2Packet,samsTshEs, hirap, oss, oare, besttmf, finaltmf, finalbias, radgse, samsff, artificial]
    for i in subtypes:
        try:
            p = i(packet, showWarnings=0)
            return p
        except WrongTypeOfPacket:
            pass
    if showWarnings:
        t = UnixToHumanTime(time(), 1) + 'unknown packet type detected'
        printLog(t)
    return accelPacket(packet)

DigitalIOstatusHolder = {} # global dictionary to hold SAMS TSH-ES DigitalIOstatus between packets

#def getCCSDS(hb):
#    #for b in hb[38:39]:
#    #    print '%02x ' % ord(b)
#    sec = struct.unpack('!I', hb[34:38])[0] 
#    sec = sec + 315964800
#    msec = ord(hb[38:39])/float(256)
#    return sec + msec
#
#def printHeaderBlob(hb):
#	hx = ''
#	start = 0
#	size = 16
#	ln = len(hb)
#	while start < ln:
#		# print line number
#		line = '%04x  ' % start
#		#print hex representation
#		c = 0
#		asc = hb[start:min(start+size, ln)]
#		for b in asc:
#			if c == 8:
#				line = line + '  '
#			line = line + '%02x ' % ord(b)
#			c = c + 1
#		line = ljust(line, 58) + '"'
#		# print ascii representation, replace unprintable characters with spaces
#		for i in range(len(asc)):
#			if ord(asc[i])<32 or ord(asc[i]) == 209:
#				asc = replace(asc, asc[i], ' ')
#		line = line + asc + '"\n'  
#		hx = hx + line
#		start = start + size
#	return hx

###############################################################################    
# class to represent all types of accel data (SAMS2, MAMS, etc)
class accelPacket:
    # packets don't change, so we can cache all the calculated values for reuse
    def __init__(self, packet):
        self.p = packet
        self._rep_ = None
        self.type = 'unknown'
        self._time_ = None
        self._dqmIndicator_ = 0
        self._additionalDQMtext_ = ''

    # return the name of the data directory appropriate for this packet:
    def dataDirName(self):
        return self.type        

   # return anything that should be inserted into the DQM header 
    def additionalDQM(self):
        return self._additionalDQMtext_

    # add something to the DQM header (note: only one packet in the PAD file is checked for
    #    additionalDQM, so you can't just call this any time and expect it to show up)
    def addAdditionalDQM(self, text):
        self._additionalDQMtext_ = self._additionalDQMtext_ + text

    # return header dictionary appropriate for this packet (everything except the accel data)
    def header(self):
        raise 'Subclass responsibility'
    
    # return sensor name appropriate for this packet (for database table)
    def name(self):
        raise 'Subclass responsibility'
    
    # return xyz info appropriate for this packet
    def xyz(self):
        raise 'Subclass responsibility'
    
    # return txyz info appropriate for this packet
    def txyz(self):
        raise 'Subclass responsibility'
    
    # return extraColumns info appropriate for this packet
    def extraColumns(self):
        return None

    # return starting time appropriate for this packet
    def time(self):
        raise 'Subclass responsibility'

    # return ending time appropriate for this packet
    def endTime(self):
        raise 'Subclass responsibility'

    # return data sample appropriate for this packet
    def rate(self):
        raise 'Subclass responsibility'

    # return header info in XML format for this packet
    def xmlHeader(self):
        raise 'Subclass responsibility'

    # return true if this packet is contiguous with the supplied packet
    def contiguous(self, other):
        if not other:
#            print 'contiguous: no other'
            return 0
        if self.type != other.type: # maybe we should throw an exception here
#            print 'contiguous: other type mis-match'
            return 0
        if self.rate() != other.rate():
#            print 'contiguous: other rate mis-match'
            return 0
        if self._dqmIndicator_ != other._dqmIndicator_:
#            print 'contiguous: other dqm mis-match'
            return 0
        ostart = other.time()
        oend = other.endTime()
        start = self.time()
        if self.rate() == 0: # non-periodic data
#            print 'contiguous: OK non-periodic'
            return (start > oend)
        gap = start - oend
        # when samples == 1, any jitter can cause a delay that shows up as a gap, so inflate allowableGap
        if self.samples() == 1:
            allowAbleGap = 1.5*self.samples()/self.rate()
        else:
            allowAbleGap = self.samples()/self.rate()
        result =  (start >= ostart) and (gap <= allowAbleGap)
        #print "here", result, gap,allowAbleGap
        #if not result:
        #     print 'contiguous:%s ostart:%.4lf oend:%.4lf start:%.4lf gap:%.4lf allowAbleGap:%.4lf' % (result, ostart, oend, start, gap, allowAbleGap) 
        return result
    
    # print a representation of this packet
    def dump(self, accelData=0):
        if not self._rep_:
            header = self.header()
            hkeys = header.keys()
            className = split(str(self.__class__), '.')[1] 
            self._rep_ = '%s(' % className
            for i in hkeys:
                if i == 'time' or i == 'endTime': # work around Python 3 decimal place default for times
                    self._rep_ = self._rep_ + ' %s:%.4f' % (i, header[i])
                else:
                    self._rep_ = self._rep_ + ' %s:%s' % (i, header[i])
            if accelData:
                self._rep_ = self._rep_ + '\ndata:'
                for j in self.xyz():
                    self._rep_ = self._rep_ + '\n%.7e %.7e %.7e' % tuple(j)
#                for j in self.txyz():
#                    self._rep_ = self._rep_ + '\n%.4f %.7e %.7e %.7e' % j
        return self._rep_
        
    def hexDump(self):
        self._hex_ = ''
        start = 0
        size = 16
        ln = len(self.p)
        while start < ln:
            # print line number
            line = '%04x  ' % start
            #print hex representation
            c = 0
            asc = self.p[start:min(start+size, ln)]
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
            self._hex_ = self._hex_ + line
            start = start + size
        return self._hex_

###############################################################################    
class oss(accelPacket):
    # packets don't change, so we can cache all the calculated values for reuse
    def __init__(self, packet, showWarnings=0):
        accelPacket.__init__(self, packet)
        self._showWarnings_ = showWarnings
        self._oss_ = None
        if not self.isOSSPacket():
            raise WrongTypeOfPacket
        self.type = 'mams_accel_ossraw'
        self._name_ = None
        self._rate_ = 10.0
        self._header_ = {}
        self._samples_ = None
        self._time_ = None
        self._endTime_ = None
        self._temperature_ = None
        self._Ts_ = []
        self._xyz_ = []
        self._txyz_ = []
        self._xmlHeader_ = None
        
    # print a representation of this packet
    def dump(self, accelData=0):
        if not self._rep_:
            header = self.header()
            hkeys = header.keys()
            className = split(str(self.__class__), '.')[1] 
            self._rep_ = '%s(' % className
            for i in hkeys:
                if i == 'time' or i == 'endTime': # work around Python 3 decimal place default for times
                    self._rep_ = self._rep_ + ' %s:%.4f' % (i, header[i])
                else:
                    self._rep_ = self._rep_ + ' %s:%s' % (i, header[i])
            if accelData:
                self._rep_ = self._rep_ + '\ndata:'
                for j in self.xyz():
                    self._rep_ = self._rep_ + '\n%.7e %.7e %.7e' % j
                self._rep_ = self._rep_ + '\ntemperature, status'
                for j in self._Ts_:
                    self._rep_ = self._rep_ + '\n%.7f %.1f' % j
#                for j in self.txyz():
#                    self._rep_ = self._rep_ + '\n%.4f %.7e %.7e %.7e' % j
        return self._rep_
         
    # return true if this appears to be a oss raw acceleration packet
    def isOSSPacket(self):
        if 1074 != len(self.p): # all oss raw packets have the same length
            if 1084 != len(self.p): # unless they are extended by 10 bytes for ccsds time
                self._oss_ = 0
                return self._oss_
        try:
            self.time() # make sure time is really BCD compatible values
            self.extractPerPacketData() # might as well extract it now, maybe check for errors
            self._oss_ = 1
        except 'ValueError', value:
            t = UnixToHumanTime(time(), 1) + ' packet with bad time ignored'
            printLog(t)
            self._oss_ = 0
        except BCDConversionException, value:
            self._oss_ = 0
        return self._oss_
    
    # return header info in XML format for this packet
    def xmlHeader(self):
        if not self._xmlHeader_:
            self._xmlHeader_ = ''
            self._xmlHeader_ = self._xmlHeader_ + '\t<SensorID>%s</SensorID>\n' % self.name()
            self._xmlHeader_ = self._xmlHeader_ + '\t<TimeZero>%s</TimeZero>\n' % UnixToHumanTime(self.time())
            self._xmlHeader_ = self._xmlHeader_ + '\t<SampleRate>%s</SampleRate>\n' % self.rate()
            self._xmlHeader_ = self._xmlHeader_ + '\t<CutoffFreq>%s</CutoffFreq>\n' % 1
#            self._xmlHeader_ = self._xmlHeader_ + '\t<Gain>%s</Gain>\n' % 1
        return self._xmlHeader_
    
    # return header dictionary appropriate for this packet (everything except the accel data)
    def header(self):
        if not self._header_:
            self._header_['name'] = self.name()
            self._header_['isOSSPacket'] = self.isOSSPacket()
            self._header_['rate'] = self.rate()
            self._header_['time'] = self.time()
            self._header_['endTime'] = self.endTime()
        return self._header_

    def name(self):
        if not self._name_:
            self._name_ = 'ossraw'
        return self._name_

    def rate(self):
        if not self._rate_:
            self._rate_ = 10.0
        return self._rate_

    def time(self):
        if not self._time_:
            century = BCD(self.p[0])
            year =    BCD(self.p[1]) + 100*century
            month =   BCD(self.p[2])
            day =     BCD(self.p[3])
            hour =    BCD(self.p[4])
            minute =  BCD(self.p[5])
            second =  BCD(self.p[6])
            millisec = struct.unpack('h', self.p[8:10])[0]
            millisec = millisec & 0xffff
            self._time_ = HumanToUnixTime(month, day, year, hour, minute, second, millisec/1000.0)
        return self._time_
    
    def endTime(self):
        if not self._endTime_:
            # all oss-raw packets have 160 samples
            self._endTime_ = self.time() + 159.0 / self.rate() 
        return self._endTime_

    def samples(self): # all oss-raw packets have 160 samples
        if not self._samples_:
            self._samples_ = 160
        return self._samples_

    def extractPerPacketData(self):
        temperatureBytes = struct.unpack('h', self.p[10:12])[0]
        temperatureBytes = temperatureBytes & 0xffff
        self._temperature_ = (32768 - temperatureBytes) * (20.0/65536.0) * 20.0 - 17.8

    def txyz(self):
        if not self._txyz_:
            if not self._temperature_:
                self.extractPerPacketData()
            dt = 1.0/self.rate()
            begin = 50
            for s in range(16):
                sstart = begin + s*64
                dataStatus, rangeStatus, gimbalStatus = struct.unpack('BxBB', self.p[sstart:sstart+4])
                status = ((dataStatus<<16) + (rangeStatus<<8) + gimbalStatus) * 1.0 # pack and convert to float
                
                if rangeStatus & 0x03 == 0: #range A
                    zRange = 2500
                elif rangeStatus & 0x03 == 1: #range B
                    zRange = 197
                elif rangeStatus & 0x03 == 2: #range C
                    zRange = 15
                else:
                    raise 'rangeStatus value out of range'
                rangeStatus = rangeStatus >> 2
                if rangeStatus & 0x03 == 0: #range A
                    yRange = 2500
                elif rangeStatus & 0x03 == 1: #range B
                    yRange = 197
                elif rangeStatus & 0x03 == 2: #range C
                    yRange = 15
                else:
                    raise 'rangeStatus value out of range'
                rangeStatus = rangeStatus >> 2
                if rangeStatus & 0x03 == 0: #range A
                    xRange = 1000
                elif rangeStatus & 0x03 == 1: #range B
                    xRange = 100
                elif rangeStatus & 0x03 == 2: #range C
                    xRange = 10
                else:
                    raise 'rangeStatus value out of range'                

                x_coeff = ((20.0 / 65536.0) * xRange) / 1000000.0
                y_coeff = ((20.0 / 65536.0) * yRange) / 1000000.0
                z_coeff = ((20.0 / 65536.0) * zRange) / 1000000.0

                for i in range(10):
                    start = sstart + 4 + i*6
                    stop = start+6
                    x, y, z = struct.unpack('hhh', self.p[start:stop])
                    x = x & 0xffff
                    y = y & 0xffff
                    z = z & 0xffff
                    x = (32768.0 - x) * x_coeff
                    y = (32768.0 - y) * y_coeff
                    z = (32768.0 - z) * z_coeff
                    t = (s*10+i)*dt
                    self._txyz_.append((t, x, y, z))
                    self._Ts_.append((self._temperature_, status))
        return self._txyz_

    def xyz(self):
        if not self._xyz_:
            if not self._temperature_:
                self.extractPerPacketData()
            begin = 50
            #print self.time()
            for s in range(16):
                sstart = begin + s*64
                dataStatus, rangeStatus, gimbalStatus = struct.unpack('BxBB', self.p[sstart:sstart+4])
                #print '-------------------------'
                #print sstart,sstart+4
                #print dataStatus,rangeStatus,gimbalStatus
                status = ((dataStatus<<16) + (rangeStatus<<8) + gimbalStatus) * 1.0 # pack and convert to float
                #print status
                
                if rangeStatus & 0x03 == 0: #range A
                    zRange = 2500
                elif rangeStatus & 0x03 == 1: #range B
                    zRange = 197
                elif rangeStatus & 0x03 == 2: #range C
                    zRange = 15
                else:
                    raise 'rangeStatus value out of range'
                rangeStatus = rangeStatus >> 2
                if rangeStatus & 0x03 == 0: #range A
                    yRange = 2500
                elif rangeStatus & 0x03 == 1: #range B
                    yRange = 197
                elif rangeStatus & 0x03 == 2: #range C
                    yRange = 15
                else:
                    raise 'rangeStatus value out of range'
                rangeStatus = rangeStatus >> 2
                if rangeStatus & 0x03 == 0: #range A
                    xRange = 1000
                elif rangeStatus & 0x03 == 1: #range B
                    xRange = 100
                elif rangeStatus & 0x03 == 2: #range C
                    xRange = 10
                else:
                    raise 'rangeStatus value out of range'                

                x_coeff = ((20.0 / 65536.0) * xRange) / 1000000.0
                y_coeff = ((20.0 / 65536.0) * yRange) / 1000000.0
                z_coeff = ((20.0 / 65536.0) * zRange) / 1000000.0
                #print '-------------------------'

                for i in range(10):
                    start = sstart + 4 + i*6
                    stop = start+6
                    x, y, z = struct.unpack('hhh', self.p[start:stop])
                    x = x & 0xffff
                    y = y & 0xffff
                    z = z & 0xffff
                    #print start,stop, x,y,z
                    x = (32768.0 - x) * x_coeff
                    y = (32768.0 - y) * y_coeff
                    z = (32768.0 - z) * z_coeff
                    #print x,y,z
                    self._xyz_.append((x, y, z))
                    self._Ts_.append((self._temperature_, status))
        return self._xyz_
    
    def extraColumns(self):
        return self._Ts_
    
###############################################################################
class oare(accelPacket): # similar to oss, but everything is in a different place
    # packets don't change, so we can cache all the calculated values for reuse
    def __init__(self, packet, showWarnings=0):
        accelPacket.__init__(self, packet)
        self._showWarnings_ = showWarnings
        self._oare_ = None
        if not self.isOAREPacket():
            raise WrongTypeOfPacket
        self.type = 'mams_accel_oare'
        self._name_ = None
        self._rate_ = 10.0
        self._header_ = {}
        self._samples_ = None
        self._time_ = None
        self._endTime_ = None
        self._temperature_ = None
        self._Ts_ = []
        self._xyz_ = []
        self._txyz_ = []
        self._xmlHeader_ = None

    # print a representation of this packet
    def dump(self, accelData=0):
        if not self._rep_:
            header = self.header()
            hkeys = header.keys()
            className = split(str(self.__class__), '.')[1]
            self._rep_ = '%s(' % className
            for i in hkeys:
                if i == 'time' or i == 'endTime': # work around Python 3 decimal place default for times
                    self._rep_ = self._rep_ + ' %s:%.4f' % (i, header[i])
                else:
                    self._rep_ = self._rep_ + ' %s:%s' % (i, header[i])
            if accelData:
                self._rep_ = self._rep_ + '\ndata:'
                for j in self.xyz():
                    self._rep_ = self._rep_ + '\n%.7e %.7e %.7e' % j
                self._rep_ = self._rep_ + '\ntemperature, status'
                for j in self._Ts_:
                    self._rep_ = self._rep_ + '\n%.7f %.1f' % j
        return self._rep_

    # return true if this appears to be a oare raw acceleration packet
    def isOAREPacket(self):
        if 75 != len(self.p): # all oare raw packets have the same length
            self._oare_ = 0
            return self._oare_
        try:
            self.time() # make sure time is really BCD compatible values
            self.extractPerPacketData() # might as well extract it now, maybe check for errors
            self._oare_ = 1
        except 'ValueError', value:
            t = UnixToHumanTime(time(), 1) + ' packet with bad time ignored'
            printLog(t)
            self._oare_ = 0
        except BCDConversionException, value:
            self._oare_ = 0
        return self._oare_

    # return header info in XML format for this packet
    def xmlHeader(self):
        if not self._xmlHeader_:
            self._xmlHeader_ = ''
            self._xmlHeader_ = self._xmlHeader_ + '\t<SensorID>%s</SensorID>\n' % self.name()
            self._xmlHeader_ = self._xmlHeader_ + '\t<TimeZero>%s</TimeZero>\n' % UnixToHumanTime(self.time())
            self._xmlHeader_ = self._xmlHeader_ + '\t<SampleRate>%s</SampleRate>\n' % self.rate()
            self._xmlHeader_ = self._xmlHeader_ + '\t<CutoffFreq>%s</CutoffFreq>\n' % 1
        return self._xmlHeader_

    # return header dictionary appropriate for this packet (everything except the accel data)
    def header(self):
        if not self._header_:
            self._header_['name'] = self.name()
            self._header_['isOAREPacket'] = self.isOAREPacket()
            self._header_['rate'] = self.rate()
            self._header_['time'] = self.time()
            self._header_['endTime'] = self.endTime()
        return self._header_

    def name(self):
        if not self._name_:
            self._name_ = 'oare'
        return self._name_

    def rate(self):
        if not self._rate_:
            self._rate_ = 10.0
        return self._rate_

    def time(self):
        if not self._time_:
            century = BCD(self.p[0])
            year =    BCD(self.p[1]) + 100*century
            month =   BCD(self.p[2])
            day =     BCD(self.p[3])
            hour =    BCD(self.p[4])
            minute =  BCD(self.p[5])
            second =  BCD(self.p[6])
            millisec = struct.unpack('h', self.p[8:10])[0]
            millisec = millisec & 0xffff
            self._time_ = HumanToUnixTime(month, day, year, hour, minute, second, millisec/1000.0)
        return self._time_

    def endTime(self):
        if not self._endTime_:
            # all oare packets have 10 samples
            self._endTime_ = self.time() + 9.0 / self.rate()
        return self._endTime_

    def samples(self): # all oare packets have 10 samples
        if not self._samples_:
            self._samples_ = 10
        return self._samples_

    def extractPerPacketData(self):
        temperatureBytes = struct.unpack('h', self.p[70:72])[0]
        temperatureBytes = temperatureBytes & 0xffff
        self._temperature_ = (32768 - temperatureBytes) * (20.0/65536.0) * 20.0 - 17.8
        self.dataStatus, self.rangeStatus, self.gimbalStatus = struct.unpack('BBB', self.p[72:75])

    def txyz(self):
        if not self._txyz_:
            if not self._temperature_:
                self.extractPerPacketData()
            dt = 1.0/self.rate()
            sstart = 10
            status = ((self.dataStatus<<16) + (self.rangeStatus<<8) + self.gimbalStatus) * 1.0 # pack and convert to float

            if self.rangeStatus & 0x03 == 0: #range A
                zRange = 2500
            elif self.rangeStatus & 0x03 == 1: #range B
                zRange = 197
            elif self.rangeStatus & 0x03 == 2: #range C
                zRange = 15
            else:
                raise 'rangeStatus value out of range %s' % (self.rangeStatus & 0x03)
            self.rangeStatus = self.rangeStatus >> 2
            if self.rangeStatus & 0x03 == 0: #range A
                yRange = 2500
            elif self.rangeStatus & 0x03 == 1: #range B
                yRange = 197
            elif self.rangeStatus & 0x03 == 2: #range C
                yRange = 15
            else:
                raise 'rangeStatus value out of range'
            self.rangeStatus = self.rangeStatus >> 2
            if self.rangeStatus & 0x03 == 0: #range A
                xRange = 1000
            elif self.rangeStatus & 0x03 == 1: #range B
                xRange = 100
            elif self.rangeStatus & 0x03 == 2: #range C
                xRange = 10
            else:
                raise 'rangeStatus value out of range'

            x_coeff = ((20.0 / 65536.0) * xRange) / 1000000.0
            y_coeff = ((20.0 / 65536.0) * yRange) / 1000000.0
            z_coeff = ((20.0 / 65536.0) * zRange) / 1000000.0

            for i in range(10):
                start = sstart + i*6
                stop = start+6
                x, y, z = struct.unpack('hhh', self.p[start:stop])
                x = x & 0xffff
                y = y & 0xffff
                z = z & 0xffff
                x = (32768.0 - x) * x_coeff
                y = (32768.0 - y) * y_coeff
                z = (32768.0 - z) * z_coeff
                t = i*dt
                self._txyz_.append((t, x, y, z))
                self._Ts_.append((self._temperature_, status))
        return self._txyz_

    def xyz(self):
        if not self._xyz_:
            if not self._temperature_:
                self.extractPerPacketData()
            sstart = 10
            status = ((self.dataStatus<<16) + (self.rangeStatus<<8) + self.gimbalStatus) * 1.0 # pack and convert to float

            if self.rangeStatus & 0x03 == 0: #range A
                zRange = 2500
            elif self.rangeStatus & 0x03 == 1: #range B
                zRange = 197
            elif self.rangeStatus & 0x03 == 2: #range C
                zRange = 15
            else:
                raise 'rangeStatus value out of range'
            self.rangeStatus = self.rangeStatus >> 2
            if self.rangeStatus & 0x03 == 0: #range A
                yRange = 2500
            elif self.rangeStatus & 0x03 == 1: #range B
                yRange = 197
            elif self.rangeStatus & 0x03 == 2: #range C
                yRange = 15
            else:
                raise 'rangeStatus value out of range'
            self.rangeStatus = self.rangeStatus >> 2
            if self.rangeStatus & 0x03 == 0: #range A
                xRange = 1000
            elif self.rangeStatus & 0x03 == 1: #range B
                xRange = 100
            elif self.rangeStatus & 0x03 == 2: #range C
                xRange = 10
            else:
                raise 'rangeStatus value out of range'

            x_coeff = ((20.0 / 65536.0) * xRange) / 1000000.0
            y_coeff = ((20.0 / 65536.0) * yRange) / 1000000.0
            z_coeff = ((20.0 / 65536.0) * zRange) / 1000000.0

            for i in range(10):
                start = sstart + i*6
                stop = start+6
                x, y, z = struct.unpack('hhh', self.p[start:stop])
                x = x & 0xffff
                y = y & 0xffff
                z = z & 0xffff
                x = (32768.0 - x) * x_coeff
                y = (32768.0 - y) * y_coeff
                z = (32768.0 - z) * z_coeff
                self._xyz_.append((x, y, z))
                self._Ts_.append((self._temperature_, status))
        return self._xyz_

    def extraColumns(self):
        return self._Ts_
   
###############################################################################    
class artificial(accelPacket):
    def __init__(self, packet, showWarnings=0):
        accelPacket.__init__(self, packet)
        self._showWarnings_ = showWarnings
        self._artificial_ = None
        if not self.isArtificialPacket():
            raise WrongTypeOfPacket
        self.type = 'artificial'
        self._name_ = 'Artificial'
        self._deviceId_ = None
        self._rate_ = None
        self._samples_ = None
        self._measurementsPerSample_ = None
        self._dataOffset_ = None
        self._header_ = {}
        self._time_ = None
        self._endTime_ = None
        self._xyz_ = []
        self._txyz_ = []
        self._xmlHeader_ = None

    # return true if this appears to be an artificial packet
    def isArtificialPacket(self):
        if 32 > len(self.p): # minimum length 
            self._artificial_ = 0
            return self._artificial_
        byte0 = struct.unpack('c', self.p[0])[0]
        byte1 = struct.unpack('c', self.p[1])[0]
        if not (byte0 == chr(0xfa) and byte1 == chr(0xce)):
            self._artificial_ = 0
            return self._artificial_
        self._artificial_ = 1
        return self._artificial_
    
    # return header info in XML format for this packet
    def xmlHeader(self):
        if not self._xmlHeader_:
            self._xmlHeader_ = ''
            self._xmlHeader_ = self._xmlHeader_ + '\t<SensorID>%s</SensorID>\n' % self.name()
            self._xmlHeader_ = self._xmlHeader_ + '\t<TimeZero>%s</TimeZero>\n' % self.time()
            self._xmlHeader_ = self._xmlHeader_ + '\t<SampleRate>%s</SampleRate>\n' % self.rate()
        return self._xmlHeader_
    
    # return header dictionary appropriate for this packet (everything except the accel data)
    def header(self):
        if not self._header_:
            self._header_['name'] = self.name()
            self._header_['isArtificialPacket'] = self.isArtificialPacket()
            self._header_['rate'] = self.rate()
            self._header_['time'] = self.time()
            self._header_['endTime'] = self.endTime()
            self._header_['samples'] = self.samples()
            self._header_['measurementsPerSample'] = self.measurementsPerSample()
            self._header_['deviceId'] = self.deviceId()
        return self._header_

    def name(self):
        if not self._name_:
            self._name_ = 'Artificial'
        return self._name_

    def deviceId(self):
        if not self._deviceId_:
            self._deviceId_ = ord(struct.unpack('c', self.p[3])[0])
        return self._deviceId_

    def rate(self):
        if not self._rate_:
            self._rate_ = struct.unpack('f', self.p[12:16])[0]
        return self._rate_

    def samples(self):
        if not self._samples_:
            self._samples_ = struct.unpack('i', self.p[16:20])[0]
        return self._samples_
    
    def measurementsPerSample(self):
        if not self._measurementsPerSample_:
            self._measurementsPerSample_ = struct.unpack('i', self.p[20:24])[0]
        return self._measurementsPerSample_
    
    def dataOffset(self):
        if not self._dataOffset_:
            self._dataOffset_ = struct.unpack('i', self.p[24:28])[0]
        return self._dataOffset_

    def time(self):
        if not self._time_:
            self._time_ = struct.unpack('d', self.p[4:12])[0]
        return self._time_
    
    def endTime(self):
        if not self._endTime_:
            if self.rate() == 0:
                self._endTime_ = self.time()
            else:
                self._endTime_ = self.time() + (self.samples() - 1) / self.rate() 
        return self._endTime_

    def xyz(self):
        if not self._xyz_:
            index = start = self.dataOffset()
            samples = self.samples()
            for i in range(samples):
                row = []
                for j in range(self.measurementsPerSample()):
                    x = struct.unpack('f', self.p[index:index+4])[0]
                    row.append(x)
                    index = index + 4                
                self._xyz_.append(row)
        return self._xyz_

    def txyz(self):
        if not self._txyz_:
            index = start = self.dataOffset()
            # rate = 0 means non-periodic, and implies only 1 sample per packet
            if self.rate() == 0 and self.samples() == 1:
                dt = 1 # does not matter
            else:
                dt = 1.0/self.rate()
            for i in range(self.samples()):
                t = i*dt
                row = [t]
                for j in range(self.measurementsPerSample()):
                    x = struct.unpack('f', self.p[index:index+4])[0]
                    row.append(x)
                    index = index + 4                
                self._txyz_.append(row) 
        return self._txyz_

    # print a representation of this packet
    def dump(self, accelData=0):
        if not self._rep_:
            header = self.header()
            hkeys = header.keys()
            className = split(str(self.__class__), '.')[1] 
            self._rep_ = '%s(' % className
            for i in hkeys:
                if i == 'time' or i == 'endTime': # work around Python 3 decimal place default for times
                    self._rep_ = self._rep_ + ' %s:%.4f' % (i, header[i])
                else:
                    self._rep_ = self._rep_ + ' %s:%s' % (i, header[i])
            if accelData:
                self._rep_ = self._rep_ + '\ndata:'
                for j in self.xyz():
                    self._rep_ = self._rep_ + '\n'
                    for k in j:
                        self._rep_ = self._rep_ + '%.7e ' % (k)
        return self._rep_
    
###############################################################################    
class besttmf(artificial):
    def __init__(self, packet, showWarnings=0):
        artificial.__init__(self, packet)
        self._showWarnings_ = showWarnings
        self._besttmf_ = None
        if not self.isBesttmfPacket():
            raise WrongTypeOfPacket
        self.type = 'mams_accel_ossbtmf'
        self._name_ = None

    # return true if this appears to be an besttmf packet
    def isBesttmfPacket(self):
        if not artificial.isArtificialPacket(self):
            self._besttmf_ = 0
            return self._besttmf_
        byte2 = struct.unpack('c', self.p[2])[0]
        if not byte2 == chr(0x01):
            self._besttmf_ = 0
            return self._besttmf_
        self._besttmf_ = 1
        return self._besttmf_
    
    def name(self):
        if not self._name_:
            self._name_ = 'ossbtmf'
        return self._name_
    
    # return header dictionary appropriate for this packet (everything except the accel data)
    def header(self):
        if not self._header_:
            self._header_['name'] = self.name()
            self._header_['isBesttmfPacket'] = self.isBesttmfPacket()
            self._header_['rate'] = self.rate()
            self._header_['time'] = self.time()
            self._header_['endTime'] = self.endTime()
            self._header_['samples'] = self.samples()
            self._header_['measurementsPerSample'] = self.measurementsPerSample()
            self._header_['deviceId'] = self.deviceId()
            self._header_['biasCoeff'] = '%.7e %.7e %.7e' % self.biasValues()
        return self._header_
    
    # return header info in XML format for this packet
    def xmlHeader(self):
        if not self._xmlHeader_:
            self._xmlHeader_ = ''
            self._xmlHeader_ = self._xmlHeader_ + '\t<SensorID>%s</SensorID>\n' % self.name()
            self._xmlHeader_ = self._xmlHeader_ + '\t<TimeZero>%s</TimeZero>\n' % self.time()
            self._xmlHeader_ = self._xmlHeader_ + '\t<SampleRate>%s</SampleRate>\n' % self.rate()
            self._xmlHeader_ = self._xmlHeader_ + '\t<CutoffFreq>%s</CutoffFreq>\n' % 0.01
            self._xmlHeader_ = self._xmlHeader_ + '\t<BiasCoeff x="%.7e" y="%.7e" z="%.7e"/>\n' % self.biasValues()
        return self._xmlHeader_

    def biasValues(self):
        # return the 3 bias values
        return struct.unpack('fff', self.p[28:40])
        
    # print a representation of this packet
    def dump(self, accelData=0):
        if not self._rep_:
            header = self.header()
            hkeys = header.keys()
            className = split(str(self.__class__), '.')[1] 
            self._rep_ = '%s(' % className
            for i in hkeys:
                if i == 'time' or i == 'endTime': # work around Python 3 decimal place default for times
                    self._rep_ = self._rep_ + ' %s:%.4f' % (i, header[i])
                else:
                    self._rep_ = self._rep_ + ' %s:%s' % (i, header[i])
            if accelData:
                self._rep_ = self._rep_ + '\ndata:'
                for j in self.xyz():
                    self._rep_ = self._rep_ + '\n%.7e %.7e %.7e' % tuple(j)
        return self._rep_
  
###############################################################################    
class finaltmf(artificial):
    def __init__(self, packet, showWarnings=0):
        artificial.__init__(self, packet)
        self._showWarnings_ = showWarnings
        self._finaltmf_ = None
        if not self.isFinaltmfPacket():
            raise WrongTypeOfPacket
        self.type = 'mams_accel_ossftmf'
        self._name_ = None

    # return true if this appears to be an finaltmf packet
    def isFinaltmfPacket(self):
        if not artificial.isArtificialPacket(self):
            self._finaltmf_ = 0
            return self._finaltmf_
        byte2 = struct.unpack('c', self.p[2])[0]
        if not byte2 == chr(0x02):
            self._finaltmf_ = 0
            return self._finaltmf_
        self._finaltmf_ = 1
        return self._finaltmf_
    
    def name(self):
        if not self._name_:
            self._name_ = 'ossftmf'
        return self._name_
    
    # return header dictionary appropriate for this packet (everything except the accel data)
    def header(self):
        if not self._header_:
            self._header_['name'] = self.name()
            self._header_['isFinaltmfPacket'] = self.isFinaltmfPacket()
            self._header_['rate'] = self.rate()
            self._header_['time'] = self.time()
            self._header_['endTime'] = self.endTime()
            self._header_['samples'] = self.samples()
            self._header_['measurementsPerSample'] = self.measurementsPerSample()
            self._header_['deviceId'] = self.deviceId()
        return self._header_  
   
###############################################################################    
class finalbias(artificial):
    def __init__(self, packet, showWarnings=0):
        artificial.__init__(self, packet)
        self._showWarnings_ = showWarnings
        self._finalbias_ = None
        if not self.isFinalbiasPacket():
            raise WrongTypeOfPacket
        self.type = 'mams_accel_ossfbias'
        self._name_ = None

    # return true if this appears to be an finalbias packet
    def isFinalbiasPacket(self):
        if not artificial.isArtificialPacket(self):
            self._finalbias_ = 0
            return self._finalbias_
        byte2 = struct.unpack('c', self.p[2])[0]
        if not byte2 == chr(0x03):
            self._finalbias_ = 0
            return self._finalbias_
        self._finalbias_ = 1
        return self._finalbias_
    
    def name(self):
        if not self._name_:
            self._name_ = 'ossfbias'
        return self._name_
    
    # return header dictionary appropriate for this packet (everything except the accel data)
    def header(self):
        if not self._header_:
            self._header_['name'] = self.name()
            self._header_['isFinalbiasPacket'] = self.isFinalbiasPacket()
            self._header_['rate'] = self.rate()
            self._header_['time'] = self.time()
            self._header_['endTime'] = self.endTime()
            self._header_['samples'] = self.samples()
            self._header_['measurementsPerSample'] = self.measurementsPerSample()
            self._header_['deviceId'] = self.deviceId()
        return self._header_
    
###############################################################################    
class radgse(artificial):
    def __init__(self, packet, showWarnings=0):
        artificial.__init__(self, packet)
        self._showWarnings_ = showWarnings
        self._radgse_ = None
        if not self.isRadgsePacket():
            raise WrongTypeOfPacket
        self.type = 'iss_rad'
        self._name_ = None

    # return true if this appears to be an finalbias packet
    def isRadgsePacket(self):
        if not artificial.isArtificialPacket(self):
            self._radgse_ = 0
            return self._radgse_
        byte2 = struct.unpack('c', self.p[2])[0]
        if not byte2 == chr(0x04):
            self._radgse_ = 0
            return self._radgse_
        self._radgse_ = 1
        return self._radgse_
    
    def name(self):
        if not self._name_:
            self._name_ = 'radgse'
        return self._name_
    
    def dataDirName(self):
        return 'iss_rad_radgse'
    
    # return header dictionary appropriate for this packet (everything except the accel data)
    def header(self):
        if not self._header_:
            self._header_['name'] = self.name()
            self._header_['isRadgsePacket'] = self.isRadgsePacket()
            self._header_['rate'] = self.rate()
            self._header_['time'] = self.time()
            self._header_['endTime'] = self.endTime()
            self._header_['samples'] = self.samples()
            self._header_['measurementsPerSample'] = self.measurementsPerSample()
            self._header_['deviceId'] = self.deviceId()
        return self._header_
    
    # return header info in XML format for this packet
    def xmlHeader(self):
        if not self._xmlHeader_:
            self._xmlHeader_ = ''
            self._xmlHeader_ = self._xmlHeader_ + '\t<SensorID>%s</SensorID>\n' % self.name()
            self._xmlHeader_ = self._xmlHeader_ + '\t<TimeZero>%s</TimeZero>\n' % self.time()
            self._xmlHeader_ = self._xmlHeader_ + '\t<SampleRate>%s</SampleRate>\n' % self.rate()
            self._xmlHeader_ = self._xmlHeader_ + '\t<CutoffFreq>%s</CutoffFreq>\n' % 1.0
        return self._xmlHeader_
     
###############################################################################    
class samsff(artificial):
    def __init__(self, packet, showWarnings=0):
        artificial.__init__(self, packet)
        self._showWarnings_ = showWarnings
        self._samsff_ = None
        if not self.isSamsffPacket():
            raise WrongTypeOfPacket
        self.type = 'samsff_accel'
        self._name_ = None

    # return true if this appears to be an samsff packet
    def isSamsffPacket(self):
        if not artificial.isArtificialPacket(self):
            self._samsff_ = 0
            return self._samsff_
        byte2 = struct.unpack('c', self.p[2])[0]
        if not byte2 == chr(0x05):
            self._samsff_ = 0
            return self._samsff_
        self._samsff_ = 1
        return self._samsff_
    
    def name(self):
        if not self._name_:
            self._name_ = 'samsff%02d' % self.deviceId()
        return self._name_
    
    def dataDirName(self):
        return 'samsff_accel_samsff%02d' % self.deviceId()

    # return header info in XML format for this packet
    def xmlHeader(self):
        if not self._xmlHeader_:
            self._xmlHeader_ = ''
            self._xmlHeader_ = self._xmlHeader_ + '\t<SensorID>%s</SensorID>\n' % self.name()
            self._xmlHeader_ = self._xmlHeader_ + '\t<TimeZero>%s</TimeZero>\n' % self.time()
            self._xmlHeader_ = self._xmlHeader_ + '\t<SampleRate>%s</SampleRate>\n' % self.rate()
            self._xmlHeader_ = self._xmlHeader_ + '\t<CutoffFreq>%s</CutoffFreq>\n' % (self.rate()/3.8)
        return self._xmlHeader_

    # return header dictionary appropriate for this packet (everything except the accel data)
    def header(self):
        if not self._header_:
            self._header_['name'] = self.name()
            self._header_['isSamsffPacket'] = self.isSamsffPacket()
            self._header_['rate'] = self.rate()
            self._header_['time'] = self.time()
            self._header_['endTime'] = self.endTime()
            self._header_['samples'] = self.samples()
            self._header_['measurementsPerSample'] = self.measurementsPerSample()
            self._header_['deviceId'] = self.deviceId()
        return self._header_
       
###############################################################################    
class hirap(accelPacket):
    # packets don't change, so we can cache all the calculated values for reuse
    def __init__(self, packet, showWarnings=0):
        accelPacket.__init__(self, packet)
        self._showWarnings_ = showWarnings
        self._hirap_ = None
        if not self.isHirapPacket():
            raise WrongTypeOfPacket
        self.type = 'mams_accel_hirap'
        self._name_ = 'hirap'
        self._rate_ = 1000.0
        self._samples_ = 192 # all hirap packets have 192 samples
        self._header_ = {}
        self._time_ = None
        self._endTime_ = None
        self._xyz_ = []
        self._txyz_ = []
        self._xmlHeader_ = None
            
    # return true if this appears to be a hirap acceleration packet
    def isHirapPacket(self):
        if 1172 != len(self.p): # all Hirap packets have the same length
            self._hirap_ = 0
            return self._hirap_
        try:
            self.time() # make sure time is really BCD compatible values
            self._hirap_ = 1
        except 'ValueError', value:
            t = UnixToHumanTime(time(), 1) + ' packet with bad time ignored'
            printLog(t)
            self._oss_ = 0
        except BCDConversionException, value:
            self._hirap_ = 0
        return self._hirap_
    
    # return header info in XML format for this packet
    def xmlHeader(self):
        if not self._xmlHeader_:
            self._xmlHeader_ = ''
            self._xmlHeader_ = self._xmlHeader_ + '\t<SensorID>%s</SensorID>\n' % self.name()
            self._xmlHeader_ = self._xmlHeader_ + '\t<TimeZero>%s</TimeZero>\n' % UnixToHumanTime(self.time())
            self._xmlHeader_ = self._xmlHeader_ + '\t<SampleRate>%s</SampleRate>\n' % self.rate()
            self._xmlHeader_ = self._xmlHeader_ + '\t<CutoffFreq>%s</CutoffFreq>\n' % 100
            self._xmlHeader_ = self._xmlHeader_ + '\t<Gain>%s</Gain>\n' % 1
        return self._xmlHeader_
    
    # return header dictionary appropriate for this packet (everything except the accel data)
    def header(self):
        if not self._header_:
            self._header_['name'] = self.name()
            self._header_['isHirapPacket'] = self.isHirapPacket()
            self._header_['rate'] = self.rate()
            self._header_['time'] = self.time()
            self._header_['endTime'] = self.endTime()
        return self._header_

    def name(self):
        if not self._name_:
            self._name_ = 'osshirap'
        return self._name_

    def rate(self):
        if not self._rate_:
            self._rate_ = 1000.0
        return self._rate_

    def time(self):
        if not self._time_:
            century = BCD(self.p[0])
            year =    BCD(self.p[1]) + 100*century
            month =   BCD(self.p[2])
            day =     BCD(self.p[3])
            hour =    BCD(self.p[4])
            minute =  BCD(self.p[5])
            second =  BCD(self.p[6])
            millisec = struct.unpack('h', self.p[8:10])[0]
            millisec = millisec & 0xffff
            self._time_ = HumanToUnixTime(month, day, year, hour, minute, second, millisec/1000.0)
        return self._time_
    
    def endTime(self):
        if not self._endTime_:
            # all hirap packets have 192 samples
            self._endTime_ = self.time() + (self.samples() - 1.0) / self.rate() 
        return self._endTime_

    def samples(self): 
        if not self._samples_:
            self._samples_ = 192.0
        return self._samples_

    def xyz(self):
        if not self._xyz_:
            for i in range(192):
                start = 20+6*i
                stop = start+6
                x, y, z = struct.unpack('hhh', self.p[start:stop])
                #if i < 3:
                #  print x,y,z
                self._xyz_.append((x/2048000.0, y/2048000.0, z/2048000.0)) # 16 / 32768 / 1000= 1/2048000
        return self._xyz_

    def txyz(self):
        if not self._txyz_:
            dt = 1.0/self.rate()
            for i in range(192):
                start = 20+6*i
                stop = start+6
                x, y, z = struct.unpack('hhh', self.p[start:stop])
                t = i*dt
                self._txyz_.append((t, x/2048000.0, y/2048000.0, z/2048000.0)) # 16 / 32768 / 1000= 1/2048000
        return self._txyz_
   
###############################################################################    
class sams2Packet(accelPacket):
    # packets don't change, so we can cache all the calculated values for reuse
    def __init__(self, packet, showWarnings=0):
        accelPacket.__init__(self, packet)
        self._showWarnings_ = showWarnings
        self._sams2_ = None
        self._samples_ = None
        self._adjustment_ = None
        if not self.isSams2Packet():
            raise WrongTypeOfPacket
        self.type = 'sams2_accel'
        self._name_ = None
        self._header_ = {}
        self._eeId_ = None
        self._seId_ = None
        self._head_ = None
        self._status_ = None
        self._rate_ = None
        self._gain_ = None
        self._unit_ = None
        self._time_ = None
        self._endTime_ = None
        self._xyz_ = []
        self._txyz_ = []
        self._xmlHeader_ = None
        
    def dataDirName(self):
        return 'sams2_accel_' + self.seId()

    def measurementsPerSample(self):
        return 3 

    # return true if this packet is contiguous with the supplied packet
    # sams-ii packets vary in size, we need to correctly catch a missing minimum size packet
    # every half second, packets of the following sizes are sent:
    #     at   62.5 Hz: 32 or 31
    #     at  125   Hz: 63 or 62
    #     at  250   Hz: 74, 51
    #     at  500   Hz: 74, 74, 74, 28
    #     at 1000   Hz: 74, 74, 74, 74, 74, 74, 56
    def contiguous(self, other):
        minSamples = { 62.5:31, 125.0:62, 250.0:51, 500.0:28, 1000.0:56 }
        if not other:
#            print 'contiguous: no other'
            return 0
        if self.type != other.type: # maybe we should throw an exception here
#            print 'contiguous: other type mis-match'
            return 0
        if self.rate() != other.rate():
#            print 'contiguous: other rate mis-match'
            return 0
        if self._dqmIndicator_ != other._dqmIndicator_:
#            print 'contiguous: other dqm mis-match'
            return 0
        ostart = other.time()
        oend = other.endTime()
        start = self.time()
        if self.rate() == 0: # non-periodic data
#            print 'contiguous: OK non-periodic'
            return (start > oend)
        gap = start - oend
        allowAbleGap = minSamples[self.rate()]/self.rate()
        result =  (start >= ostart) and (gap <= allowAbleGap)
#        if not result:
#             print 'contiguous:%s ostart:%.4lf oend:%.4lf start:%.4lf gap:%.4lf' % (result, ostart, oend, start, gap) 
        return result

    # name of the database table this data should be in (no dashes)
    def name(self):
        if not self._name_:
             self._name_ = self.seId()
        return  self._name_

    # return true if this appears to be a sams2 acceleration packet
    def isSams2Packet(self): # struct.unpack doesn't seem to think 'h' is 2 bytes

        if not self._sams2_:
            if len(self.p) < 68:
                self._sams2_ = 0
                if self._showWarnings_:
                    t = 'SAMSII packet warning\n' + self.hexDump() + UnixToHumanTime(time(), 1) + '\n'  
                    t = t + ' packet too short (%s) to be a sams-ii acceleration packet' % len(self.p)
                    printLog(t)
                return self._sams2_
            byte0 = struct.unpack('c', self.p[0])[0]
            byte1 = struct.unpack('c', self.p[1])[0]
            if not (byte0 == chr(0xda) and byte1 == chr(0xbe)):
                self._sams2_ = 0
                if self._showWarnings_:
                    t = 'SAMSII packet warning\n' + self.hexDump() + UnixToHumanTime(time(), 1) + '\n'  
                    t = t + ' packet cannot be sams-ii accel because it does not start with 0xdabe'
                    printLog(t)
                return self._sams2_
            byte2 = struct.unpack('c', self.p[12])[0]
            byte3 = struct.unpack('c', self.p[13])[0]
            accelpacket = (byte2 == chr(100)) and (byte3 == chr(0))
            if not accelpacket and self._showWarnings_:
                self._sams2_ = 0
                t = 'SAMSII packet warning\n' + self.hexDump() + UnixToHumanTime(time(), 1) + '\n'  
                t = t + ' packet cannot be sams-ii accel because it does not have 0x6400 at offset 12'
                printLog(t)
                return self._sams2_
            if len(self.p) < 52+16*self.samples():
                self._sams2_ = 0
                t = 'SAMSII packet warning\n' + self.hexDump() + UnixToHumanTime(time(), 1) + '\n'  
                t = t + ' packet is not a complete sams-ii accel packet, %s samples are not present' % self.samples()
                printLog(t)
                return self._sams2_
            self._sams2_ = 1
            self.addAdditionalDQM(self.adjustment()) 
        return self._sams2_

    # return header info in XML format for this packet
    def xmlHeader(self):
        if not self._xmlHeader_:
            self._xmlHeader_ = ''
            self._xmlHeader_ = self._xmlHeader_ + '\t<SensorID>%s</SensorID>\n' % self.name()
            self._xmlHeader_ = self._xmlHeader_ + '\t<TimeZero>%s</TimeZero>\n' % UnixToHumanTime(self.time())
            self._xmlHeader_ = self._xmlHeader_ + '\t<Gain>%s</Gain>\n' % self.gain()
            #self._xmlHeader_ = self._xmlHeader_ + '\t<Units>%s</Units>\n' % self.unit()
            self._xmlHeader_ = self._xmlHeader_ + '\t<SampleRate>%s</SampleRate>\n' % self.rate()
            self._xmlHeader_ = self._xmlHeader_ + '\t<CutoffFreq>%s</CutoffFreq>\n' % (self.rate() * 0.4)
        return self._xmlHeader_
    
    # return header dictionary appropriate for this packet (everything except the accel data)
    def header(self):
        if not self._header_:
            self._header_['name'] = self.name()
            self._header_['eeId'] = self.eeId()
            self._header_['seId'] = self.seId()
            self._header_['head'] = self.head()
            self._header_['isSams2Packet'] = self.isSams2Packet()
            self._header_['status'] = self.status()
            self._header_['rate'] = self.rate()
            self._header_['gain'] = self.gain()
            self._header_['unit'] = self.unit()
            self._header_['adjustment'] = self.adjustment()
            self._header_['samples'] = self.samples()
            self._header_['time'] = self.time()
            self._header_['endTime'] = self.endTime()
        return self._header_
    
    def eeId(self):
        if not self._eeId_:
            self._eeId_ = self.p[16:24]
            self._eeId_ = replace(self._eeId_ , chr(0), '') # delete nulls
            self._eeId_ = join(split(self._eeId_, '-'), '') # delete dashes
        return self._eeId_
    
    def seId(self):
        if not self._seId_:
            self._seId_ = self.p[24:32]
            self._seId_ = replace(self._seId_ , chr(0), '') # delete nulls
            self._seId_ = join(split(self._seId_, '-'), '') # delete dashes
        return self._seId_
    
    def head(self):
        if not self._head_:
            self._head_ = struct.unpack('c', self.p[32])[0]
            self._head_ = (self._head_ == 1)
        return self._head_
    
    def status(self):
        if not self._status_:
            self._status_ = struct.unpack('I', self.p[44:48])[0]
        return self._status_

    def samples(self):
        if not self._samples_:
            self._samples_ = struct.unpack('i', self.p[48:52])[0]
        return self._samples_

    def rate(self):
        if not self._rate_:
            self._rate_ = struct.unpack('b', self.p[64])[0] & 0x07
            if self._showWarnings_: # check for mis-matched rate bytes
                for i in range(16, 161, 16): # check next 10 rate bytes
                    if 64+i >= len(self.p):
                        break
                    dupRate = struct.unpack('b', self.p[64+i])[0] & 0x07
                    if dupRate != self._rate_:
                        t = UnixToHumanTime(time(), 1) + '\n'  
                        t = t + ' mis-matched rate bytes, %s at offset 64 and %s at offset %s\n' % (self._rate_, dupRate, 64+i)
                        t = t + self.dump()
                        printLog(t)
                        break
            if (self._rate_ == 0):
                self._rate_ = 62.5
            elif (self._rate_ == 1):
                self._rate_ = 125.0
            elif (self._rate_ == 2): # will have to split packet for this rate and above
                self._rate_ = 250.0
            elif (self._rate_ == 3):
                self._rate_ = 500.0
            elif (self._rate_ == 4):
                self._rate_ = 1000.0
            else:
                if self._showWarnings_:
                    t = '\n' + self.hexDump()
                    t = t + '\n' +  self.dump()
                    t = t + '\n' +  UnixToHumanTime(time(), 1),  
                    t = t + '\n' +  ' bogusRateByte: %s at time %.4f, assuming rate=1000' % (self._rate_, self.time())
                    printLog(t)
                self._rate_ = 1000.0
        return self._rate_
    
    def gain(self):
        if not self._gain_:
            self._gain_ = (struct.unpack('b', self.p[64])[0] & 0x18 ) >> 3
            if (self._gain_ == 0):
                self._gain_ = 1.0
            elif (self._gain_ == 1):
                self._gain_ = 10.0
            elif (self._gain_ == 2):
                self._gain_ = 100.0
            elif (self._gain_ == 3):
                self._gain_ = 1000.0
            else:
                if self._showWarnings_:
                    t = '\n' + self.hexDump()
                    t = t + '\n' +  self.dump()
                    t = t + '\n' +  UnixToHumanTime(time(), 1),  
                    t = t + '\n' +  ' bogusGainByte: %s at time %.4f, assuming gain=1' % (self._gain_, self.time())
                    printLog(t)
                self._gain_ = 1.0
        return self._gain_

    def unit(self):
        if not self._unit_:
            self._unit_ = (struct.unpack('b', self.p[65])[0] )
            if (self._unit_ == 1):
                self._unit_ = 'counts'
            elif (self._unit_ == 2):
                self._unit_ = 'volts'
            elif (self._unit_ == 3):
                self._unit_ = 'g'
            else:
                if self._showWarnings_:
                    t = '\n' + self.hexDump()
                    t = t + '\n' +  self.dump()
                    t = t + '\n' +  UnixToHumanTime(time(), 1),  
                    t = t + '\n' +  ' bogusUnitByte: %s at time %.4f, assuming unit=ug' % (self._unit_, self.time())
                    printLog(t)
                self._unit_ = 'ug'
        return self._unit_

    def adjustment(self):
        if not self._adjustment_:
            a = (struct.unpack('b', self.p[66])[0] )
            self._dqmIndicator_ = a & 0x07
            self._adjustment_ = ''
            if (a & 0x01 == 1):
                self._adjustment_ = 'temperature'
            if (a & 0x02 == 2):
                if self._adjustment_:
                    self._adjustment_ = self._adjustment_ + '+'
                self._adjustment_ = self._adjustment_ + 'gain'
            if (a & 0x04 == 4):
                if self._adjustment_:
                    self._adjustment_ = self._adjustment_ + '+'
                self._adjustment_ = self._adjustment_ + 'axial-mis-alignment'
            if (a & 0x07 == 0):
                self._adjustment_ = 'no-adjustments'
            if a > 7:
                if self._showWarnings_:
                    t = '\n' + self.hexDump()
                    t = t + '\n' +  self.dump()
                    t = t + '\n' +  UnixToHumanTime(time(), 1),  
                    t = t + '\n' +  ' bogusAdjustmentByte: %s at time %.4f, ignoring' % (a, self.time())
                    printLog(t)
        return self._adjustment_

    def time(self):
        if not self._time_:
            sec, usec = struct.unpack('II', self.p[36:44])
            self._time_ = sec + usec/1000000.0
        return self._time_
    
    def endTime(self):
        if not self._endTime_:
            self._endTime_ = self.time() + (self.samples()-1) / self.rate() 
        return self._endTime_

    def xyz(self):
        if not self._xyz_:
            convert = 0
            if self.unit() != 'g':
                convert = 1
                if self.unit() == 'volts':
                    m = 1.0/3.89791388
                    b = 0
                else: # must be counts
                    if self.gain() == 1.0:
                        m = 2.18538e-07
                        b = -0.026280804
                    elif self.gain() == 10.0:
                        m = 2.18538e-08
                        b = -0.00262381
                    elif self.gain() == 100.0:
                        m = 2.18538e-09
                        b = -0.00026280804
                    elif self.gain() == 1000.0:
                        m = 2.18538e-10
                        b = -0.000026280804
            for i in range(self.samples()):
                start = 52+16*i
                stop = start+16
                x, y, z, j = struct.unpack('fffI', self.p[start:stop])
                if convert:
                    x, y, z = x*m+b, y*m+b, z*m+b
                self._xyz_.append((x,y,z))
        return self._xyz_
    
    def txyz(self):
        if not self._txyz_:
            dt = 1.0/self.rate()
            convert = 0
            if self.unit() != 'g':
                convert = 1
                if self.unit() == 'volts':
                    m = 1.0/3.89791388
                    b = 0
                else: # must be counts
                    if self.gain() == 1.0:
                        m = 2.18538e-07
                        b = -0.026280804
                    elif self.gain() == 10.0:
                        m = 2.18538e-08
                        b = -0.00262381
                    elif self.gain() == 100.0:
                        m = 2.18538e-09
                        b = -0.00026280804
                    elif self.gain() == 1000.0:
                        m = 2.18538e-10
                        b = -0.000026280804
            for i in range(self.samples()):
                start = 52+16*i
                stop = start+16
                x, y, z, j = struct.unpack('fffI', self.p[start:stop])
                if convert:
                    x, y, z = x*m+b, y*m+b, z*m+b
                t = i*dt
                self._txyz_.append((t,x,y,z))
        return self._txyz_
    
###############################################################################   
class samsTshEs(accelPacket):
    # packets don't change, so we can cache all the calculated values for reuse
    def __init__(self, packet, showWarnings=0):
        accelPacket.__init__(self, packet)
        self._showWarnings_ = showWarnings
        self._samsTshEs_ = None
        self._samples_ = None
        self._adjustment_ = None
        self._status_ = None
        if not self.isSamsTshEsPacket():
            raise WrongTypeOfPacket
        self.type = 'samses_accel'
        self._name_ = None
        self._header_ = {}
        self._Id_ = None
        self._head_ = None
        self._rate_ = None
        self._gain_ = None
        self._unit_ = None
        self._adjustment_ = None
        self._time_ = None
        self._endTime_ = None
        self._xyz_ = []
        self._txyz_ = []
        self._xmlHeader_ = None
        self._cutoffFreq_ = None
        
    def dataDirName(self):
        return 'samses_accel_' + self.Id()

    def measurementsPerSample(self):
        return 3 # what about 'something interesting happened' bit?

    # return true if this packet is contiguous with the supplied packet
    def contiguous(self, other): 
        if not other:
#            print 'contiguous: no other'
            return 0
        if self.type != other.type: # maybe we should throw an exception here
#            print 'contiguous: other type mis-match'
            return 0
        if self.rate() != other.rate():
#            print 'contiguous: other rate mis-match'
            return 0
        if self._dqmIndicator_ != other._dqmIndicator_:
#            print 'contiguous: other dqm mis-match'
            return 0
        ostart = other.time()
        oend = other.endTime()
        start = self.time()
        if self.rate() == 0: # non-periodic data
#            print 'contiguous: OK non-periodic'
            return (start > oend)
        #### during testing, all tsh-es packets are maximum size and very regular
        #### on orbit, theu will be broken into multiple smaller packets of unknown size
        #### once we know the correct sizes, minSamples should be reduced
        minSamples = { 1000.:512, 500.0:512, 250.0:256, 125.0:128, 62.5:64, 31.25:64, 15.625:64, 7.8125:32 }
        gap = start - oend
        allowAbleGap = minSamples[self.rate()]/self.rate()
        result =  (start >= ostart) and (gap <= allowAbleGap)
#        if not result:
#             print 'contiguous:%s ostart:%.4lf oend:%.4lf start:%.4lf gap:%.4lf' % (result, ostart, oend, start, gap) 
        return result

    # name of the database table this data should be in (no dashes)
    def name(self):
        if not self._name_:
             self._name_ = self.Id()
        return  self._name_

    # return true if this appears to be a samsTshEs acceleration packet
    def isSamsTshEsPacket(self): # struct.unpack doesn't seem to think 'h' is 2 bytes
        if not self._samsTshEs_:
            if len(self.p) < 80:
                self._samsTshEs_ = 0
                if self._showWarnings_:
                    t = 'SAMS TSH-ES packet warning\n' + self.hexDump() + UnixToHumanTime(time(), 1) + '\n'  
                    t = t + ' packet too short (%s) to be a samsTshEs acceleration packet' % len(self.p)
                    printLog(t)
                return self._samsTshEs_
            byte0 = struct.unpack('c', self.p[0])[0]
            byte1 = struct.unpack('c', self.p[1])[0]
            if not (byte0 == chr(0xac) and byte1 == chr(0xd3)):
                self._samsTshEs_ = 0
                if self._showWarnings_:
                    t = 'SAMS TSH-ES packet warning\n' + self.hexDump() + UnixToHumanTime(time(), 1) + '\n'  
                    t = t + ' packet cannot be samsTshEs accel because it does not start with 0xacd3'
                    printLog(t)
                return self._samsTshEs_
            byte2 = struct.unpack('c', self.p[40])[0]
            byte3 = struct.unpack('c', self.p[41])[0]
            selector = ord(byte2)*256+ord(byte3)
            accelpacket = (selector == 170) or (selector == 171) # || (selector == 177)
            if not accelpacket:
                self._samsTshEs_ = 0
                if self._showWarnings_:
                    t = 'SAMS TSH-ES packet warning\n' + self.hexDump() + UnixToHumanTime(time(), 1) + '\n'  
                    t = t + ' packet cannot be samsTshEs accel because it does not have an TshesAccelPacket selector at offset 40'
                    printLog(t)
                return self._samsTshEs_
            if len(self.p) < 80+16*self.samples():
                self._sams2_ = 0
                t = 'SAMS TSH-ES packet warning\n' + self.hexDump() + UnixToHumanTime(time(), 1) + '\n'  
                t = t + ' packet is not a complete samsTshEs accel packet, %s samples are not present' % self.samples()
                printLog(t)
                return self._samsTshEs_
            self._samsTshEs_ = 1
            self.addAdditionalDQM(self.adjustment())
        return self._samsTshEs_

    # return header info in XML format for this packet
    def xmlHeader(self):
        if not self._xmlHeader_:
            self._xmlHeader_ = ''
            self._xmlHeader_ = self._xmlHeader_ + '\t<SensorID>%s</SensorID>\n' % self.name()
            self._xmlHeader_ = self._xmlHeader_ + '\t<TimeZero>%s</TimeZero>\n' % UnixToHumanTime(self.time())
            self._xmlHeader_ = self._xmlHeader_ + '\t<Gain>%s</Gain>\n' % self.gain()
            self._xmlHeader_ = self._xmlHeader_ + '\t<SampleRate>%s</SampleRate>\n' % self.rate()
            self._xmlHeader_ = self._xmlHeader_ + '\t<CutoffFreq>%s</CutoffFreq>\n' % self._cutoffFreq_ 
        return self._xmlHeader_
    
    # return header dictionary appropriate for this packet (everything except the accel data)
    def header(self):
        if not self._header_:
            self._header_['name'] = self.name()
            self._header_['Id'] = self.Id()
            self._header_['isSamsTshEsPacket'] = self.isSamsTshEsPacket()
            self._header_['status'] = self.status()
            self._header_['rate'] = self.rate()
            self._header_['gain'] = self.gain()
            self._header_['unit'] = self.unit()
            self._header_['adjustment'] = self.adjustment()
            self._header_['samples'] = self.samples()
            self._header_['time'] = self.time()
            self._header_['endTime'] = self.endTime()
        return self._header_
        
    def Id(self): 
        if not self._Id_:
            self._Id_ = self.p[44:60]
            self._Id_ = replace(self._Id_ , chr(0), '') # delete nulls
            self._Id_ = join(split(self._Id_, '-'), '') # delete dashes
            self._Id_ = self._Id_[-4:]                  # keep last 4 characters only, i.e., "es13"
        return self._Id_
        
    def status(self): # packet status
        if not self._status_:
            self._status_ = struct.unpack('!i', self.p[72:76])[0] # Network byte order
        return self._status_

    def samples(self):
        if not self._samples_:
            self._samples_ = struct.unpack('!i', self.p[76:80])[0] # Network byte order
        return self._samples_

    def rate(self):
        if not self._rate_:
            statusInt = self.status()
            rateBits = (statusInt & 0x0f00) >> 8

            if (rateBits == 0):
                self._rate_ = 7.8125
                self._cutoffFreq_ = 3.2
            elif (rateBits == 1):
                self._rate_ = 15.625
                self._cutoffFreq_ = 6.3
            elif (rateBits == 2): 
                self._rate_ = 31.25
                self._cutoffFreq_ = 12.7
            elif (rateBits == 3):
                self._rate_ = 62.5
                self._cutoffFreq_ = 25.3
            elif (rateBits == 4):
                self._rate_ = 125.0
                self._cutoffFreq_ = 50.6
            elif (rateBits == 5):
                self._rate_ = 250.0
                self._cutoffFreq_ = 101.4
            elif (rateBits == 6):
                self._rate_ = 500.0
                self._cutoffFreq_ = 204.2
            elif (rateBits == 7):
                self._rate_ = 1000.0
                self._cutoffFreq_ = 408.5
            elif (rateBits == 8):
                self._rate_ = 125.0
                self._cutoffFreq_ = 23.5
            else:
                if self._showWarnings_:
                    t = '\n' + self.hexDump()
                    t = t + '\n' +  self.dump()
                    t = t + '\n' +  UnixToHumanTime(time(), 1),  
                    t = t + '\n' +  ' bogusRateByte: %s at time %.4f, assuming rate=1000' % (rateBits, self.time())
                    printLog(t)
                self._rate_ = 1000.0
        return self._rate_
    
    def gain(self):
        if not self._gain_:
            statusInt = self.status()
            gainBits = statusInt & 0x001f
            
            if (gainBits == 0):
                self._gain_ = 1.0
                self._input_ = 'Ground' # _input_ is not used as far as I can tell
            elif (gainBits == 1):
                self._gain_ = 2.5
                self._input_ = 'Ground'
            elif (gainBits == 2):
                self._gain_ = 8.5
                self._input_ = 'Ground'
            elif (gainBits == 3):
                self._gain_ = 34.0
                self._input_ = 'Ground'
            elif (gainBits == 4):
                self._gain_ = 128.0
                self._input_ = 'Ground'
            elif (gainBits == 8):
                self._gain_ = 1.0
                self._input_ = 'Test'
            elif (gainBits == 9):
                self._gain_ = 2.5
                self._input_ = 'Test'
            elif (gainBits == 10):
                self._gain_ = 8.5
                self._input_ = 'Test'
            elif (gainBits == 11):
                self._gain_ = 34.0
                self._input_ = 'Test'
            elif (gainBits == 12):
                self._gain_ = 128.0
                self._input_ = 'Test'
            elif (gainBits == 16):
                self._gain_ = 1.0
                self._input_ = 'Signal'
            elif (gainBits == 17):
                self._gain_ = 2.5
                self._input_ = 'Signal'
            elif (gainBits == 18):
                self._gain_ = 8.5
                self._input_ = 'Signal'
            elif (gainBits == 19):
                self._gain_ = 34.0
                self._input_ = 'Signal'
            elif (gainBits == 20):
                self._gain_ = 128.0
                self._input_ = 'Signal'
            elif (gainBits == 24):
                self._gain_ = 1.0
                self._input_ = 'Vref'
            elif (gainBits == 25):
                self._gain_ = 1.0
                self._input_ = 'Sensor test'
            elif (gainBits == 26):
                self._gain_ = 2.0
                self._input_ = 'Sensor test'               
            else:
                if self._showWarnings_:
                    t = '\n' + self.hexDump()
                    t = t + '\n' +  self.dump()
                    t = t + '\n' +  UnixToHumanTime(time(), 1),  
                    t = t + '\n' +  ' TSH-ES bogusGainByte: %s at time %.4f, assuming gain=1' % (gainBits, self.time())
                    printLog(t)
                self._gain_ = 1.0
        return self._gain_

    def unit(self):
        if not self._unit_:
            statusInt = self.status()
            unitBits = (statusInt & 0x0060) >> 5
            
            if (unitBits == 0):
                self._unit_ = 'counts'
            elif (unitBits == 1):
                self._unit_ = 'volts'
            elif (unitBits == 2):
                self._unit_ = 'g'
            else:
                if self._showWarnings_:
                    t = '\n' + self.hexDump()
                    t = t + '\n' +  self.dump()
                    t = t + '\n' +  UnixToHumanTime(time(), 1),  
                    t = t + '\n' +  ' TSH-ES bogusUnitByte: %s at time %.4f, assuming unit=g' % (unitBits, self.time())
                    printLog(t)
                self._unit_ = 'g'
        return self._unit_

    def adjustment(self):
        if not self._adjustment_:
            statusInt = self.status()
            adjBits = (statusInt & 0x0080) >> 7

            self._dqmIndicator_ = adjBits
            self._adjustment_ = 'no-compensation'
            if (adjBits == 1):
                self._adjustment_ = 'temperature-compensation'
        return self._adjustment_

    def time(self):
        if not self._time_:
            sec, usec = struct.unpack('!II', self.p[64:72]) # Network byte order
            self._time_ = sec + usec/1000000.0
        return self._time_
    
    def endTime(self): 
        if not self._endTime_:
            self._endTime_ = self.time() + (self.samples()-1) / self.rate() 
        return self._endTime_
    
    def handleDigitalIOstatus(self, digitalIOstatus, sampleNumber):
        # check for the 'something interesting happened' bit for this sensor and do something with it
        enabled = digitalIOstatus & 0x0001
        if enabled:
            inputIO = (digitalIOstatus & 0x0004) > 2
            if DigitalIOstatusHolder.has_key(self.name()):
                interestingBit = DigitalIOstatusHolder[self.name()]
                if interestingBit != inputIO: # state change
                    DigitalIOstatusHolder[self.name()] = inputIO
                    # state change detected, what should be do with that information?
                    eventTime = self.time() + sampleNumber/self.rate()
                    msg = ' (inputIO_state_change:%s time:%.4f)' % (inputIO, eventTime)
                    print self.name(), msg
            else:
                DigitalIOstatusHolder[self.name()] = inputIO

    def xyz(self):
        if not self._xyz_:
            convert = 0
##            if self.unit() != 'g':   #### need calibration numbers for flight units
##                convert = 1
##                if self.unit() == 'volts':
##                    mx = my = mz = 1.0/3.89791388
##                    bx = by = bz = 0
##                else: # must be counts
##                    if self.gain() == 1.0:
##                        mx = my = mz = 2.18538e-07
##                        bx = by = bz = -0.026280804
##                    elif self.gain() == 10.0:
##                        mx = my = mz = 2.18538e-08
##                        bx = by = bz = -0.00262381
##                    elif self.gain() == 100.0:
##                        mx = my = mz = 2.18538e-09
##                        bx = by = bz = -0.00026280804
##                    elif self.gain() == 1000.0:
##                        m = 2.18538e-10
##                        bx = by = bz = -0.000026280804
            for i in range(self.samples()):
                start = 80+16*i
                stop = start+16
                x, y, z, digitalIOstatus = struct.unpack('!fffI', self.p[start:stop]) # Network byte order
                self.handleDigitalIOstatus(digitalIOstatus, i)
                if convert:
                    x, y, z = x*mx+bx, y*my+by, z*mz+bz
                self._xyz_.append((x,y,z))
        return self._xyz_
    
    def txyz(self):
        if not self._txyz_:
            dt = 1.0/self.rate()
            convert = 0
##            if self.unit() != 'g':
##                convert = 1
##                if self.unit() == 'volts':
##                    mx = my = mz = 1.0/3.89791388
##                    bx = by = bz = 0
##                else: # must be counts
##                    if self.gain() == 1.0:
##                        mx = my = mz = 2.18538e-07
##                        bx = by = bz = -0.026280804
##                    elif self.gain() == 10.0:
##                        mx = my = mz = 2.18538e-08
##                        bx = by = bz = -0.00262381
##                    elif self.gain() == 100.0:
##                        mx = my = mz = 2.18538e-09
##                        bx = by = bz = -0.00026280804
##                    elif self.gain() == 1000.0:
##                        m = 2.18538e-10
##                        bx = by = bz = -0.000026280804
            for i in range(self.samples()):
                start = 80+16*i
                stop = start+16
                x, y, z, digitalIOstatus = struct.unpack('!fffI', self.p[start:stop]) # Network byte order
                self.handleDigitalIOstatus(digitalIOstatus, i)
                if convert:
                    x, y, z = x*mx+bx, y*my+by, z*mz+bz
                t = i*dt
                self._txyz_.append((t,x,y,z))
        return self._txyz_

class Counter(object):
    #for c in Counter(3, 8):
    #    print c
    #raise SystemExit    
    def __init__(self, low, high):
        self.current = low
        self.high = high

    def __iter__(self):
        return self

    def next(self):
        if self.current > self.high:
            raise StopIteration
        else:
            self.current += 1
            return self.current - 1

class PacketProcessor(object):
    """iterate over and process db records containing accel packets"""
    def __init__(self, query_str, host):
        """init the packet processor"""
        self.query_str = query_str
        self.host = host
        self.summary = self.processRecords(query_str, host)

    def showThisRecord(self, c, r, pis):
        # NOTE: r[0] is time, r[1] is the blob, r[2] is the type
        p = guessPacket(r[1])
        print '%06d' % c,
        print p.name(),
        print 'packet from:', UnixToHumanTime( p.time() ),
        print 'to:', UnixToHumanTime( p.endTime() ),
        print 'fs:', p.rate(),
        print 'samples:', p.samples(),
        tdelta = p.endTime() - p.time()
        poff = ( ( p.samples() - 1 ) / p.rate() ) - tdelta
        poffstr = 'poff: {0:>9f}'.format( np.around(poff, 4) )
        print poffstr,
        pi = PadInterval( unix2dtm(p.time()), unix2dtm(p.endTime()), sampleRate=p.rate() )
        pis.add(pi)
        print "intervalSetLen:", len(pis)
        #print p.dump(1)
        #print p.hexDump()

    def processRecords(self, query_str, shost='localhost', suser=UNAME, spasswd=PASSWD, sdb=SCHEMA):
        sqlRetryTime = 30
        try:
            con = Connection(host=shost, user=suser, passwd=spasswd, db=sdb)
            cursor = con.cursor()
            cursor.execute(query_str)

            count = 0
            packetIntervalSet = PadIntervalSet()
            results = self.fetchsome(cursor)
            for rec in results:
                # NOTE: rec[0] is time, rec[1] is the blob, rec[2] is the type
                count += 1
                #print count, UnixToHumanTime( rec[0] )
                self.showThisRecord(count, rec, packetIntervalSet)

            cursor.close()
            con.close()
        except MySQLError, msg:
            t = UnixToHumanTime(time(), 1) + '\n' + msg[1] + '\nMySQL call failed, will try again in %s seconds' % sqlRetryTime
            printLog(t)
            if idleWait(sqlRetryTime):
                return []
        summary = 'What to do for summary?'
        return summary

    def fetchsome(self, cursor, some=4800):
        """ when fs = 500 sa/sec, packet rate is about 8 pkts/sec, so some = 4800 gives 10 minutes """
        fetch = cursor.fetchmany
        while True:
            rows = fetch(some)
            if not rows: break
            print '--- FETCHED %d RECORDS ---' % len(rows)
            for row in rows:
                yield row

def demo_simple_pad_interval():
    t1 = datetime.datetime(2013, 9, 8, 7, 6, 0, 0)
    t2 = datetime.datetime(2013, 9, 8, 7, 6, 1, 2100)
    t3 = datetime.datetime(2013, 9, 8, 7, 6, 1, 4100)
    t4 = datetime.datetime(2013, 9, 8, 7, 6, 2, 1500)
    t5 = datetime.datetime(2013, 9, 8, 7, 6, 2, 3510)
    t6 = datetime.datetime(2013, 9, 8, 7, 6, 3, 0)
    
    print t2
    print t3
    pi12 = PadInterval(t1, t2, sampleRate=500.0)
    pi34 = PadInterval(t3, t4, sampleRate=500.0)
    print pi12.adjacent_to(pi34)
    
    print t4
    print t5
    pi56 = PadInterval(t5, t6, sampleRate=500.0)
    print pi34.adjacent_to(pi56)
    
    pis = PadIntervalSet()
    pis.add(pi12)
    pis.add(pi34)
    pis.add(pi56)
    
    print pis
    print len(pis)

def demo_packet_processor():
    # Packet processor was quickly coded, but I managed to rig generator to avoid memory issues (hopefully)
    import sys
    sensor = sys.argv[1]
    pp = PacketProcessor('select * from ' + sensor + ' order by time limit 20', 'manbearpig')
    print pp.summary

###############################################################################
if __name__ == "__main__":

	#demo_simple_pad_interval(); raise SystemExit

	#demo_packet_processor(); raise SystemExit

    # SAMS-II test
#    results = sqlConnect('select * from 121_e01 order by time limit 1', 'parrot.grc.nasa.gov')
	results = sqlConnect('select * from 121f03 order by time limit 50', 'manbearpig')

    # Hirap test
#    results = sqlConnect('select * from hirap order by time limit 1', 'vizquel.grc.nasa.gov')

    # OSS test
    #results = sqlConnect('select * from oss order by time desc limit 1', 'localhost')
    
    # best-fit-tmf test
#    results = sqlConnect('select * from besttmf957993371 order by time limit 1', 'justice.grc.nasa.gov')
    
    # final-tmf test
#    results = sqlConnect('select * from finaltmf957156731 order by time limit 1', 'justice.grc.nasa.gov')

    # bias-final test
#    results = sqlConnect('select * from finalbias957156731 order by time limit 1', 'justice.grc.nasa.gov')

    # samsff test
#    results = sqlConnect('select * from SAMSFF_PAD order by time desc limit 1', 'fryman.grc.nasa.gov')

    # sams tsh-es test
#    results = sqlConnect('select * from es05 order by time desc limit 1', 'localhost')

	for i in results:
		# i[0] is time, i[1] is the blob, i[2] is the type
		print 'time from table:', UnixToHumanTime( i[0] )
		print 'time:', UnixToHumanTime( guessPacket(i[1]).time() )
		print 'name:', guessPacket(i[1]).name()
		print 'rate:', guessPacket(i[1]).rate()
		print 'samples:', guessPacket(i[1]).samples()
		#print 'measurementsPerSample:', guessPacket(i[1]).measurementsPerSample()
		
		print 'at dbTime:%.4f' % i[0], 'is a',
		print guessPacket(i[1]).dump(1)
		#print guessPacket(i[1]).hexDump()
		
		p = guessPacket(i[1])
		print 'Verification of Sample Rate:', (p.samples() - 1) / ( p.endTime() - p.time() )