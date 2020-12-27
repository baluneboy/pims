#!/usr/bin/env python
version = '$Id: padutils.py,v 1.12 2005/02/23 19:52:50 hrovat Exp $'

import os, sys
from string import *
from time import *
from commands import *
from math import *
from xml.dom.minidom import *
import createheaderdict as chd
import glob
from resample import unixTimeToString, stringTimeToUnix, stringTimeToTuple
from jwstcal import getSampleRate
#import creatematlabinfomatfile as cmi

def stringTimeToUnix_NEW(st):
    """convert a number in 2002_12_18_11_59_12.960 format to Unix time"""
    y, m, d, h, n, s, ms = stringTimeToTuple(st)
    epochSecs = mktime(map(int ,(y, m, d, h, n, s, 0, 0, 0)))-timezone
    #print "seconds is %f\n" % (epochSecs + int(ms)/1000.0)
    return epochSecs + int(ms)/1000.0

def unixTimeToString_NEW(ut):
    """convert a number in Unix time to 2002_12_18_11_59_12.960 format"""
    intTime = int(ut)
    frac = ut - intTime
    #print "\nfrac is %f, conv is %f" % (frac, round(frac*1000))
    y, m, d, ho, mi, se, junk1, junk2, junk3 = gmtime(intTime)
    #print "ut is %f, s is %4d_%02d_%02d_%02d_%02d_%02d.%03d\n" % (ut, y, m, d, ho, mi, se, int(frac*1000))
    #return '%4d_%02d_%02d_%02d_%02d_%02d.%03d' % (y, m, d, ho, mi, se, int(frac*1000))
    return '%4d_%02d_%02d_%02d_%02d_%02d.%03d' % (y, m, d, ho, mi, se, round(frac*1000))

def stringTimeToTuple_NEW(st):
    """ get date/time component tuple from string like this  2002_12_18_11_59_12.960 """
    st, ms = split(st, '.')
    y, m, d, h, n, s = split(st, '_')
    return y,m,d,h,n,s,ms

def fileTimeRange(padFileName):
    """convert long PIMS PAD file names into numbers"""
    padFileName = split(padFileName, '/')[-1] # throw away path 
    padFileName = split(padFileName, '.header')[0] # throw away '.header'
    sensor =  split(padFileName, '.')[-1]
    padFileName = join(split(padFileName, '.')[:-1], '.')
    pair = split(padFileName, '-')
    if len(pair) == 1:
        pair = split(padFileName, '+')
        joiner = '-'
    else:
        joiner = '+'
    return stringTimeToUnix(pair[0]), joiner, stringTimeToUnix(pair[1])


def prevDate(y, m, d):
    """returns the year, month, and day before the one that is given"""
    dateTuple = (y, m, d, 0, 0, 0, 0, 0, 0)
    epochSecs = mktime(dateTuple)
    prevDateTuple = localtime(epochSecs-24*60*60)
    return prevDateTuple[:3]

def nextDate(y, m, d):
    """returns the year, month, and day following the one that is given"""
    dateTuple = (y, m, d, 0, 0, 0, 0, 0, 0)
    epochSecs = mktime(dateTuple)
    nextDateTuple = localtime(epochSecs+24*60*60)
    return nextDateTuple[:3]

def pareHeader(headerFile,Ldontcares=['GData','BiasCoeff','headerFile','y_m_d','TimeZero']):
    """ get rid of don't cares and so on """
    reload(chd) # KEN SCOPE ISSUE?
    dHeader = chd.main(['headerFile=' + headerFile])
    #Ldontcares = ['GData','BiasCoeff','headerFile','y_m_d','TimeZero']
    #Ldontcares = ['GData','BiasCoeff','headerFile','y_m_d']
    for k in Ldontcares:
        del dHeader[k]
    dataFile = split(headerFile,'.header')[0] # toss extension
    return dHeader,dataFile

def getPadHeaderFiles(padPath, dateStart, dateStop, sensor):
    """ find contiguous PAD header file groups """
    padFiles,sampleRate,dataColumns = getPadFiles(padPath,dateStart,dateStop,sensor,'.header')
    return padFiles,sampleRate,dataColumns

def getPadDataFiles(padPath, dateStart, dateStop, sensor):
    """ find contiguous PAD data file groups """
    padFiles,sampleRate,dataColumns = getPadFiles(padPath,dateStart,dateStop,sensor,'')
    return padFiles,sampleRate,dataColumns

def isValidPimsDateString(s):
    """ verify input string is 'PIMS date like' (YYYY_MM_DD_hh_mm_ss.sss) with weak date validation """
    import re
    #                          -------YYYY _ ------------ MM _ ----------------------DD _ --------------------hh _ -----------------mm _ -----------------ss.sss
    goodplaces = re.compile(r'^(19|20)\d\d[_](0[1-9]|1[012])[_](0[1-9]|[12][0-9]|3[01])[_](0[0-9]|1[0-9]|2[0-3])[_](0[0-9]|[1-5][0-9])[_](0[0-9]|[1-5][0-9]).\d{3}$')
    # NOTE: re module's match function matches beginning, while ...
    #       search does not necessarily start match at first postion
    if goodplaces.match(s):
        return True
    else:
        return False

def mutt(addr,subj,text):
    """ If mutt is available, then send body message to addr with subj """
    cmd = 'mutt -h'
    res = getoutput(cmd)
    p = split(res,'\n')[0]
    if lower(p)[0:4] != 'mutt':
        print 'Cannot send mail -- no mutt?'
        return
    cmd = 'echo "%s" | mutt -s "%s" %s' % (text, subj, addr)
    res = getoutput(cmd)
    #print res

def getMaxAbs(data):
    """ Get indices of max values from data [t x y z] """
    import Numeric as N
    nCols = N.size(data,axis=1)
    iMax = []
    for iCol in range(nCols):
        iMax.append(N.argmax(abs(data[:,iCol])))
    return iMax

