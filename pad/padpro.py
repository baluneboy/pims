#!/usr/bin/env python
version = '$Id'

###############################################################################
# Imports
import glob
import os, sys
import re
from stat import ST_SIZE
from padutils import *
from string import *
from commands import *
from collections import *
from math import *
import createheaderdict as chd
import numpy as np
import copy
from fraction import *
from interval import Interval, IntervalSet, BaseIntervalSet
import resample
import datetime
from fileglobber import FileGlobber #, FileGlobberIterUniqDirs
from datetimeranger import TimeRange
#import matplotlib.pyplot as plt

###############################################################################
# Inputs
defaults = { # required for padpro.py
    'padPath':'/misc/yoda/pub/pad',          # where to look for root of PAD file tree
    'spgPath':'/misc/yoda/www/plots/batch',  # where to look for root of spectrogram (roadmap) file tree
    'dateStart':'2012_07_01_00_00_00.000',   # first data time to process
    'dateStop': '2012_07_01_23_59_59.999',   # last data time to process
    'sensor':'121f02',                       # name of sensor to process (for legacy support, not part of the walker)
    'ignore':'quarantined|.*0bbd'            # rx for "root" matches to ignore LIKE "/misc/yoda/pub/pad/year2012/month07/day01/iss_rad_radgse"
}
parameters = defaults.copy()
#/misc/yoda/pub/pad/year2012/month07/day10/mma_accel_0bbd/2012_07_10_18_33_52.000-2012_07_10_18_43_51.999.0bbd.header
def readPadFile(padFile,offsetRecs=0,numRecs=None,elementsPerRec=4):
    """ read binary PAD file and return data as numarray """
    import array # need array module for fromfile function
    from stat import ST_SIZE
    # initialize array of floats
    data = array.array('f')
    f = open(padFile, mode='rb')
    f.seek(int(offsetRecs*elementsPerRec*4)) # offset into file
    if not numRecs:
        fileBytes = os.stat(padFile)[ST_SIZE]
        data.fromfile(f,fileBytes/4)            # read to end of file
    else:
        data.fromfile(f,numRecs*elementsPerRec) # read numRecs of file
    f.close()
    d = np.array(data,dtype=float)      # initialize output array
    d = np.reshape(d,((len(data)/elementsPerRec),elementsPerRec)) # reshape array
    return d
    
def stripExtension(p):
    """strip extension from pathname p"""
    return os.path.splitext(p)[0]

class ProductFileGlobber(FileGlobber):
    """derived class with helpful attributes"""
    def __init__(self, sensor, product, year, month, day, hour, suffix, abbrev, numExpect, basePath='/misc/yoda/www/plots/batch', fileWild='*.pdf', skipDirWildList=['quarantined','trash']):
        bp = os.path.join(basePath, 'year%4d' % year, 'month%02d' % month, 'day%02d' % day)
        #YYYY_MM_DD_HH_00_00.000_SENSOR+SUFFIX_ABBREV_roadmaps*.pdf
        fw = '%4d_%02d_%02d_%02d_00_00.000_%s%s_%s_roadmaps*.pdf' % ( year, month, day, hour, sensor, suffix, abbrev)
        super(ProductFileGlobber,self).__init__(basePath=bp, fileWild=fw, skipDirWildList=skipDirWildList)
        self.sensor = sensor
        self.product = product
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.suffix = suffix
        self.abbrev = abbrev
        self.numExpect = numExpect

class ProductFileGlobberDay(FileGlobber):
    """derived class with helpful attributes"""
    def __init__(self, sensor, product, year, month, day, suffix, abbrev, numExpect, basePath='/misc/yoda/www/plots/batch', fileWild='*.pdf', skipDirWildList=['quarantined','trash']):
        bp = os.path.join(basePath, 'year%4d' % year, 'month%02d' % month, 'day%02d' % day)
        if not os.path.exists(bp):
            self.fileList = []
            self.fileWild = 'NOT_EXIST_%s' % bp
            return
        #YYYY_MM_DD_*_00_00.000_SENSOR+SUFFIX_ABBREV_roadmaps*.pdf
        fw = '%4d_%02d_%02d_*_00_00.000_%s%s_%s_roadmaps*.pdf' % ( year, month, day, sensor, suffix, abbrev)
        super(ProductFileGlobberDay,self).__init__(basePath=bp, fileWild=fw, skipDirWildList=skipDirWildList)
        self.sensor = sensor
        self.product = product
        self.year = year
        self.month = month
        self.day = day
        self.suffix = suffix
        self.abbrev = abbrev
        self.numExpect = numExpect

class PadIntervalException( Exception ): pass
class PadIntervalSampleRateException( PadIntervalException ): pass
# put other PadInterval Exception subclasses here

class PadBaseIntervalSet(BaseIntervalSet):
    """Base class for PadIntervalSet. """

    def _add(self, obj):
        """Appends an PadInterval or PadBaseIntervalSet to the object. """
        if isinstance(obj, PadInterval):
            r = obj
        else:
            r = PadInterval.equal_to(obj)

        if r:   # Don't bother appending an empty PadInterval
            # If r continuously joins with any of the other
            newIntervals = []
            for i in self.intervals:
                if i.overlaps(r) or i.adjacent_to(r):
                    #print i.upper_bound.strftime('%Y_%m_%d_%H_%M_%S.%f'), "overlaps or is adjacent to"
                    #print r.lower_bound.strftime('%Y_%m_%d_%H_%M_%S.%f')                    
                    r = r.join(i)
                else:
                    #print i.upper_bound.strftime('%Y_%m_%d_%H_%M_%S.%f'), "DOES NOT overlap or NOT adjacent to"
                    #print r.lower_bound.strftime('%Y_%m_%d_%H_%M_%S.%f')                      
                    newIntervals.append(i)
            newIntervals.append(r)
            self.intervals = newIntervals
            self.intervals.sort()

class PadIntervalSet(PadBaseIntervalSet):
    """ The PAD [cheap filename-based] version of IntervalSet. """
    
    def __init__(self, items=[]):
        """ Initializes the PadIntervalSet. """
        PadBaseIntervalSet.__init__(self, items)

    def add(self, obj):
        """Adds an Interval or discrete value to the object."""
        if len(self.intervals) == 0:
            self.sampleRate = obj.sampleRate
        else:
            pass
        PadBaseIntervalSet._add(self, obj)

class PadInterval(Interval):
    """class based on Interval; adds convenience methods and overrides adjacent_to method"""
    def __init__(self, *args, **kwargs):
        #super(PadInterval,self).__init__(*args, **kwargs) ## SEE PYTHON NEW-STYLE CLASS ISSUE
        if 'sampleRate' not in kwargs:
            self.sampleRate = 0.0
            self.timeStep = sys.float_info.max
        else:
            self.sampleRate = kwargs['sampleRate']
            self.timeStep = 1.0/self.sampleRate
            del kwargs['sampleRate']
        Interval.__init__(self, *args, **kwargs)

    def __and__(self, other):
        """intersection of two PadIntervals"""
        result = super(PadInterval,self).__and__(other)
        return PadInterval(result.lower_bound,result.upper_bound)

    def join(self, other):
        """Combines two continous PadIntervals. """
        if self.overlaps(other) or self.adjacent_to(other):
            if self.lower_bound < other.lower_bound:
                lbound = self.lower_bound
                linc = self.lower_closed
            elif self.lower_bound == other.lower_bound:
                lbound = self.lower_bound
                linc = max(self.lower_closed, other.lower_closed)
            else:
                lbound = other.lower_bound
                linc = other.lower_closed
    
            if self.upper_bound > other.upper_bound:
                ubound = self.upper_bound
                uinc = self.upper_closed
            elif self.upper_bound == other.upper_bound:
                ubound = self.upper_bound
                uinc = max(self.upper_closed, other.upper_closed)
            else:
                ubound = other.upper_bound
                uinc = other.upper_closed

            assert self.sampleRate == other.sampleRate
            return PadInterval(lbound, ubound, upper_closed=uinc, lower_closed=linc, sampleRate=self.sampleRate)

        else:
            raise ArithmeticError("The PadIntervals are disjoint.")   
   
    def getSpanSeconds(self):
        """span between lower_bound & upper_bound in seconds"""
        dtm = self.upper_bound - self.lower_bound
        if dtm.days != 0:
            raise('unhandled case when PadInterval spans a day or more')
        return dtm.seconds + dtm.microseconds/1.0e6
   
    def extends_beyond(self, other):
        """tells whether self interval extends beyond other interval on both ends
        self extends_beyond other when self's lower bound is less 
        than other's lower bound AND self's upper bound is greater
        than other's upper bound
        """
        if self == other:
            result = False
        elif ( self.lower_bound < other.lower_bound ) and ( self.upper_bound > other.upper_bound ):
            result = True
        else:
            result = False
        return result
    
    def comes_after(self, other):
        """tells whether an interval lies after the object
        self comes after other when sorted if its lower bound is greater 
        than other's upper bound
        """
        if self == other:
            result = False
        elif self.lower_bound > other.upper_bound:
            result = True
        else:
            result = False
        return result    

    def gapSeconds(self, other):
        """ return gap in seconds; NOTE: python2.7 has timedelta.total_seconds() """
        assert other.lower_bound > self.upper_bound        
        gap = other.lower_bound - self.upper_bound
        return gap.seconds + (gap.microseconds / 1e6) + (gap.days * 86400)        

    def adjacent_to(self, other):
        """ Tells whether a PadInterval is adjacent to other object without overlap (i.e. WITHIN SAMPLE RATE). """
        if self.sampleRate != other.sampleRate:
            msg = 'The sample rate %7.2f does not match expected value of %7.2f.' %(other.sampleRate, self.sampleRate)
            raise PadIntervalSampleRateException(msg)
        if self.comes_before(other):
            if self.upper_bound == other.lower_bound:
                result = (self.upper_closed != other.lower_closed)
            else:
                result = False
            gap = self.gapSeconds(other)
            if gap <= (1.01*self.timeStep):
                result = True # this is where we deal with sampleRate for adjacency
        elif self == other:
            result = False
        else:
            result = other.adjacent_to(self)
        #if not result:
        #    print '--- NON-ADJACENT ---'            
        #    print self
        #    print other
        #    print gap
        #    print ''
        return result