class FileGetter(object):
    """ FileGetter is a class that manages getting common files
        Inputs:
        basePath='/base/path/goes/here'
        dateStart='YYYY_MM_DD_hh_mm_ss.sss'
        dateStop='YYYY_MM_DD_hh_mm_ss.sss'
        sensor='121f0X'
        subDir='more/path'
        ext='EXT'

        Some common ones are:

        padhist = RESULTSPATH/YMDPATH/SENSOR/SUBDIR/YYYY_MM_DD_HH_SENSOR_hstv+fsFSfcFC.mat
        -------------------$RESULTSPATH/---------------YMDpath/SENSOR/-SUBDIR/YYYY_MM_DD_HH_SENSOR_hstv+fs-FSfc-FC.mat
        /mnt/yoda/offline/batch/results/year2005/month01/day04/121f02/padhist/2005_01_04_23_121f02_hstv+fs250fc100.mat

        padspec = RESULTSPATH/YMDPATH/SENSOR/SUBDIR/YYYY_MM_DD_HH_MM_SS_SSS_SENSOR_spgs+roadmapsFS.mat
        -------------------$RESULTSPATH/---------------YMDpath/SENSOR/----------SUBDIR/YYYY_MM_DD_HH_MM_SS_SSS_SENSOR_spgs+roadmaps-FS.mat
        /mnt/yoda/offline/batch/results/year2005/month01/day04/121f02/padspec/roadmaps/2005_01_04_22_27_39_281_121f02_spgs+roadmaps250.mat

        pad = PADPATH/YMDPATH/DTYPE_accel_SENSOR/YYYY_MM_DD_HH_MM_SS.SSS+YYYY_MM_DD_HH_MM_SS.SSS.SENSOR.header
        ---------$PADPATH/---------------YMDpath/DTYPE_accel_SENSOR/YYYY_MM_DD_HH_MM_SS.SSS+YYYY_MM_DD_HH_MM_SS.SSS.SENSOR.header
        /mnt/yoda/pub/pad/year2004/month12/day22/sams2_accel_121f02/2004_12_22_23_52_10.269+2004_12_23_00_02_10.269.121f02.header
        
    """
    
    def __init__(self, *args, **kwargs):

        # Get keyword args
        for k,v in kwargs.iteritems():
            setattr(self, k, v)    

        # Verify attributes
        self.verify()

        self._files = None
        self.fileList = []
        self.numFiles = 0
        self.index = -1
        
    def __str__(self):
        s  = '  basePath: %s' % self.basePath
        s += '\n dateStart: %s' % unixTimeToString(self.uStart)
        s += '\n  dateStop: %s' % unixTimeToString(self.uStop)
        s += '\n    subDir: %s' % self.subDir
        s += '\n    sensor: %s' % self.sensor
        s += '\n  numFiles: %d' % len(self.fileList)
        if len(self.fileList) != 0:
            s += '\nfirst file: %s' % split(self.fileList[0],os.path.sep)[-1]
            s += '\n last file: %s' % split(self.fileList[-1],os.path.sep)[-1]
        return s
        
    def __len__(self):
        return len(self.fileList)
        
    def __iter__(self):
	return self

    def next(self):
        """ iterate over fileList """
        self.index += 1
        if self.index < len(self.fileList):
            return self.fileList[self.index]
        elif self.index == len(self.fileList):
            self.index = -1
            raise StopIteration
        else:
            raise StopIteration
        
    def isValidBasePath(self):
        if self.basePath == 'RESULTSPATH' or self.basePath == 'PADPATH':
            self.basePath = getoutput('echo ${' + self.basePath + '}') # get ${RESULTSPATH} or ${PADPATH}
        if os.path.exists(self.basePath):
            return True
        else:
            return False
        
    def verify(self):
        """ verify non-optional args to FileGetter """
        
        # Check non-optional args
        pList = ['basePath', 'dateStart', 'dateStop','sensor']
        for p in pList:
            if not hasattr(self, p):
                self.showUsage()
                raise '\nMissing keyword arg: %s.\n' % p
            
        if not self.isValidBasePath():
            raise '\nbasePath (%s) does not exist.\n' % self.basePath

        if not isValidPimsDateString(self.dateStart):
            raise '\ndateStart (%s) is not valid\n' % self.dateStart
        else:
            self.uStart = stringTimeToUnix(self.dateStart)

        if not isValidPimsDateString(self.dateStop):
            raise '\ndateStop (%s) is not valid\n' % self.dateStop
        else:
            self.uStop = stringTimeToUnix(self.dateStop)

    def showUsage(self):
        """ show FileGetter usage """
        print
        print "Required FileGetter keyword args:"
        print "---------------------------------"
        print "basePath='/base/path/goes/here'"
        print "dateStart='YYYY_MM_DD_hh_mm_ss.sss'"
        print "sensor='121f0X'"
        print

class FileGetterPad(FileGetter):
    """ FileGetterPad class derived from FileGetter that manages getting pad files
        Inputs:
        basePath='PADPATH'
        dateStart='YYYY_MM_DD_hh_mm_ss.sss'
        dateStop='YYYY_MM_DD_hh_mm_ss.sss'
        subDir='mams_accel_ossbtmf'
        ext='EXT'

        pad =     BASEPATH/               YMDPATH/ SYS_TYPE_SENSOR/YYYY_MM_DD_HH_mm_ss.sss+YYYY_MM_DD_HH_mm_ss.sss.SENSOR
        ----------$PADPATH/---------------YMDpath/----------SUBDIR/filename
        /mnt/yoda/pub/pad/year2005/month02/day03/mams_accel_ossraw/2005_02_03_15_05_25.054+2005_02_03_17_05_38.837.ossraw

    """
    
    def __init__(self, *args, **kwargs):

        # Get sensor from subdir
        self.subDir = kwargs['subDir']
        self.sensor = split(self.subDir,'_')[-1]
        if self.sensor == 'ossraw':
            self.numCols = 6
        else:
            self.numCols = 4

        # Super init
        super(FileGetterPad, self).__init__(*args, **kwargs)