class PadDaySensor(object):
    def __init__ (self, sensorPath, numDayParts=3):
        """initialize PadDaySensor object (this can be a better class...not just day -- maybe dayRange)"""
        # FIXME can we abstract this for arbitrary time intervals without regard for DAY (ymd directory) boundaries
        # TODO get self.date = FROM sensorPath
        self._inputsOkay(sensorPath, numDayParts)
        self.sensor = split(self.sensorPath,'_')[-1]
        self.properlyPairedHeaderFiles = self.getProperlyPairedHeaderFiles()

    def _inputsOkay(self, sensorPath, numDayParts):
        # verify numDayParts is integer greater than zero
        if not (numDayParts==int(numDayParts) and numDayParts>0):
            print '*** Abort because numDayParts is not an integer greater than zero'
            sys.exit(-1)
            
        #  verify sensor path exists
        if not os.path.exists(sensorPath):
            print '*** Abort because sensorPath "%s" does not exist' % sensorPath
            sys.exit(-1)

        #  verify sensor path matches template pattern LIKE "/some/leading/path/year2012/month07/day01/sys_{accel,rad}_sensor"
        pat = '.*/year(?P<year>\d{4})/month(?P<month>\d{2})/day(?P<day>\d{2})/.*_accel_\w+$'
        if not re.match(pat,sensorPath):
            print '*** Abort because sensorPath "%s" does not match pattern "%s"' % (sensorPath, pat)
            sys.exit(-1)
        c = re.compile(pat)
        ma = c.search(sensorPath)
        y = int(ma.group('year'))
        m = int(ma.group('month'))
        d = int(ma.group('day'))
            
        # extract date from sensor path
        date = datetime.date(y,m,d) # date that corresponds to sensorPath's ymd part
        
        # TODO:
        #  3. get files list (wastefully ignoring what the walker did) <<<  WE SHOULD PROBABLY NOT USE WALKER THEN AND JUST GLOB PATTERN TO GET HERE
        
        self.sensorPath = sensorPath
        self.date = date
        self.numDayParts = numDayParts
    
    def getProperlyPairedHeaderFiles(self):
        # FIXME decision point (abandon the walker and go with header file list for THIS sensorPath)
        fileList = [os.path.join(self.sensorPath,name) for name in files if name.endswith('.header') and os.path.exists(os.path.join(self.sensorPath,name.replace('.header','')))]
        fileList.sort()
        return fileList
    
    def __str__(self):
        return 'sensorPath = %s, sensor = %s' % (self.sensorPath, self.sensor)


class PadYmdWalker(object):
    def __init__ (self, year, month, day, padPath='/misc/yoda/pub/pad', ignore='quarantined|junk', numDayParts=3, spgPath='/misc/yoda/www/plots/batch'):
        """initialize PadYmdWalker object"""
        self.padPath = padPath
        self.year = year
        self.month = month
        self.day = day
        self.ignore = ignore
        self.datetime = datetime.datetime(year,month,day,0,0,0)
        self.numDayParts = numDayParts
        self.padPath = os.path.join(padPath, 'year%4d' % year, 'month%02d' % month, 'day%02d' % day) # FIXME change to self.ymdPath
        self.spgPath = os.path.join(spgPath, 'year%4d' % year, 'month%02d' % month, 'day%02d' % day)
        self.walkSensorSubdirs()

    def getFileAndIntervalInfo(self,padFileName):
        """extract info from pad filename: (sensor, bytes, seconds, interval)"""
        phf = PadHeaderFile(padFileName)
        basePath,padFileName = os.path.split(padFileName)
        # FIXME the next few lines are quite hideous
        padFileName = split(padFileName, '.header')[0] # throw away '.header' suffix
        sensor =  split(padFileName, '.')[-1]
        padFileName = join(split(padFileName, '.')[:-1], '.')
        pair = split(padFileName, '-') # joiner is a minus
        if len(pair) == 1: pair = split(padFileName, '+') # in case joiner is a plus
        dtStart = datetime.datetime.strptime(pair[0],'%Y_%m_%d_%H_%M_%S.%f')
        dataBytes = resample.fileSize(os.path.join(basePath,padFileName+'.'+sensor))
        dataSeconds = (dataBytes/4.0/phf.ElementsPerRec-1.0)/phf.SampleRate
        dtStop = dtStart + datetime.timedelta(dataSeconds/86400.0)
        smallInterval = PadInterval(dtStart,dtStop)
        return sensor, dataBytes, dataSeconds, smallInterval

    def processHeaderFileList(self, largeInterval, sensorFromDir):
        #self.showHeaderFileList()        
        filesToRemove = []
        spanLargeSecs = largeInterval.getSpanSeconds()
        
        count = 0
        cumSumSecsBytes = np.array([0.0, 0.0])
        for f in self.properlyPairedHeaderFiles:
            count += 1
            sensor,dataBytes,dataSeconds,smallInterval = self.getFileAndIntervalInfo(f)
            
            if sensor != sensorFromDir:
                raise('unhandled case when a pad file yields sensor string (%s) that does not match dir (%s)' % (sensor,sensorFromDir))
                
            overlap = smallInterval & largeInterval
            #sensorSecsBytes = PadSensorDict()
            #sensorSecsBytes[sensor] = np.array([dataSeconds,dataBytes])
            
            spanOverlapSecs = 0.0
            numOverlapBytes = 0.0          
            if not smallInterval.overlaps(largeInterval):                   # SMALL TOTALLY OUTSIDE LARGE
                if smallInterval.comes_before(largeInterval):               # SMALL TOTALLY COMES BEFORE LARGE
                    msg = "xBEF"
                    filesToRemove.append(f)
                else:                                                       # SMALL TOTALLY COMES AFTER LARGE
                    msg = " AFT"
            
            elif smallInterval.extends_beyond(largeInterval):               # SMALL EXTENDS BEYOND LARGE ON BOTH ENDS
                msg = " EXB"
            
            elif smallInterval in largeInterval:                            # SMALL TOTALLY INSIDE LARGE
                msg = "xOLT"
                spanOverlapSecs = overlap.getSpanSeconds()
                numOverlapBytes = np.floor(dataBytes*spanOverlapSecs/dataSeconds)
                #self.sensorSumSecsBytes = self.sensorSumSecsBytes + sensorSecsBytes
                filesToRemove.append(f)
            
            elif smallInterval.overlaps(largeInterval):                     # SMALL PARTIALLY OVERLAPS LARGE
                if smallInterval.lower_bound < largeInterval.lower_bound:   # SMALL PARTIALLY OVERLAPS LARGE ON LEFT
                    msg = "xOLL"
                    spanOverlapSecs = overlap.getSpanSeconds()
                    numOverlapBytes = np.floor(dataBytes*spanOverlapSecs/dataSeconds)
                    #self.sensorSumSecsBytes = self.sensorSumSecsBytes + sensorSecsBytes
                    filesToRemove.append(f)
                else:                                                       # SMALL PARTIALLY OVERLAPS LARGE ON RIGHT
                    msg = " OLR"
                    spanOverlapSecs = overlap.getSpanSeconds()
                    numOverlapBytes = np.floor(dataBytes*spanOverlapSecs/dataSeconds)
                    #self.sensorSumSecsBytes = self.sensorSumSecsBytes + sensorSecsBytes
                    
            else:
                raise('unhandled case when comparing smallInterval, %s, to largeInterval, %s' % (smallInterval,largeInterval))
            
            cumSumSecsBytes = cumSumSecsBytes + np.array([spanOverlapSecs, numOverlapBytes])
            #print "FILE %3d IS %s %s %.3f %d %.3f %d" % (count, msg, f, spanOverlapSecs, numOverlapBytes, cumSumSecsBytes[0], cumSumSecsBytes[1])
            
        for r in filesToRemove:
            self.properlyPairedHeaderFiles.remove(r)
        self.properlyPairedHeaderFiles.sort()
 
        return cumSumSecsBytes
 
    def walkSensorSubdirs(self):
        # NOTE: at this point, root is LIKE "/misc/yoda/pub/pad/year2012/month07/day01/iss_rad_radgse"
        for root, dirs, files in os.walk(self.padPath): # FIXME when rename above is done this should become self.ymdPath as arg to walk
            # Some things to ignore
            if root == self.padPath or re.match(self.ignore, root):
                #print 'IGNORE %s BECAUSE ITS TOPMOST or MATCHES "%s"' % (root, self.ignore)
                continue

            self.properlyPairedHeaderFiles = [os.path.join(root,name) for name in files if name.endswith('.header') and os.path.exists(os.path.join(root,name.replace('.header','')))]
            self.properlyPairedHeaderFiles.sort()
            sensorFromDir = split(root,'_')[-1]
            
            # FIXME some of the above few lines get moved into this new object!
            p = PadDaySensor(root, numDayParts=self.numDayParts) # root is full pad path to sensor subdir
            sys.exit(0)
            
            daySumSecsBytes = np.array([0.0, 0.0])
            hrs = np.zeros(self.numDayParts)
            numPadFilePairs = len(self.properlyPairedHeaderFiles) # note that this list gets changed as we go
            #print "%s has %d PAD pairs" % ( root, numPadFilePairs)
            if numPadFilePairs > 0:
                
                # FIXME this could be moved into the "day parts" for loop to get per-eight-hour-ish breakout
                #       using int(dt1.strftime('%H')) for hour part as part of fileWild
                pfg = ProductFileGlobberDay(sensorFromDir, 'pdfSpgDef', self.year, self.month, self.day, '', 'spg*', 1)
                #wildPathSpgDef = os.path.join(self.spgPath,'%4d_%02d_%02d_%s_00_00.000_%s_spg*_roadmaps*.pdf' % (self.year, self.month, self.day, dt1.strftime('%H'), sensorFromDir))
                #numPdfsDef = len(glob.glob(wildPathSpgDef))
                wildPathSpgDef = pfg.fileWild
                numPdfsDef = len(pfg.fileList)
                #print numPdfsDef, wildPathSpgDef
                
                wildPathSpgTen = os.path.join(self.spgPath,'%4d_%02d_%02d_*_00_00.000_%sten_spg*_roadmaps*.pdf' % (self.year, self.month, self.day, sensorFromDir))
                numPdfsTen = len(glob.glob(wildPathSpgTen))
                #print numPdfsTen, wildPathSpgTen
                
                wildPathSpgOne = os.path.join(self.spgPath,'%4d_%02d_%02d_*_00_00.000_%sone_spg*_roadmaps*.pdf' % (self.year, self.month, self.day, sensorFromDir))
                numPdfsOne = len(glob.glob(wildPathSpgOne))
                #print numPdfsOne, wildPathSpgOne
                    
                for ind in range(self.numDayParts):
                    dt1 = self.datetime + datetime.timedelta(float(ind)/self.numDayParts)
                    dt2 = self.datetime + datetime.timedelta(float(ind+1)/self.numDayParts)
                    largeInterval = PadInterval(dt1, dt2, upper_close=False)
                    partSumSecsBytes = self.processHeaderFileList(largeInterval,sensorFromDir)
                    daySumSecsBytes = daySumSecsBytes + partSumSecsBytes
                    hrs[ind] = partSumSecsBytes[0]/3600.0
                    msgInterval = "  interval from %s to %s gives %7.4f hours and %7.2f MB" % ( dt1, dt2, partSumSecsBytes[0]/3600.0, partSumSecsBytes[1]/1024.0/1024.0)
                    #print "%s" % msgInterval
            #msgDay = "TOTALS FOR %s ON %s ARE %7.4f hours and %7.2f MB" % (sensorFromDir, dt1.strftime('%Y-%m-%d'), daySumSecsBytes[0]/3600.0, daySumSecsBytes[1]/1024.0/1024.0)
            #print "%s" % msgDay.rjust(len(msgInterval))
            
            msgDay = "%s, %10s, %4d, %s, %7.4f, %8.2f, %2d, %2d, %2d" % (dt1.strftime('%Y-%m-%d'),
                                                                 sensorFromDir,
                                                                 numPadFilePairs,
                                                                 str(hrs),
                                                                 daySumSecsBytes[0]/3600.0,
                                                                 daySumSecsBytes[1]/1024.0/1024.0,
                                                                 numPdfsDef,
                                                                 numPdfsTen,
                                                                 numPdfsOne )
            print "%s" % msgDay
                        
    def showHeaderFileList(self):
        count = 0
        print "HEADER FILE LIST (%d FILES):" % len(self.properlyPairedHeaderFiles)
        for f in self.properlyPairedHeaderFiles:
            count += 1
            print "FILE %3d IS %s" % (count, f)