##        # For pad, get dateStart & dateStop to whole hour
##        self.uStart = int(self.uStart/3600.0)*3600.0
##        self.uStop = int(self.uStop/3600.0)*3600.0

        # Get list of files
        self.getFileList()
        self._files = self.fileList[:]
        self._files.reverse() # for iteration scheme

        # Get first file sampleRate and offsetRecs
        file1 = self.fileList[0]
        startOffsetSamples, actualStart = startOffset(file1,getSampleRate(file1),self.dateStart,self.numCols)

        # Get last file numRecs
        fileN = self.fileList[-1]
        stopNumRecs, actualStop = endNum(fileN,getSampleRate(fileN),self.dateStop)
        
    def getFileList(self):
        """ populate file list attribute """
        print 'getting fileList ...',
        sid = 86400 # change to 3600 for hour-by-hour
        uDays = range(sid*(int(self.uStart)/sid),sid+(sid*(int(self.uStop)/sid)),sid)
        fileList = []
        sep = os.path.sep
        for d in uDays:
            s = unixTimeToString(d)
            ymdPath = 'year' + s[0:4] + sep + 'month' + s[5:7] + sep + 'day' + s[8:10]
            dirname = self.basePath + sep + ymdPath + sep + self.subDir
            pattern = '*' + self.sensor
            nameList = glob.glob1(dirname,pattern)
            for name in nameList:
                ufStart = stringTimeToUnix(name[0:23])
                ufStop  = stringTimeToUnix(name[24:47])
                if  ( ufStart <= self.uStart <= ufStop ) or ( self.uStart <= ufStart <= self.uStop ) or ( ufStart <= self.uStop <= ufStop ):
                    #print 'IN: %s' % unixTimeToString(uTime)
                    fileList.append(dirname + sep + name)
##                else:
##                    print 'OUT:\n%s\n%s\n%s' % (unixTimeToString(ufStart),unixTimeToString(self.uStart),unixTimeToString(ufStop))
        fileList.sort()
        self.fileList = fileList
        print 'done'

class FileGetterPadSpec(FileGetter):
    """ FileGetterPadSpec class derived from FileGetterPadHist that manages getting padspec files
        Inputs:
        basePath='RESULTSPATH'
        dateStart='YYYY_MM_DD_hh_mm_ss.sss'
        dateStop='YYYY_MM_DD_hh_mm_ss.sss'
        sensor='121f0X'
        subDir='more/path'
        ext='EXT'

        padspec = RESULTSPATH/YMDPATH/SENSOR/SUBDIR/YYYY_MM_DD_HH_MM_SS_SSS_SENSOR_spgs+roadmapsFS.mat
        -------------------$RESULTSPATH/---------------YMDpath/SENSOR/----------SUBDIR/YYYY_MM_DD_HH_MM_SS_SSS_SENSOR_spgs+roadmaps-FS.mat
        /mnt/yoda/offline/batch/results/year2005/month01/day04/121f02/padspec/roadmaps/2005_01_04_22_27_39_281_121f02_spgs+roadmaps250.mat
    """

    def getGlobArgs(self):
        """ get dirname and pattern arguments for glob1 """
        dirname,pattern = '/tmp','trash2*.txt'
        return dirname, pattern


class FileGetterPadHist(FileGetterPadSpec):
    """ FileGetterPadHist class derived from FileGetter that manages getting padhist files
        Inputs:
        basePath='RESULTSPATH'
        dateStart='YYYY_MM_DD_hh_mm_ss.sss'
        dateStop='YYYY_MM_DD_hh_mm_ss.sss'
        sensor='121f0X'
        subDir='more/path'
        ext='EXT'

        padhist = BASEPATH/YMDPATH/SENSOR/SUBDIR/YYYY_MM_DD_HH_SENSOR_hstv+fsFSfcFC.mat
        -------------------$RESULTSPATH/---------------YMDpath/SENSOR/-SUBDIR/YYYY_MM_DD_HH_SENSOR_hstv+fs-FSfc-FC.mat
        /mnt/yoda/offline/batch/results/year2005/month01/day04/121f02/padhist/2005_01_04_23_121f02_hstv+fs250fc100.mat

    """
    
    def __init__(self, *args, **kwargs):

        from scipy import io

        # Super init
        super(FileGetterPadHist, self).__init__(*args, **kwargs)

        # For padhist, get dateStart & dateStop to whole hour
        self.uStart = int(self.uStart/3600.0)*3600.0
        self.uStop = int(self.uStop/3600.0)*3600.0
        
    def getFileList(self):
        """ populate file list attribute (padhist are strictly hourly) """
        sid = 86400 # change to 3600 for hour-by-hour
        uDays = range(sid*(int(self.uStart)/sid),sid+(sid*(int(self.uStop)/sid)),sid)
        fileList = []
        sep = os.path.sep
        for d in uDays:
            s = unixTimeToString(d)
            ymdPath = 'year' + s[0:4] + sep + 'month' + s[5:7] + sep + 'day' + s[8:10]
            dirname = self.basePath + sep + ymdPath + sep + self.sensor + sep + 'padhist'
            pattern = '*' + self.sensor + '_hstv*.mat'
            nameList = glob.glob1(dirname,pattern)
            for name in nameList:
                uTime = stringTimeToUnix(name[0:13] + '_00_00.000')
                if ( self.uStart <= uTime <= self.uStop ):
                    #print 'IN: %s' % unixTimeToString(uTime)
                    fileList.append(dirname + sep + name)
        fileList.sort()
        self.fileList = fileList
        
    def checkthisout(self):
        print [h for h in uRange if h>=0]
        for uHour in range(self.uStart,self.uStop,3600):
            print unixTimeToString(uHour)