class PadFile(object):
    """PIMS Acceleration Data (PAD) object created from file, like this: p = PadFile(filename)""" 
    def __init__ (self,filename,offsetRecs=0,numRecs=None,elementsPerRec=4):
        """initialize PadFile object"""
        self.filename = filename
        self.header = PadHeaderFile(filename)
        self.data = readPadFile(filename,offsetRecs,numRecs,elementsPerRec)
        self.dateStart = stringTimeToUnix(os.path.basename(filename)[:23]) + (offsetRecs/self.header.SampleRate)
        self.dateStop = self.dateStart + ((len(self.data)-1)/self.header.SampleRate)
        self.interval = Interval(self.dateStart,self.dateStop)
        
    def __str__(self):
        s  = '\n filename: %s' % self.filename
        s += '\ndateStart: %s' % unixTimeToString(self.dateStart)
        s += '\n dateStop: %s' % unixTimeToString(self.dateStop)
        #s += '\n interval: %s' % str(self.interval)
        s += '\n*** header %s' % (44*'*')
        s += '\n%s' % str(self.header)
        s += '\n***  data: [ length is %d ] %s' % (len(self.data),22*'*')
        s += '\n%s' % str(self.data)
        return s

    def __len__(self):
        return len(self.data)

    def __sub__(self,other):
        """ return gap filled with relative time column and NaN xyz values (or overlap neg. number of pts) """
        # (f2-f1); where self is f2; & other is f1
        if self.header != other.header:
            raise RuntimeError, 'incompatible headers'
        gap = copy.copy(self)
        fs = gap.header.SampleRate
        t0 = other.dateStart
        t1 = other.dateStop
        t2 = self.dateStart
        t3 = self.dateStop
        N = int(round((t2 - t1) * fs)) - 1
        if t2 < t0:
            print '2nd chunk start:', unixTimeToString(t2), 'verbatim from', self.filename
            print '1st chunk start:', unixTimeToString(t0), 'computed from', other.filename
            raise RuntimeError, '2nd chunk starts BEFORE 1st'
        elif ( (t2 >= t0) and (t3 <= t1) ):
            print '1st chunk start:', unixTimeToString(t0), 'computed from', other.filename
            print '2nd chunk start:', unixTimeToString(t2), 'verbatim from', self.filename
            print '2nd chunk  stop:', unixTimeToString(t3)
            print '1st chunk  stop:', unixTimeToString(t1)
            raise RuntimeError, '2nd chunk is SUBSET of first'
        elif t0 <= t2 <= t1:
            print '\n---PAD Overlap---\n'
            return N
        gap.dateStart = t1 + (1.0 / fs)
        gap.dateStop = gap.dateStart + ((N - 1) / fs)
        newFilename = "%sG%s.%s" % (unixTimeToString(gap.dateStart),unixTimeToString(gap.dateStop),gap.header.SensorID)
        gap.filename = os.path.join(os.path.dirname(gap.filename),newFilename)
        # create time column & NaN array for gap's xyz
        T = np.arange(0,(N+1.0)/fs,(1.0/fs))  # overshoot to get around arange issue
        t = np.reshape(T[:N],(N,1))           # truncate at needed number of pts (N)
        xyz = np.zeros((N,3),np.Float32) + (1e333333/1e333333) # Better way to get NaN array?
        gap.data = np.concatenate((t,xyz),1) # horizontal concatenation
        return gap

    def __add__(self,other):
        """ return concatenation """
        if self.header != other.header:
            print 'incompatible headers'
            return None
        gap = other - self # other is after (larger time than) self, so subtract the smaller (self)
        new = copy.copy(self)
        fs = new.header.SampleRate
        newLen = len(self) + len(gap) + len(other)
        new.dateStop = self.dateStart + (newLen - 1.0) / fs
        newFilename = "%sJ%s.%s" % (unixTimeToString(new.dateStart),unixTimeToString(new.dateStop),new.header.SensorID)
        new.filename = os.path.join(os.path.dirname(new.filename),newFilename)
        # create time column & vertically concatenated xyz columns
        t = np.arange(0,newLen/fs,(1.0 / fs),shape=(newLen,1))
        xyz = np.concatenate((self.data[:,1:4],gap.data[:,1:4],other.data[:,1:4]),0)
        new.data = np.concatenate((t,xyz),1)
        return new

class PadHeaderFile(object):
    """
    PIMS Acceleration Data (PAD) header object created from header file
    like this: h = PadHeaderFile(filename)
    """

    def __init__ (self,filename):
        """ initialize PadHeaderFile """
        if split(filename,'.')[-1] != 'header': filename += '.header'
        dHeader = chd.main(['headerFile=' + filename])    # get header dict
        for k,v in dHeader.iteritems(): setattr(self,k,v) # this does dynamic set attribute
        self.SampleRate = float(self.SampleRate)
        self.CutoffFreq = float(self.CutoffFreq)
        # parse coord sys info from subdict and convert xyz/rpy to float numarrays
        for coord in ['SensorCoordinateSystem','DataCoordinateSystem']:
            self.parseCoord(['x','y','z'],coord)
            self.parseCoord(['r','p','w'],coord)
        self.ElementsPerRec = int(self.ElementsPerRec)
        self.filename = filename
        
    def __str__(self):
        s  = '\n  DataType: %s' % self.DataType
        s += '\n  SensorID: %s' % self.SensorID
        s += '\nSampleRate: %7.2f sa/sec' % self.SampleRate
        s += '\nCutoffFreq: %7.2f Hz' % self.CutoffFreq
        s += '\nElemPerRec: %7d' % self.ElementsPerRec
        s += '\n%s' % self.showCoordSys('Data')
        s += '\n%s' % self.showCoordSys('Sensor')
        return s

    def __cmp__(self, other):
        """ compare instances of PadHeaderFile (see http://www.python.org/doc/current/ref/customization.html) """
        for a in ['DataType','SensorID','SampleRate','CutoffFreq']:
            if getattr(self,a) != getattr(other,a):
                print '??? %s mismatch ???' % a
                return cmp(getattr(self,a),getattr(other,a))
        for c in ['Data','Sensor']:
            for ax in ['Name','Comment']:
                A = getattr(self ,c + 'CoordinateSystem' + ax)
                B = getattr(other,c + 'CoordinateSystem' + ax)
                if A != B:
                    print '??? %sCoordinateSystem%s mismatch ???' % (c,ax)
                    return cmp(A,B)
            for ax in ['XYZ','RPW']:
                S = getattr(self ,c + 'CoordinateSystem' + ax)
                H = getattr(other,c + 'CoordinateSystem' + ax)
                if not np.alltrue(S == H):
                    print '??? %sCoordinateSystem%s mismatch ???' % (c,ax)
                    return -1
        return 0

    def getTimeRangeFromName(self):
        """ get 'cheap' time range from header filename """
        tr = TimeRange(self.filename)
        return tr.start, tr.stop

    def parseCoord(self,L,coord):
        """ parse dict and convert xyz or rpy into float numarray """
        dCoord = getattr(self,coord)
        Lxyz = []
        for ax in L:
            Lxyz.append(float(dCoord.__getitem__(ax)))
        xyz = np.array(Lxyz,dtype=float)
        S = reduce(lambda x,y: x+y, L)
        setattr(self,coord + upper(S),xyz)
        setattr(self,coord + 'Name',dCoord['name'])
        setattr(self,coord + 'Comment',dCoord['comment'])

    def showCoordSys(self,s):
        """ show coord sys """
        t  = '\n--------------------'
        t += '\n%33s: %s' % (s + 'CoordinateSystemName',getattr(self,s + 'CoordinateSystemName'))
        t += '\n%33s: %s' % (s + 'CoordinateSystemComment',getattr(self,s + 'CoordinateSystemComment'))
        t += '\n%33s:' % (s + 'CoordinateSystemXYZ')
        t += '[%7.2f %7.2f %7.2f] in.' % tuple(getattr(self,s + 'CoordinateSystemXYZ'))
        t += '\n%33s:' % (s + 'CoordinateSystemRPY')
        t += '[%7.2f %7.2f %7.2f] deg.' % tuple(getattr(self,s + 'CoordinateSystemRPW'))
        return t

class PadPrimer(object):
    """PIMS Acceleration Data (PAD) 'primer' object created from data (not header) file, like this: p = PadPrimer(filename)"""

    def __init__ (self,filename,dataColumns):
        """initialize PadPrimer object"""
        self.filename = filename
        self.dataColumns = dataColumns
        self.fileBytes = os.stat(filename)[ST_SIZE]
        self.fileRecs = round(self.fileBytes / (dataColumns * 4.0),1)
        ut1,j,ut2 = resample.fileTimeRange(filename)
        #print ut2, "-", ut1
        self.spanSeconds = ut2-ut1

    def __str__(self):
        s   = '   filename: %s' % self.filename
        s  += '\ndataColumns: %s' % self.dataColumns
        s  += '\n  fileBytes: %9d' % self.fileBytes
        s  += '\n   fileRecs: %9d' % self.fileRecs
        s  += '\nspanSeconds: %9d' % self.spanSeconds
        return s

    def __len__(self):
        return self.fileRecs