def getPadFiles(padPath, dateStart, dateStop, sensor, ext):
    """
    find contiguous PAD file groups
    padFiles, sampleRate, dataColumns = getPadFiles(padPath, dateStart, dateStop, sensor, ext)
    """
    if dateStart >= dateStop:
        raise 'why start after stop?'
    start = split(dateStart, '_')
    startS = float(start[-1])
    startY, startM, startD, startH, startN = map(int, start[:-1])
    stop = split(dateStop, '_')
    stopS = float(stop[-1])
    stopY, stopM, stopD, stopH, stopN = map(int, stop[:-1])
    y,m,d = prevDate(startY,startM,startD)
    result = ''
    #while y <= stopY and m <= stopM and d <= stopD: # does not handle begin month borders
    while (y,m,d) <= (stopY,stopM,stopD): 
        # grab all sensor matching headers from each day ('ls' results are sorted)
        cmd = 'ls -1 %s/year%s/month%02d/day%02d/*/*%s%s' % (padPath, y, m, d, sensor, ext)#; print cmd
        cmdOutput = getoutput(cmd)
        if cmdOutput[-25:] != 'No such file or directory':
            result += cmdOutput + '\n'#; print result
        y, m , d = nextDate(y, m , d)

    if result == '': return [],[],[] # no files to process

    # make sure all filenames are OK
    trimmed = split(result, '\n')
    allLines = []
    for i in trimmed:
        if i != '':
            allLines.append(i)

##    print 'allLines[0] is ' + allLines[0]

    # keep files with data after dateStart & before dateStop
    padFiles = []
    for i in allLines:
        fname = split(i,'/')[-1] # toss path
        e = split(fname, '-')
        if len(e) == 1:
            e = split(fname, '+')
        if (e[1] >'%s.%s%s' % (dateStart, sensor, ext)) and (e[0] <= '%s.%s%s' % (dateStop, sensor, ext)):
            padFiles.append(i)
    
    # get number of dat columns
    dataColumns = 4 # default
    if sensor == u'oare' or sensor == u'ossraw':
        dataColumns = 6 # mams has temperature and status columns

    # get sample rate of first PAD header file
    if padFiles:
        if ext == '':
            sampleRate = float(parse(padFiles[0]+'.header').documentElement.getElementsByTagName('SampleRate')[0].childNodes[0].nodeValue)
        else:
            sampleRate = float(parse(padFiles[0]).documentElement.getElementsByTagName('SampleRate')[0].childNodes[0].nodeValue)
        return padFiles,sampleRate,dataColumns
    else:
        return [],[],[]

def startOffset(padFile,sampleRate,dateStart,dataColumns=4):
    """determine samples to skip (usually in first pad file of many)"""
    #bytesPerRecord = dataColumns * 4
    bb, bj, be = fileTimeRange(padFile)
    #print '    start: %s\ndateStart: %s\n     stop: %s' % ( unixTimeToString(bb), dateStart, unixTimeToString(be) )
    practicalStart = max(stringTimeToUnix(dateStart), bb)
    dateStartOffset = practicalStart - bb # time to skip in first pad file
    startOffsetSamples = int(dateStartOffset * sampleRate  - 0.5)
    #startOffsetBytes = startOffsetSamples * bytesPerRecord
    actualStart = bb + startOffsetSamples/float(sampleRate)
    #print 'START OFFSET: samples: %d, bytes: %d, sec: %f' % ( startOffsetSamples, startOffsetBytes, startOffsetSamples/float(sampleRate) )
    #print 'START OFFSET: samples: %d, sec: %f' % ( startOffsetSamples, startOffsetSamples/float(sampleRate) )
    return startOffsetSamples,actualStart

def endNum(lastFile,sampleRate,dateStop):
    """determine number of records needed from last file"""
    eb, ej, ee = fileTimeRange(lastFile)
    #print '    start: %s\n dateStop: %s\n     stop: %s' % ( unixTimeToString(eb), dateStop, unixTimeToString(ee) )
    practicalStop = min(stringTimeToUnix(dateStop), ee)
    dateStopOffset = practicalStop - eb # time to skip in last pad file
    stopNumRecords = int(dateStopOffset * sampleRate  + 0.5)
    actualStop = eb + stopNumRecords/float(sampleRate)
    #print ' STOP: numRecords: %d, sec: %f' % ( stopNumRecords, stopNumRecords/float(sampleRate) )
    return stopNumRecords,actualStop

def boolean(seq0, seq1, boolean_modus):
    """ perform 'and', 'not', 'or', or 'xor' operation on sequences """
    if boolean_modus == 'and':    # intersection
        seq1 = seq1[:]
        intersection = []
        for item in seq0:
            if item in seq1:
                intersection.append(item)
                seq1.remove(item)
        return intersection
    elif boolean_modus == 'not':  # set difference
        setdiff = seq0[:]
        for item in seq1:
            if item in setdiff:
                setdiff.remove(item)
        return setdiff
    elif boolean_modus == 'or':   # union
        return seq0 + boolean(seq1, seq0, 'not')
    elif boolean_modus == 'xor':  # symmetric difference
        return boolean(boolean(seq0, seq1, 'or'), boolean(seq0, seq1, 'and'), 'not')

def showArgs(padPath,dateStart,dateStop,sensor,abbr,whichAx,pm,tag,Nfft,No):
    """ show arguments """
    print
    print '  padPath:', parameters['padPath']
    print 'dateStart:', parameters['dateStart'], stringTimeToUnix(parameters['dateStart'])
    print ' dateStop:', parameters['dateStop'], stringTimeToUnix(parameters['dateStop'])
    print '   sensor:', parameters['sensor']
    print '     abbr:', parameters['abbr']
    print '  whichAx:', parameters['whichAx']
    print '       pm:', parameters['pm']
    print '      tag:', parameters['tag']
    print '     Nfft:', parameters['Nfft']
    print '       No:', parameters['No']
    print