def processData():
    """get pad files prescribed by inputs and do WHAT?"""
    
    padPath = parameters['padPath']
    dateStart = parameters['dateStart']
    dateStop = parameters['dateStop']
    sensor = parameters['sensor']

    # Get list of pad header files that cover span of interest
    padHeaderFiles,sampleRate,dataColumns = getPadHeaderFiles(padPath,dateStart,dateStop,sensor)
    
    # Strip ".header" from header files & put results in double-ended queue
    padFiles = deque(map(stripExtension,padHeaderFiles))
    if len(padFiles) == 0:
        print 'no pad files'
        raise SystemExit
    print 'Found %d PAD files that cover span of interest for sensor "%s".' % (len(padFiles),sensor)
    pts,dur = [],[]
    
    # Initialize with first header file
    p1 = PadPrimer(padFiles.popleft(),dataColumns)
    print "first file is:", p1.filename, "with", p1.fileRecs, "records"
    print p1.spanSeconds, "seconds"
    
    while len(padFiles) > 0:
        p = PadPrimer(padFiles.popleft(),dataColumns)
        print " this file is:", p.filename, "with", p.fileRecs, "records"
        print p.spanSeconds, "seconds"

    raise SystemExit
 
    # Now process the rest of the header files   
    for i in range(0,len(padFiles)-1):
        f1 = split(padFiles[i],'.header')[0]
        f2 = split(padFiles[i+1],'.header')[0]
        fileBytes = os.stat(f1)[ST_SIZE]
        fileRecs = fileBytes / (dataColumns * 4.0)
        p = PadFile(f1,offsetRecs=fileRecs-5,numRecs=5) #  last 5 records in f1
        q = PadFile(f2,offsetRecs=0,numRecs=5)          # first 5 records in f2
        print unixTimeToString(p.dateStop)
        print unixTimeToString(q.dateStart)
        #print p
        #print q
        #raise SystemExit
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        # FIXME this try/except is letting RuntimeError(s) get through!
        try:
            ptsGap = len(q-p)
            pts.append(ptsGap)
            dur.append(float(ptsGap)/p.header.SampleRate)
            print '%4d,%7.3f' % (ptsGap,float(ptsGap)/p.header.SampleRate)
        except:
            #print f1
            #print f2
            print '??? %.3f sec.\n' % (p.dateStop-q.dateStart)
##            print p
##            print q
##            raise SystemExit
##        s = p + q
##        print s
    pts.sort()
    dur.sort()
    print 'Median number of points: %.3f' % np.median(pts)
    print 'Median duration in secs: %.3f' % np.median(dur)
    print 'done'
    raise SystemExit

##    from matplotlib.matlab import *
##    q = PadFile(sys.argv[1],offsetRecs=0,numRecs=3)
##    print unixTimeToString(q.dateStart)
##    print unixTimeToString(q.dateStop)
##    print q.data
##    q = PadFile(sys.argv[1])
##    print unixTimeToString(q.dateStart)
##    print unixTimeToString(q.dateStop)
##    print q.data

##    plot(q.data[:,1],q.data[:,2])
##    from matplotlib import mlab
##    padFile=sys.argv[1]
##    d = readPadFile(padFile,numRecs=512,offsetRecs=3)
##    print d
##    pxx,f = mlab.psd(d[:,1])
##    print pxx[:11], f[:11]
##    sys.exit()


def parametersOK():
    """check for reasonableness of parameters entered on command line"""
    #print 'INPUTS'
    #print 'padPath  :', parameters['padPath']
    #print 'dateStart:', parameters['dateStart'] #, '(', stringTimeToUnix(parameters['dateStart']) ,'sec )'
    #print 'dateStop :', parameters['dateStop']  #, '(', stringTimeToUnix(parameters['dateStop']) ,'sec )'
    #print 'sensor   :', parameters['sensor']

    # TODO put sanity/other checks here, but for now anything goes...
    if not os.path.exists(parameters['padPath']):
        print '*** Abort because padPath = "%s" does not exist' % parameters['padPath']
        return 0
    return 1 # one for all OK; otherwise, return zero

def printUsage():
    """print short description of how to run the program"""
    print version
    print 'usage: padpro.py [options]'
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '            %s=%s' % (i, defaults[i])

def demoRead():
    padFile = '/misc/yoda/pub/pad/year2012/month02/day01/sams2_accel_121f03/2012_02_01_00_08_39.413+2012_02_01_00_09_51.264.121f03'
    offsetRecs = 0
    numRecs = 100
    elementsPerRec = 4
    d = readPadFile(padFile,offsetRecs=0,numRecs=None,elementsPerRec=4)
    print d
    
    # start with a rectangular Figure
    plt.figure(1, figsize=(18,15))
    
    ax = plt.axes()
    
    # the scatter plot
    ax.plot(d[:,0], d[:,1])
    plt.show()    
    