def processTemplate(padPath,dateStart,dateStop,sensor,abbr='spg',whichAx='s',pm='+',tag='untitled',Nfft=None,No=None):
    """ this is how a PAD processing routine should look """

    showArgs(padPath,dateStart,dateStop,sensor,abbr,whichAx,pm,tag,Nfft,No)

    # get list of pad header files that cover span of interest
    padFiles,sampleRate,dataColumns = getPadHeaderFiles(padPath,dateStart,dateStop,sensor)
    if not(padFiles): return # no files?

    # get samples to skip and actualStart from first PAD file
    startOffsetSamples,actualStart = startOffset(padFiles[0],sampleRate,dateStart,dataColumns)

    # get header template to lead the way from first PAD file (and dataFile)
    headerTemplate,dataFile = pareHeader(padFiles[0])
    strFs = headerTemplate['SampleRate']

    # if Nfft or No not defined, then get defaults
    if not Nfft or not No:
        Nfft,No = cmi.getNfftNo(float(strFs))
        
    print 'B ' + dataFile # FIRST PAD FILE TO WORK ON
    #octaveCalcSpec(dataFile,startOffsetSamples,'inf',abbr,whichAx,pm,tag,strFs,Nfft,No)

    # work pad files list for loop & last processing below
    h1=padFiles[0]                                        
    del(padFiles[0])
    if not(padFiles): return # only one file done
    lastFile = padFiles[-1]
    del(padFiles[-1])
    
    # now do all but last file
    padFiles.reverse()
    while padFiles:
	headerFile = padFiles.pop()
	thisHeader,dataFile = pareHeader(headerFile)
	if thisHeader == headerTemplate:
	    print 'M ' + dataFile # ONE OF TWEEN PAD FILES TO WORK ON
            #octaveCalcSpec(dataFile,0,'inf',abbr,whichAx,pm,tag,strFs,Nfft,No)
	else:
	    print 'X ' + dataFile # DOES NOT MATCH HEADER TEMPLATE

    # determine samples to skip in last pad file
    thisHeader,dataFile = pareHeader(lastFile)
    if thisHeader == headerTemplate:
        stopNumRecords,actualStop = endNum(lastFile,sampleRate,dateStop)
        print 'E ' + dataFile # LAST OF PAD FILES TO WORK ON
        #octaveCalcSpec(dataFile,0,stopNumRecords,abbr,whichAx,pm,tag,strFs,Nfft,No)
    else:
        print 'X ' + dataFile # DOES NOT MATCH HEADER TEMPLATE

def sanityCheck(parameters):
    """ sanity check parameters entered on command line """
    if not parameters: printUsage(); sys.exit()

    # these may differ depending on type of processing to do
    padPath = parameters['padPath']
    dateStart = parameters['dateStart']
    dateStop = parameters['dateStop']
    sensor = parameters['sensor']
    abbr = parameters['abbr']
    whichAx = parameters['whichAx']
    pm = parameters['pm']
    tag = parameters['tag']
    Nfft = parameters['Nfft']
    No = parameters['No']
    
    if not os.path.isdir(padPath): print '%s does not exist' % padPath; sys.exit()
    if not(pm in ['+','-']): print 'bad pm flag (%s): it should be either (+) for demean OR (-) for keep mean' % pm; sys.exit()

    return padPath,dateStart,dateStop,sensor,abbr,whichAx,pm,tag,Nfft,No

def printUsage():
    """print short description of how to run the program"""
    print version
    print "usage: $PROGPATH/python/padutils.py padPath dateStart dateStop sensor abbr='spg' whichAx='s' pm='+' tag='untitled' Nfft=None No=None"

def parseCommandLine(argv):
    """ parse command line parameters """
    parameters = {}
    for p in argv[1:]: # skip 0th element (module name)
        pair = split(p, '=', 1)
        if (2 != len(pair)):
            print 'bad parameter: %s (had no equals sign for pairing)' % p
            sys.exit()
        else:
            parameters[pair[0]] = pair[1]
    return parameters


def getBins(fs):
	""" Determine binMin,binStep,binMax from fs """
	dN = {#   fs:(binMin,binStep,binMax)
		  10:(0     ,  1.25e-06,  0.25e-03), # for 1 Hz LPF (fsNew=10)
		  50:(0     ,  2.5e-06,   0.5e-03),  # for 6 Hz LPF (fsNew=50)
		 250:(0     , 25e-06  ,   5e-03),
		 500:(0     , 50e-06  ,  10e-03),
		1000:(0     ,100e-06  ,  20e-03)
	}
	binMin,binStep,binMax = dN.get(fs, (False,False,False))
	if not binStep: raise '\nunaccounted for sample rate = %f\n' % fs
	return binMin,binStep,binMax
	
def getNfftNo(fs):
	""" Determine Nfft and No from fs """
	dN = {#   fs:(Nfft,No)
		  10:(4096,3072), # for 1 Hz LPF (fsNew=10)
		  12:(2048,1024), # for 2 Hz LPF (fsNew=12)
		  50:(4096,2048), # for 6 Hz LPF (fsNew=50)
		62.5:(1024, 512),
		 250:(2048,   0),
		 500:(4096,   0),
		1000:(8192,   0)
	}
	Nfft,No = dN.get(fs, (False,False))
	if not Nfft: raise '\nunaccounted for sample rate = %f\n' % fs
	return Nfft,No

def printHeader(dHeader):
	""" print header fields & values """
	for k,v in dHeader.iteritems():
		typ = str(type(v))
		if typ == "<type 'dict'>":
		    	for sk,sv in v.iteritems():
				print "sHeader.%s%s='%s';" % (k, sk.capitalize(), sv)
		else:
			print "sHeader.%s='%s';" % (k, v)

def getAxisSuffix(d):
	""" Get suffix from WhichAx """	
	dSuffix = { 'xyz':'3' ,
	            'sum':'s' ,
	            'xxx':'x' ,
	            'yyy':'y' ,
	            'zzz':'z' }
	suffix = dSuffix.get(d['whichAx'],None)
	if not suffix:
		raise '\nunaccounted for whichAx suffix lookup with %s\n' % d['whichAx']
	else:
		return suffix

def getYearMonthPath(headerFile):
	""" get year/month subdir of path from headerFile name """
	headerFileName = split(headerFile, '/')[-1] # throw away path
	t = split(headerFileName,'_')
	return t[0],t[1]

def createMatlabScript(dHeader):
	""" print header fields & values to script file """
	h = parse(dHeader['headerFile'])
	L = ['SampleRate','CutoffFreq','Gain','DataQualityMeasure','SensorID','TimeZero','ISSConfiguration']
	for i in L:
		dHeader[i] = str(h.documentElement.getElementsByTagName(i)[0].childNodes[0].nodeValue)
	dHeader['DataType'] = str(h.documentElement.nodeName)
	dHeader['BiasCoeff'] = getSubfield(h,'BiasCoeff',['x','y','z'])
	dHeader['ScaleFactor'] = getSubfield(h,'ScaleFactor',['x','y','z'])
	Lcoord = ['x','y','z','r','p','w','name','time','comment']
	dHeader['SensorCoordinateSystem'] = getSubfield(h,'SensorCoordinateSystem',Lcoord)
	dHeader['DataCoordinateSystem'] = getSubfield(h,'DataCoordinateSystem',Lcoord)
	dHeader['GData'] = getSubfield(h,'GData',['format','file'])
	dHeader['year'],dHeader['month'] = getYearMonthPath(dHeader['headerFile'])
	if not dHeader['Nfft'] and not dHeader['No']:
		dHeader['Nfft'],dHeader['No'] = getNfftNo(float(dHeader['SampleRate']))
	elif dHeader['Nfft'] and not dHeader['No']:
		dHeader['Nfft'] = int(dHeader['Nfft'])
		dHeader['No'] = 0
	elif dHeader['Nfft'] and dHeader['No']:
		dHeader['Nfft'] = int(dHeader['Nfft'])
		dHeader['No']   = int(dHeader['No'])
	else:
	    raise '\nweird case with No defined, but not Nfft\n'

        # Create path/name for info m-file
	resPath = getoutput('echo ${RESULTSPATH}')				
        if dHeader.has_key('actualStart'):
                actualStart = float(dHeader['actualStart'])
        else:
                actualStart = stringTimeToUnix(dHeader['dateStart'])
        st = split(unixTimeToString(actualStart),'_')[:3]
        resPath += '/year' + st[0] + '/month' + st[1] + '/day' + st[2] + '/' + dHeader['sensor'] + '/padspec/' + dHeader['tag']
        strFs = dHeader['SampleRate'].replace('.','p')
	abbr = dHeader['abbr']
	pm = dHeader['pm']
	suff = getAxisSuffix(dHeader)
	infoFilename = '%s/m%s%s%s%s%sinfo.m' % (resPath,dHeader['SensorID'], abbr, suff, dHeader['tag'], strFs)

        if not os.path.isdir(resPath):
            cmd = 'mkdir -p ' + resPath
            res = getoutput(cmd) # os.mkdir(resPath) would not work because [is minus p supported?]
        if os.path.isfile(infoFilename):
            print 'not overwriting info script: %s' % infoFilename
            return
        if ( (len(infoFilename)-len(resPath))>33 ):
            print 'MATLAB may not read long script name %s (must be 32 chars or less)?' % infoFilename
        else:
            print 'writing info script: %s ...' % infoFilename,
        
	outfile = open(infoFilename,'w')
	print >> outfile, 'fs=%.3f;' % float(dHeader['SampleRate'])
	print >> outfile, 'fc=%.3f;' % float(dHeader['CutoffFreq'])
	print >> outfile, 'Nfft=%d;' % dHeader['Nfft']
	print >> outfile, 'No=%d;' % dHeader['No']
	print >> outfile, 'df=fs/Nfft;'
	print >> outfile, 'dT=(Nfft-No)/fs;'
	print >> outfile, 'f=0:fs/Nfft:fs/2;'
	print >> outfile, "sHeader.DataType='%s';" % dHeader['DataType']
	print >> outfile, "sHeader.SensorID='%s';" % dHeader['SensorID']
	print >> outfile, "sHeader.Gain='%.1f';" % float(dHeader['Gain'])
	print >> outfile, "sHeader.SampleRate=%.3f;" % float(dHeader['SampleRate'])
	print >> outfile, "sHeader.CutoffFreq=%.3f;" % float(dHeader['CutoffFreq'])
	print >> outfile, "sHeader.GDataFormat='%s';" % dHeader['GData']['format']
	print >> outfile, "sHeader.BiasCoeffX='%.2f';" % float(dHeader['BiasCoeff']['x'])
	print >> outfile, "sHeader.BiasCoeffY='%.2f';" % float(dHeader['BiasCoeff']['y'])
	print >> outfile, "sHeader.BiasCoeffZ='%.2f';" % float(dHeader['BiasCoeff']['z'])
	print >> outfile, "sHeader.SensorCoordinateSystemName='%s';" % dHeader['SensorCoordinateSystem']['name']
	print >> outfile, "sHeader.SensorCoordinateSystemRPY=[%.1f %.1f %.1f];" % (float(dHeader['SensorCoordinateSystem']['r']),
										   float(dHeader['SensorCoordinateSystem']['p']),
										   float(dHeader['SensorCoordinateSystem']['w']) )
	print >> outfile, "sHeader.SensorCoordinateSystemXYZ=[%.1f %.1f %.1f];" % (float(dHeader['SensorCoordinateSystem']['x']),
										   float(dHeader['SensorCoordinateSystem']['y']),
										   float(dHeader['SensorCoordinateSystem']['z']) )
	print >> outfile, "sHeader.SensorCoordinateSystemComment='%s';" % dHeader['SensorCoordinateSystem']['comment']
	print >> outfile, "sHeader.SensorCoordinateSystemTime='%s';" % dHeader['SensorCoordinateSystem']['time']
	print >> outfile, "sHeader.DataCoordinateSystemName='%s';" % dHeader['DataCoordinateSystem']['name']
	print >> outfile, "sHeader.DataCoordinateSystemRPY=[%.1f %.1f %.1f];" % (float(dHeader['DataCoordinateSystem']['r']),
										 float(dHeader['DataCoordinateSystem']['p']),
										 float(dHeader['DataCoordinateSystem']['w']) )
	print >> outfile, "sHeader.DataCoordinateSystemXYZ=[%.1f %.1f %.1f];" % (float(dHeader['DataCoordinateSystem']['x']),
										 float(dHeader['DataCoordinateSystem']['y']),
										 float(dHeader['DataCoordinateSystem']['z']) )
	print >> outfile, "sHeader.DataCoordinateSystemComment='%s';" % dHeader['DataCoordinateSystem']['comment']
	print >> outfile, "sHeader.DataCoordinateSystemTime='%s';" % dHeader['DataCoordinateSystem']['time']
	print >> outfile, "sHeader.DataQualityMeasure='%s';" % dHeader['DataQualityMeasure']
	print >> outfile, "sHeader.ISSConfiguration='%s';" % dHeader['ISSConfiguration']
	print >> outfile, "sHeader.ScaleFactorX='%.2f';" % float(dHeader['ScaleFactor']['x'])
	print >> outfile, "sHeader.ScaleFactorY='%.2f';" % float(dHeader['ScaleFactor']['y'])
	print >> outfile, "sHeader.ScaleFactorZ='%.2f';" % float(dHeader['ScaleFactor']['z'])
	print >> outfile, "sHeader.sdnDataStart=717673.5;"
	print >> outfile, "sHeader.sdnDataStart=888-1606;"
	print >> outfile, "sHeader.GUnits='g';"
	print >> outfile, "sHeader.TUnits='seconds';"
	print >> outfile, "sOutput.Type='imagefilebat';"
	print >> outfile, "sOutput.ResultsPath='/tmp/dummy/';"
	print >> outfile, "sPlot.WhichAx='%s';" % dHeader['whichAx']
	print >> outfile, "sPlot.TUnits='hours';"
	print >> outfile, "sPlot.TSpan=8;"
	print >> outfile, "sPlot.TempRes=df;"
	print >> outfile, "sPlot.FreqRes=dT;"
	print >> outfile, "sPlot.FLim=[0 fc];"
	print >> outfile, "sPlot.CLimMode='minmax';"
	print >> outfile, "sPlot.CLim=[-12 -6];"
	print >> outfile, "sPlot.Colormap='pimsmap';"
	print >> outfile, "sPlot.Window='hanning';"
	print >> outfile, "sPlot.TLimMode='auto';"
	print >> outfile, "sPlot.TTickLabelMode='dateaxis';"
	print >> outfile, "sPlot.TTickForm='hh:mm';"
	print >> outfile, "sPlot.OverlapLim=[1 50];"
	print >> outfile, "sPlot.AxWidth=NaN;"
	print >> outfile, "sPlot.AxHeight=NaN;"
	print >> outfile, "sPlot.Nfft=Nfft;"
	print >> outfile, "sPlot.No=No;"
	print >> outfile, "sPlot.P=0;"
	print >> outfile, "sPlot.TimeSlices=floor((3600*fs*sPlot.TSpan-No)/(Nfft-No));"
	print >> outfile, "sPlot.FrequencyBins=floor(fc/df);"
	print >> outfile, "sSearch.PathQualifiers.strTimeFormat='dd-mmm-yyyy,HH:MM:SS.SSS';"
	print >> outfile, "sSearch.PathQualifiers.strTimeBase='GMT';"
	print >> outfile, "sSearch.HeaderQualifiers='dummy';"
	print >> outfile, "sSearch.ModeDur='dummy';"
	s = split(dHeader['DataType'],'_')
	print >> outfile, "sText.casUL{1}=['%s, %s at ' sHeader.SensorCoordinateSystemComment ':' sprintf('[%%g %%g %%g]',sHeader.SensorCoordinateSystemXYZ)];" % (s[0], dHeader['SensorID'])
	print >> outfile, "sText.casUL{2}='%.2f sa/sec (%.2f Hz)';" % ( float(dHeader['SampleRate']),
									float(dHeader['CutoffFreq']) )
	print >> outfile, "sText.casUL{3}=['\Deltaf' sprintf(' = %.3f Hz, Nfft = %d',df,Nfft)];"
	print >> outfile, "sText.casUL{4}=sprintf('Temp. Res. = %.3f sec, No = %d',dT,No);"
	print >> outfile, "sText.strXType='Time';"
	print >> outfile, "sText.casYStub={'\Sigma'};"
	print >> outfile, "sText.strXUnits='hours';"
	print >> outfile, "sText.strComment='%s, %s';" % (s[0], dHeader['SensorID'])
	print >> outfile, "sText.casUR{1}=sHeader.ISSConfiguration;"
	print >> outfile, "sText.casUR{2}='sum';"
	print >> outfile, "sText.casUR{3}=sPlot.Window;"
	print >> outfile, "sText.casUR{4}=sprintf('%.2f hours',sPlot.TSpan);"
	print >> outfile, "sText.strTitle='Start GMT 01-Month-0000, 000/00:00:00.000';"
	print >> outfile, "sText.strVersion=' ';"
	#print >> outfile, "%%save('%s/%s','f','sHeader','sOutput','sPlot','sSearch','sText')" % (pth, infoFile)
	outfile.close()
        print 'done'