if __name__ == '__main__':
    """ utils for pad processing """

    fs = 1000.0
    numTimeSteps = 1    
    myGapMsec = (1000.0/fs)*numTimeSteps
    gaptest = datetime.timedelta(milliseconds=myGapMsec)
    
    dtStartFile1 = datetime.datetime.strptime('2012_01_01_00_00_00.000','%Y_%m_%d_%H_%M_%S.%f')
    dtEndofFile1 = datetime.datetime.strptime('2012_01_01_00_10_00.000','%Y_%m_%d_%H_%M_%S.%f')
    
    dtStartFile2 = datetime.datetime.strptime('2012_01_01_00_10_00.002','%Y_%m_%d_%H_%M_%S.%f')
    dtEndofFile2 = datetime.datetime.strptime('2012_01_01_00_20_00.000','%Y_%m_%d_%H_%M_%S.%f')
    
    dtStartFile3 = datetime.datetime.strptime('2012_01_01_00_20_00.001','%Y_%m_%d_%H_%M_%S.%f')
    dtEndofFile3 = datetime.datetime.strptime('2012_01_01_00_30_00.000','%Y_%m_%d_%H_%M_%S.%f')
    
    dtStartFile4 = datetime.datetime.strptime('2012_01_01_00_30_00.002','%Y_%m_%d_%H_%M_%S.%f')
    dtEndofFile4 = datetime.datetime.strptime('2012_01_01_00_40_00.000','%Y_%m_%d_%H_%M_%S.%f')

    fi1 = PadInterval(dtStartFile1, dtEndofFile1, sampleRate=fs)
    fi2 = PadInterval(dtStartFile2, dtEndofFile2, sampleRate=fs)
    fi3 = PadInterval(dtStartFile3, dtEndofFile3, sampleRate=fs)
    fi4 = PadInterval(dtStartFile4, dtEndofFile4, sampleRate=fs)
    
    gap1 = dtStartFile2 - dtEndofFile1; #print gap1
    gap2 = dtStartFile3 - dtEndofFile2; #print gap2
    gap3 = dtStartFile4 - dtEndofFile3; #print gap3
    
    sensorIntervals = PadIntervalSet()
    sensorIntervals.add(fi1)
    sensorIntervals.add(fi2)
    sensorIntervals.add(fi3)
    sensorIntervals.add(fi4)
    
    for i in sensorIntervals:
        print i.lower_bound.strftime('%Y_%m_%d_%H_%M_%S.%f'), "LOWER"
        print i.upper_bound.strftime('%Y_%m_%d_%H_%M_%S.%f'), "UPPER"
    print len(sensorIntervals.intervals)
    
    
    #print fi1.timeStep*1000.0, "msec is timeStep"
    #print gap.microseconds/1e3, "msec is gap so",
    #
    #if fi1.overlaps(fi2) or fi1.adjacent_to(fi2):
    #    print "it IS adjacent"
    #else:
    #    print "is NOT adjacent"
    
    sys.exit(0)
    

    for i in sensorIntervals:
        print i.lower_bound
        print i.upper_bound
        print 'xxxx'    
    
    #demoRead(); sys.exit(0)

    #dtEight1 =  datetime.datetime.strptime('2012_12_23_00_00_00.000','%Y_%m_%d_%H_%M_%S.%f')
    #dtEight2 =  datetime.datetime.strptime('2012_12_23_08_00_00.000','%Y_%m_%d_%H_%M_%S.%f')
    #
    #dtStartFilename =  datetime.datetime.strptime('2012_12_22_23_59_59.999','%Y_%m_%d_%H_%M_%S.%f')
    #dtStopFilename =   datetime.datetime.strptime('2012_12_23_00_00_00.000','%Y_%m_%d_%H_%M_%S.%f')
    #
    #largeInterval = PadInterval(dtEight1,        dtEight2,       sampleRate=1000.0)
    #smallInterval = PadInterval(dtStartFilename, dtStopFilename, sampleRate=1000.0)
    
    #spanOverlapSecs = largeInterval.getSpanSeconds()
    #print spanOverlapSecs
    #sys.exit(0)
    
    #print smallInterval in largeInterval
    #print smallInterval.overlaps(largeInterval)
    #print smallInterval.extends_beyond(largeInterval)
    #sys.exit(0)
    
    #psd = PadSensorDict(); print psd
    #psd['ONE'] = np.array([1,11]); print psd
    #psd['TWO'] = np.array([2,22]); print psd
    #psd = psd + PadSensorDict(ONE=(4,5)); print psd
    #psd = psd + PadSensorDict(THREE=(0,0)); print psd, "<<<"
    #psd = psd + PadSensorDict(TWO=(1,3)); print psd        
    #sys.exit(0)

    #                          sensor   product   year  M  D  H  suffix  abbrev n
    #fg = ProductFileGlobberDay('121f03', 'PRODUCT', 2012, 7, 1, 8,    '', 'spg*', 1)
    #fg = ProductFileGlobberDay('121f03', 'PRODUCT', 2012, 7, 1, 8, 'ten', 'spg*', 1)
    #fg = ProductFileGlobberDay('121f03', 'PRODUCT', 2012, 7, 1, 8, 'one', 'spg*', 4)
    #fg = ProductFileGlobberDay('121f03', 'PRODUCT', 2012, 7, 1, 0,    '', 'pcss*',1)
    #print len(fg.fileList)
    #print fg.fileList
    #sys.exit(0)
    
    for p in sys.argv[1:]:  # parse command line
        pair = split(p, '=', 1)
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parametersOK():
            #processData()
            #w = PadYmdWalker(2012,7,1,padPath='/tmp/junkpad',ignore='.*radgse|quarantined|.*hirap|.*121f03006')
            #w = PadYmdWalker(2012,7,1,padPath='/tmp/junkpad',ignore='.*radgse|quarantined')
            #w = PadYmdWalker(2012,7,12,ignore=parameters['ignore'])
            #w = PadYmdWalker(2012,7,13,ignore=parameters['ignore'])
            w = PadYmdWalker(2012,8,2,ignore=parameters['ignore'])
            sys.exit(0)
    printUsage()