def getSubfield(h, field, Lsubs):
	""" Get sub fields using xml parser. """
	d = {}	
	for k in Lsubs:
		theElement = h.documentElement.getElementsByTagName(field)[0]
		d[k] = str(theElement.getAttribute(k))
	return d

def executeMatlabScript(dHeader):
	""" Call matlab script to create info.mat file. """
	# Now execute the info mat file creator
	cmd1 = r'\rm $HOME/.setupenv 2> /dev/null; . /usr/local/etc/setup.sh; setup matlab71 > /dev/null;'
	cmd2 = '%s nohup matlab -nosplash < %s > /tmp/matlabCreateOutput.txt' % (cmd1, dHeader['tempFile'])
	res2 = getoutput(cmd2)
	infoFile = dHeader['infoFile']
	cmd3 = r'chgrp pimsgrp %s; chmod g+rw %s' % (infoFile, infoFile)
	res3 = getoutput(cmd3)

def printSortedArgs(d):
	L = list(d.keys()); L.sort()
	for i in L: print '%20s = %s' % (i, d[i])
	print '~'*44

def showUsage(dHeader):
	"""print usage string with defaults"""
	print 'usage: creatematlabinfomatfile.py tempFile=/tmp/tempMfile.m headerFile=$h pm=+ abbr=spg tag=snellout'
	print  '      creatematlabinfomatfile.py tempFile=/tmp/tempMfile.m headerFile=$h pm=+ abbr=spg tag=snellout Nfft=1234'
	print  '      creatematlabinfomatfile.py tempFile=/tmp/tempMfile.m headerFile=$h pm=+ abbr=spg tag=snellout Nfft=1234 No=456'
	print  '\nvalues are:'
	L = list(dHeader.keys())
	L.sort()
	for i in L: print '%20s = %s' % (i, dHeader[i])

def hasProperField(dHeader,s):
	""" check for True header field, s """
	if not dHeader.get(s):
		showUsage(dHeader)
		raise '\nneed proper %s input\n' % s
	return 1

def specParamsOK(dHeader):
	""" check spectrogram parameters """
	L = ['abbr','tag','headerFile']
	for i in L:
		if hasProperField(dHeader,i): pass
	return 1

def createMfile(dHeader):
	""" Process header file into MATLAB script. """
	if specParamsOK(dHeader):
            createMatlabScript(dHeader)
        else:
            raise 'spec params error'

class Iterdir(object):
    def __init__(self, path, deep=False):
	self._root = path
	self._files = None
	self.deep = deep
    def __iter__(self):
	return self
    def next(self):
	if self._files:
	    join = os.path.join
	    d = self._files.pop()
	    r = join(self._root, d)
	    if self.deep and os.path.isdir(r):
		self._files += [join(d,n) for n in os.listdir(r)]
	elif self._files is None:
	    self._files = os.listdir(self._root)
	if self._files:
	    return self._files[-1]
	else:
	    raise StopIteration

def cmgProcessFile(f, offsetRecs=0, numRecs=None, elementsPerRec=4):
    """ process pad file per momentum disturbance discussion March 25, 2005 """
    uStart,joiner,uStop = fileTimeRange(f)
    print offsetRecs, numRecs, elementsPerRec
    data = readPadFile(f, offsetRecs=offsetRecs, numRecs=numRecs, elementsPerRec=elementsPerRec)

    print '(%s) %.3f ' % (split(f,os.path.sep)[-1], uStart),
    iMax = getMaxAbs(data)

##    zugmax = (10.0**6)*(data[iMax[-1],-1]) # for ossbtmf
##    print '%7.1f @ %d' % (zugmax,iMax[-1])

    zugmax = (10.0**6)*(data[iMax[-3],-3]) # for ossraw
    print '%7.1f @ %d' % (zugmax,iMax[-3])
    

if __name__ == '__main__':
    """ utils for pad processing """

    import copy
    from padpro import readPadFile
    
    print 'need better class of pad file reader functions (not readOssbtmf like in this example)'
    
    parameters = parseCommandLine(sys.argv)

    basePath  = '/mnt/yoda/pub/pad'
    subDir    = 'mams_accel_ossraw'
    sampleRate = 10
    
    dateStart = parameters['dateStart']
    dateStop  = parameters['dateStop']
    
    gg = FileGetterPad(basePath=basePath,subDir=subDir,dateStart=dateStart,dateStop=dateStop)

    # Do first file before looping through others
    f1 = gg.fileList[0]
    print gg.numCols
    cmgProcessFile(f1, offsetRecs=1, numRecs=2, elementsPerRec=gg.numCols)
    raise SystemExit
    
    
    hh = copy.deepcopy(gg)
    hh.fileList[-1] = hh.fileList[0]
    print gg
##    print hh
##    print gg.fileList
##    print hh.fileList
    count = 1
    for g in hh:
        uStart,joiner,uStop = fileTimeRange(g)
        data = readPadFile(g, offsetRecs=0, numRecs=None, elementsPerRec=6)
        #startOffsetSamples = 0
        #stopNumRecords = N.size(data,axis=0) # number of rows is axis=0 (cols is axis=1)

##        if count == 1:
##            startOffsetSamples,actualStart = startOffset(g,sampleRate,dateStart,dataColumns=6)
##        else if count == gg.numFiles:
##            stopNumRecords,actualStop = endNum(g,sampleRate,dateStop)
##        else:
##            startOffsetSamples = 0
            
##        print '(%s) %d %s' % (split(g,os.path.sep)[-1],startOffsetSamples,actualStart)
##        print '(%s) %d %s' % (split(g,os.path.sep)[-1],stopNumRecords,actualStop)
        
        print '(%s) %.3f ' % (split(g,os.path.sep)[-1], uStart),
        iMax = getMaxAbs(data)
        
##        zugmax = (10.0**6)*(data[iMax[-1],-1]) # for ossbtmf
##        print '%7.1f @ %d' % (zugmax,iMax[-1])
        
        zugmax = (10.0**6)*(data[iMax[-3],-3]) # for ossraw
        print '%7.1f @ %d' % (zugmax,iMax[-3])
