#!/usr/bin/env python
version = '$Id$'

# TODO
# 1. cli option for colorized where mismatch between actual/wanted PLUS annotated (OKAY,ERROR,WARN) like "blah-blah 121f02 ERROR"
#    AND right justify - slash - left justify
# 2. hyperlinks (pimsdadgrid)?
# 3. update this to do some good form of status_superfine checks (pimsdadgrid) for desktop convenience
# use 0 for ok, 1 for warning, 2 for error, 3 for unknown
# - more status on the status bar; keeps tab on what is about to be done, how long it took, etc.
# - GB per day, other meta summary info per day?
# -------------------------------------------------------------------------------------------------------------
# FIXME
# - extend PimsDaySensorCacheWithSampleRate to include richer set of attributes (not just sample rate)
# - why doesn't timeout work on Command class (with subprocess -- maybe not use shell param?)

import sys
import re
from interval import Interval, IntervalSet
from padpro import PadInterval, PadIntervalSet, PadIntervalSampleRateException
from pims.files.utils import filter_filenames
from resample import *
import datetime
import padquery
import subprocess
from status_superfine import getDaysApproxHourSum, getPadHoursFromHeaderFile, grepSampleRate, rxField
import numpy as np
import threading
import traceback
import logging

# input parameters
defaults = {
             'padPath':      '/misc/yoda/pub/pad',         # where to look for root of PAD file tree
             'pdfPath':      '/misc/yoda/www/plots/batch', # where to look for root of PDF file tree
             'daysAgo':      2,                            # check one day's worth starting this many days ago
             'sensorPattern':'.*ams.*_accel_.*',           # subdir match this pattern
}
parameters = defaults.copy()

def sensorMatchesRxString(sensor, rxString):
    rx = re.compile(rxString)
    return rx.match(sensor)

def overallReturnCode(retcodes):
    return int(np.max(retcodes))

def padInventory(padPath,sensorPattern,numDaysAgo):
    """main routine for taking inventory along padPath for sensorPattern from numDaysAgo"""
    sensors = getSensors(padPath,sensorPattern,numDaysAgo)
    nonOSSsensors = [s for s in sensors if not s.startswith('oss')]
    nonOSSnon006sensors = [s for s in nonOSSsensors if not s.endswith('006')]
    #return nonOSSsensors
    return nonOSSnon006sensors

def grepSixHzSensorDirPattern():
    """get sensor (dir) pattern from bash script on jimmy"""
    bashFile = '/misc/jimmy/home/pims/dev/programs/bash/cron_resample.bash'
    cmd = 'grep fcNew=6 ' + bashFile
    command = Command(cmd)
    command.run()
    sensorPatternDir = command.stdout.split('=')[-1]
    return sensorPatternDir

def getSensorDirPatternsForRoadmapsFromIke():
    # ssh ike '/usr/local/bin/matlab -nojvm -nosplash -r "cd /home/pims/dev/work;startup;show_sensor_roadmap_patterns;quit"'
    cmd = 'ssh ike ''/usr/local/bin/matlab -nojvm -nosplash -r "cd /home/pims/dev/work;show_sensor_roadmap_patterns;quit"'''
    command = Command(cmd)
    command.run()
    outstr = command.stdout

    sensorRxListTen = ''
    m = re.search(r'casSensorsTen,(.*)', outstr)
    if m:
        sensorRxListTen = m.group(1).replace('*', '.*').replace(',', '$|') + '$'

    sensorRxListOne = ''
    m = re.search(r'casSensorsOne,(.*)', outstr)
    if m:
        sensorRxListOne = m.group(1).replace('*', '.*').replace(',', '$|') + '$'

    return sensorRxListTen, sensorRxListOne

def parametersOK():
    """check for reasonableness of parameters entered on command line"""
    if not os.path.exists(parameters['padPath']):
        print 'padPath (%s) does not exist' % parameters['padPath']
        return 0

    if not os.path.exists(parameters['pdfPath']):
        print 'pdfPath (%s) does not exist' % parameters['pdfPath']
        return 0

    if parameters['daysAgo'] != None:
        parameters['daysAgo'] = atof(parameters['daysAgo'])
        dateAgo = daysAgoString(parameters['daysAgo'])
        parameters['dateStart'] =  dateAgo + "_00_00_00.000"
        parameters['dateStop']  =  dateAgo + "_23_59_59.999"
        parameters['day'] = datetime.datetime.strptime(dateAgo,'%Y_%m_%d').date()

    if parameters['sensorPattern'] != None:
        parameters['sensor'] = padInventory(parameters['padPath'],parameters['sensorPattern'],parameters['daysAgo'])
    else:
        return 0

    # get list of sensors to have been resampled
    sensorPatternDirToBeResampled = grepSixHzSensorDirPattern()
    sensorsToBeResampled = getSensors(parameters['padPath'],sensorPatternDirToBeResampled,parameters['daysAgo'])
    sensorsToBeResampled.sort()
    parameters['sensorsToBeResampled'] = [s for s in sensorsToBeResampled if not s.endswith('006')]

    return 1 # all OK, return 0 otherwise

class Command(threading.Thread):
    def __init__(self,cmd):
        self.cmd = cmd
        self.stdout = None
        self.stderr = None
        self.begintime = None
        self.endtime = None
        threading.Thread.__init__(self)

    def run(self):
        cmdstr = self.cmd.split()
        self.begintime = datetime.datetime.now()
        p = subprocess.Popen(cmdstr,
                             shell=False,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.stdout, self.stderr = p.communicate()
        self.endtime = datetime.datetime.now()
        self.returncode = p.returncode

class CommandSequence(object):
    def __init__( self, *steps ):
        self.steps = steps
    def run( self ):
        for s in self.steps:
            c = Command(s)
            print c.cmd + " gives",
            c.start()
            c.join()
            print '<%s>' % c.stdout.strip()

class PimsDayCache(object):
    """class to manage pims products for given day (pad files, roadmaps, db entries, etc.)"""

    def __init__(self, date=datetime.date.today()-datetime.timedelta(2), sensorSubDirRx='.*ams.*_accel_.*', padPath='/misc/yoda/pub/pad'):
        self.date = date
        self.sensorSubDirRx = sensorSubDirRx
        self.padPath = padPath
        self.ymd = self.date.strftime('year%Y/month%m/day%d')
        self.headerFiles = self.getHeaderList()
        self.intervals = self.getDayIntervalSets()
        self.sensorList = self.getSensorList()
        self.roadmapPdfs = self.getRoadmapPdfs()
        self.dbRoadmaps = [x[0] for x in padquery.YodaMapQueryAll(year=self.date.year,month=self.date.month,day=self.date.day).results]
        sensorRxListTen, sensorRxListOne = getSensorDirPatternsForRoadmapsFromIke()
        #self.sensorRegexsOneHz = getLaibleRoadmapGlobPatList('generate_vibratory_roadmap_superfine').replace('006','one')
        #self.sensorRegexsTenHz = getLaibleRoadmapGlobPatList('configure_roadmap_spectrogram_10hz').replace('$','ten$')
        self.sensorRegexsOneHz = sensorRxListOne.replace('006','one')
        self.sensorRegexsTenHz = sensorRxListTen.replace('$','ten$')
        self.summary = self.getSummary()
        self.logger = self.setupLogger()

    def setupLogger(self):
        cname = self.__class__.__name__
        logger = logging.getLogger(cname)
        handler = logging.FileHandler('/var/tmp/' + cname + '.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def getDayIntervalSets(self):
        def _getIntervalSet(tzero,h1,h2):
            pi = Interval( tzero + datetime.timedelta(hours=h1),  tzero + datetime.timedelta(hours=h2), upper_closed=False )
            return IntervalSet(items=[pi])
        tzero = datetime.datetime(self.date.year, self.date.month, self.date.day)
        i1 = _getIntervalSet(tzero,0,8)
        i2 = _getIntervalSet(tzero,8,16)
        i3 = _getIntervalSet(tzero,16,24)
        return [i1, i2, i3]

    def getSummary(self):
        return str(self)

    def __str__(self):
        return "cache for " + str(self.date) + ", sensorSubDirRx = " + str(self.sensorSubDirRx) + ", numHeaders = " + str(len(self.headerFiles))

    def getHeaderList(self):
        ##sensorGlobPattern = self.sensorSubDirRx.replace('.*','*')
        ##self.hdrGlobPat = os.path.join(self.padPath, self.ymd, sensorGlobPattern, '*.header')
        ##return glob.glob(self.hdrGlobPat)

        # FIXME why does next line to reject quarantined NOT WORK?
        #self.hdrRxPat = os.path.join(self.padPath, self.ymd, self.sensorSubDirRx, '(?!quarantined.*$).*\.header$')
        self.hdrRxPat = os.path.join(self.padPath, self.ymd, self.sensorSubDirRx, '.*\.header')
        predicate = re.compile(self.hdrRxPat).match
        hdr_files = [ f for f in filter_filenames( os.path.join(self.padPath, self.ymd), predicate ) if 'quarantined' not in f ]
        return hdr_files

    def getSensorList(self):
        headerRx = os.path.join(self.padPath, self.ymd, self.sensorSubDirRx,'(?P<start>[._0-9]{23})[+-](?P<stop>[._0-9]{23})\.(?P<sensor>\w*)\.header$')
        pat = re.compile(headerRx)
        matchSensors = [rxField(pat,'sensor',x) for x in self.headerFiles]
        sensorList = list(set(matchSensors))
        sensorList.sort()
        return sensorList

    def getRoadmapPdfs(self):
        return glob.glob('/misc/yoda/www/plots/batch/year%04d/month%02d/day%02d/*_*_*_roadmaps*.pdf' % (self.date.year, self.date.month, self.date.day))

class PimsDaySensorCache(object):
    """class to manage pims products for given day+sensor (pad files, roadmaps, db entries, etc.)"""

    def __init__(self, sensor=None, pimsDayCache=None):
        self.inittime = datetime.datetime.now()
        self.sensor = sensor
        if pimsDayCache is None:
            self.pimsDayCache = PimsDayCache(date=date)
        else:
            self.pimsDayCache = pimsDayCache
        self.headerFiles = self.getHeaderFiles()
        # the next line(s) reference to "cheap" is using PAD filenames to get stop times (not numrecs & fs to get secs)
        self.cheapPadIntervalSet = self.getCheapPadIntervalSetFromHeaderFilenames()
        self.hasPadInCheapIntervals = [len(self.cheapPadIntervalSet & y)>0 for y in self.pimsDayCache.intervals]
        self.approxPadHours = getDaysApproxHourSum(self.headerFiles)
        self.roadmapPdfs = self.getRoadmapPdfs('')
        self.onePdfs = self.getRoadmapPdfs('one')
        self.tenPdfs = self.getRoadmapPdfs('ten')
        self.dbDefRoadmaps = self.getDbRoadmaps('')
        self.dbOneRoadmaps = self.getDbRoadmaps('one')
        self.dbTenRoadmaps = self.getDbRoadmaps('ten')
        #self.needsIkeDbRepair()
        self.retcode = self.getSensorStatus()
        #self.textline = '[ %2d %2d %2d/%2d %2d/%2d %2d/%2d %2d/%2d %2d/%2d %2d/%2d] %s' % (self.retcode, self.approxPadHours, len(self.roadmapPdfs), self.expectedNumRoadmaps, len(self.tenPdfs), self.expectedNumTens, len(self.onePdfs), self.expectedNumOnes, len(self.dbDefRoadmaps), self.expectedNumRoadmaps, len(self.dbTenRoadmaps), self.expectedNumTens, len(self.dbOneRoadmaps), self.expectedNumOnes, self.sensor)

    def __str__(self):
        s = ('[ '
             '{s.retcode:1d} '
             '{s.approxPadHours:2d} '
             '{n1:>2d}/{s.expectedNumRoadmaps:<2d} '
             '{n2:>2d}/{s.expectedNumTens:<2d} '
             '{n3:>2d}/{s.expectedNumOnes:<2d} '
             '{n4:>2d}/{s.expectedNumRoadmaps:<2d} '
             '{n5:>2d}/{s.expectedNumTens:<2d} '
             '{n6:>2d}/{s.expectedNumOnes:<2d} '
             '] {s.sensor:<}').format(
            s=self,
            n1=len(self.roadmapPdfs),
            n2=len(self.tenPdfs),
            n3=len(self.onePdfs),
            n4=len(self.dbDefRoadmaps),
            n5=len(self.dbTenRoadmaps),
            n6=len(self.dbOneRoadmaps),
            )
        return s

    def needsIkeDbRepair(self):
        sumPdfs = len(self.roadmapPdfs) + len(self.tenPdfs) + len(self.onePdfs)
        sumDbs  = len(self.dbDefRoadmaps) + len(self.dbTenRoadmaps) + len(self.dbOneRoadmaps)
        if sumPdfs>sumDbs:
            #getRepairModTime()
            print '\n ~~~ %s ~~~\nNEEDS IKE REPAIR\n%d PDFs versus %d DBs\n ~~~ ~~~ ~~~\n' % (self.sensor, sumPdfs, sumDbs)

    def _doCheckCodes(self, checktype, tupCheckList, checkCodesArr):
        unwantedCode = 2
        if checktype.endswith('warn'):
            unwantedCode = 1
        for tup in tupCheckList:
            actual = tup[0]
            wanted = tup[1]
            if actual==wanted:
                code = 0
            else:
                code = unwantedCode
            checkCodesArr = np.append(checkCodesArr, code)
        return checkCodesArr

    def parseFromFilename(self, pair):
        try:
            dtStartFilename = datetime.datetime.strptime(pair[0].split(os.path.sep)[-1],'%Y_%m_%d_%H_%M_%S.%f')
            dtStopFilename =  datetime.datetime.strptime(pair[1],'%Y_%m_%d_%H_%M_%S.%f')
        except ValueError, value_error:
            print '*START PART: ', pair[0].split(os.path.sep)[-1]
            print '*STOP  PART: ', pair[1]
            print '*INSPECT VALUES ABOVE, THIS MIGHT BE THE "60 SECONDS IN FILENAME" PROBLEM FROM packetWriter.py?'
        except Exception, original_error:
            try:
                raise
            finally:
                try:
                    cleanup()
                except:
                    print 'THERE WAS AN ERROR IN CLEANUP, BUT WE IGNORED IT.'
                    pass # ignore errors in cleanup
        return dtStartFilename, dtStopFilename

    def getCheapPadIntervalSetFromHeaderFilenames(self):
        """extract info from pad filename: (sensor, bytes, seconds, interval)"""
        intervalSet = IntervalSet()
        for padFileName in self.headerFiles:
            # FIXME the next few lines are quite hideous
            padFileName = split(padFileName, '.header')[0] # throw away '.header' suffix
            padFileName = join(split(padFileName, '.')[:-1], '.')
            pair = split(padFileName, '-') # joiner is a minus
            if len(pair) == 1: pair = split(padFileName, '+') # in case joiner is a plus
            try:
                dtStartFilename, dtStopFilename = self.parseFromFilename(pair)
            except Exception, err:
                traceback.print_exc()
                sys.exit(1)
            intervalSet.add( Interval( dtStartFilename, dtStopFilename ) ) # this is where sample_rate goes BUT many headers -> one sample_rate?
        return intervalSet

    def getExpectedNumRoadmaps(self):
        xn = sum([int(x) for x in self.hasPadInCheapIntervals])
        #xn = ( ( int(self.approxPadHours) - 1) / 8 ) + 1
        return xn + 1 # number of spgs (plus one for pcss)

    def getSensorStatus(self):
        """get self.sensor status"""

        expectedNumRoadmaps, expectedNumTens, expectedNumOnes = 0, 0, 0

        if not (self.sensor.endswith('006') or self.sensor.endswith('ossbtmf') or self.sensor.endswith('ossraw')):
            expectedNumRoadmaps = self.getExpectedNumRoadmaps()

        #if sensorMatchesRxString(self.sensor, self.pimsDayCache.sensorRegexsTenHz):
        #    expectedNumTens = self.getExpectedNumRoadmaps()

        #### THIS BLOCK OF CODE WAS WHEN 121f02 WAS ON MSG W/O xform-to-SSA INFO
        ###if self.sensor.endswith('121f02'): # no xform to SSA for most 121f02 data, so no per-axis spgx, spgy, spgz
        ###    expectedNumTens = 0
        ###elif not self.sensor.endswith('006') and sensorMatchesRxString(self.sensor+'ten', self.pimsDayCache.sensorRegexsTenHz):
        ###    xnr = self.getExpectedNumRoadmaps()
        ###    expectedNumTens = ( ( xnr - 1 ) * 4 ) + 1 # (s,x,y,z) for each [8-hour] interval + one more for pcss
        #### THIS BLOCK OF CODE WAS WHEN 121f02 WAS ON MSG W/O xform-to-SSA INFO

        if not self.sensor.endswith('006') and sensorMatchesRxString(self.sensor+'ten', self.pimsDayCache.sensorRegexsTenHz):
            xnr = self.getExpectedNumRoadmaps()
            expectedNumTens = ( ( xnr - 1 ) * 4 ) + 1 # (s,x,y,z) for each [8-hour] interval + one more for pcss

        if self.sensor.endswith('121f02'): # no xform to SSA for most 121f02 data, so no per-axis spgx, spgy, spgz
            expectedNumOnes = 0
        elif not self.sensor.endswith('006') and sensorMatchesRxString(self.sensor+'one', self.pimsDayCache.sensorRegexsOneHz):
            xnr = self.getExpectedNumRoadmaps()
            expectedNumOnes = ( ( xnr - 1 ) * 4 ) + 1 # (s,x,y,z) for each [8-hour] interval + one more for pcss

        checkCodes = np.array([], dtype=int)
        checkListError = [(len(self.roadmapPdfs), expectedNumRoadmaps), (len(self.tenPdfs), expectedNumTens), (len(self.onePdfs), expectedNumOnes)]
        checkListWarn  = [(len(self.dbDefRoadmaps), expectedNumRoadmaps), (len(self.dbTenRoadmaps), expectedNumTens), (len(self.dbOneRoadmaps), expectedNumOnes)]
        checkCodes = self._doCheckCodes('error', checkListError, checkCodes)
        checkCodes = self._doCheckCodes('warn',  checkListWarn,  checkCodes)
        sensorCode = overallReturnCode(checkCodes)

        self.expectedNumRoadmaps, self.expectedNumTens, self.expectedNumOnes = expectedNumRoadmaps, expectedNumTens, expectedNumOnes

        return sensorCode

    def getRoadmapPdfs(self,suffix):
        rx = os.path.join('.*', self.pimsDayCache.ymd, '.*_' + self.sensor + suffix + '_.*_roadmaps.*.pdf')
        pat = re.compile(rx)
        return [x for x in self.pimsDayCache.roadmapPdfs if pat.match(x)]

    def getDbRoadmaps(self,suffix):
        ymdPrefix = self.pimsDayCache.date.strftime('%Y_%m_%d')
        rx = os.path.join(ymdPrefix + '_.*_' + self.sensor + suffix + '_.*_roadmaps.*.pdf')
        pat = re.compile(rx)
        return [x for x in self.pimsDayCache.dbRoadmaps if pat.match(x)]

    def getHeaderFiles(self):
        padPath = self.pimsDayCache.padPath
        ymd = self.pimsDayCache.ymd
        sensorRx = '.*' + self.sensor
        headerRx = os.path.join(padPath, ymd, sensorRx,'(?P<start>[._0-9]{23})[+-](?P<stop>[._0-9]{23})\.(?P<sensor>\w*)\.header$')
        pat = re.compile(headerRx)
        return [x for x in self.pimsDayCache.headerFiles if pat.match(x)]

class PimsDaySensorCacheWithSampleRate(PimsDaySensorCache):
    """class to identify intervals for given day+sensor"""

    def __init__(self, sensor=None, pimsDayCache=None):
        self.inittime = datetime.datetime.now()
        self.sensor = sensor
        if pimsDayCache is None:
            self.pimsDayCache = PimsDayCache(date=date)
        else:
            self.pimsDayCache = pimsDayCache
        self.headerFiles = self.getHeaderFiles()
        # the next line(s) reference to "cheap" is using PAD filenames to get stop times (not numrecs & fs to get secs)
        self.cheapPadIntervalSet = self.getCheapPadIntervalSetFromHeaderFilenames()
        # SNIP
        self.approxPadHours = getDaysApproxHourSum(self.headerFiles)
        # SNIP

    def __str__(self):
        s = (
            '  {s.sensor:<11s} '
            '{s.cheapPadIntervalSet.sampleRate:>8.2f} sa/sec '
            '{n1:>3d} intervals '
            ' ~{s.approxPadHours:3d}hrsPAD '
            '{n2:>5d} hdrFiles '
            ).format(
            s=self,
            n1=len(self.cheapPadIntervalSet.intervals),
            n2=len(self.headerFiles),
            )
        return s

    def getSampleRateFromHeaderFile(self, headerFile):
        """extract sample rate from headerFile"""
        with open(headerFile) as f:
            for line in f:
                match = re.search(".*SampleRate.(.*)..SampleRate.*", line)
                if match:
                    return float(match.group(1))
        return None

    def parseFromFilename(self, pair, intervalSet, sampleRate, logMessages):
        try:
            dtStartFilename = datetime.datetime.strptime(pair[0].split(os.path.sep)[-1],'%Y_%m_%d_%H_%M_%S.%f')
            dtStopFilename =  datetime.datetime.strptime(pair[1],'%Y_%m_%d_%H_%M_%S.%f')
            intervalSet.add( PadInterval( dtStartFilename, dtStopFilename, sampleRate=sampleRate ) ) # this is where sample_rate goes BUT many headers -> one sample_rate?
        except ValueError, value_error:
            msg = 'START PART: %s' % pair[0].split(os.path.sep)[-1]
            msg += '\nSTOP  PART: %s' % pair[1]
            msg += 'INSPECT VALUES ABOVE, THIS MIGHT BE THE "60 SECONDS IN FILENAME" PROBLEM FROM packetWriter.py?'
            logMessages.append(msg)
        except PadIntervalSampleRateException, sample_rate_error:
            logMessages.append('%s for file that starts with %s' % (sample_rate_error, pair[0]))
        except Exception, original_error:
            try:
                raise
            finally:
                try:
                    cleanup()
                except:
                    logMessages.append('THERE WAS AN ERROR IN CLEANUP, BUT WE IGNORED IT.')
                    pass # ignore errors in cleanup
        return dtStartFilename, dtStopFilename, intervalSet

    def getCheapPadIntervalSetFromHeaderFilenames(self):
        """extract info from pad filename: (sensor, bytes, seconds, interval)"""
        logMessages = []
        intervalSet = PadIntervalSet()
        for padFileName in self.headerFiles:
            # FIXME the next few lines are quite hideous
            sampleRate = self.getSampleRateFromHeaderFile(padFileName)
            padFileName = split(padFileName, '.header')[0] # throw away '.header' suffix
            padFileName = join(split(padFileName, '.')[:-1], '.')
            pair = split(padFileName, '-') # joiner is a minus
            if len(pair) == 1: pair = split(padFileName, '+') # in case joiner is a plus
            try:
                dtStartFilename, dtStopFilename, intervalSet = self.parseFromFilename(pair, intervalSet, sampleRate, logMessages)
            except Exception, err:
                traceback.print_exc()
                sys.exit(1)
        if len(logMessages) > 0:
            [self.pimsDayCache.logger.info(msg) for msg in logMessages]
        return intervalSet

    def plotIntervalSet(self, ppi, y): #, sensor, start, stop, color='k', lw=6):
        # Set current axes
        fig = ppi.fig
        ax = ppi.ax
        fig.sca(ax)

        # Plot horizontal lines
        hLines = []
        #for t1,t2 in zip(start,stop):
        #    hLines.append(plt.hlines(y, t1, t2, color, lw=lw))
        for i in self.cheapPadIntervalSet:
            ppi.tmin = min([ppi.tmin, i.lower_bound])
            ppi.tmax = max([ppi.tmax, i.upper_bound])
            hLines.append(plt.hlines(y, i.lower_bound, i.upper_bound, color='b', lw=9))
        return hLines

class PadHoursDayCache(PimsDayCache):
    """class to manage pad hours for given day (hinges on header files)"""

    def __init__(self, date=datetime.date.today()-datetime.timedelta(2), sensorSubDirRx='.*ams.*_accel_.*', padPath='/misc/yoda/pub/pad'):
        self.date = date
        self.sensorSubDirRx = sensorSubDirRx
        self.padPath = padPath
        self.ymd = self.date.strftime('year%Y/month%m/day%d')
        self.headerFiles = self.getHeaderList()
        self.sensorList = self.getSensorList()

    def __str__(self):
        return "approx. pad hours for " + str(self.date) + ", sensorSubDirRx = " + str(self.sensorSubDirRx) + ", numHeaders = " + str(len(self.headerFiles))

def getSummaryText(allSensors,okaySensors,errorSensors,warnSensors,da,d):
    def getThisList(prefix,L):
        s = '; ' + prefix + ' = [ '
        for sensor in L:
            #s += Bcolors.FAIL + sensor + Bcolors.ENDC + ' '
            s += sensor + ' '
        s += ']'
        return s
    summaryText = '%d of %d sensors are OK' % ( len(okaySensors), len(allSensors) )
    #if len(errorSensors)>0: summaryText += getThisList(Bcolors.FAIL + 'errorSensors' + Bcolors.ENDC, errorSensors)
    if len(errorSensors)>0: summaryText += getThisList('errorSensors', errorSensors)
    if len(warnSensors)>0: summaryText += getThisList('warnSensors',warnSensors)
    summaryText += ' for %d days ago (%s)' % (da, d.strftime('%d-%b-%Y'))
    return summaryText

def dummyNagiosUnknown():
    print "dummyNagiosUnknown@%s | lineOne: after pipeOn1\nlineTwo\nlineThree | line3: after pipeOn3" % datetime.datetime.now()
    sys.exit(3)

def dummyNagiosError():
    print "dummyNagiosError@%s | lineOne: after pipeOn1\nlineTwo\nlineThree | line3: after pipeOn3" % datetime.datetime.now()
    sys.exit(2)

def dummyNagiosWarn():
    print "dummyNagiosWarn@%s" % datetime.datetime.now()
    sys.exit(1)

def dummyNagiosOkay():
    print "dummyNagiosOkay@%s" % datetime.datetime.now()
    sys.exit(0)

def main():
    for p in sys.argv[1:]:  # parse command line
        pair = split(p, '=', 1)
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parametersOK():
            retcodes = np.array([], dtype=int)
            textlines = ''
            pdc = PimsDayCache(sensorSubDirRx=parameters['sensorPattern'], date=datetime.date.today()-datetime.timedelta(parameters['daysAgo']))
            errorSensors, warnSensors, okaySensors = [], [], []
            for sensor in pdc.sensorList:
                pds = PimsDaySensorCache(sensor=sensor, pimsDayCache=pdc)
                if pds.retcode==2:
                    errorSensors.append(sensor)
                elif pds.retcode==1:
                    warnSensors.append(sensor)
                elif pds.retcode==0:
                    okaySensors.append(sensor)
                else:
                    errorSensors.append(sensor)
                retcodes = np.append(retcodes, pds.retcode)
                textlines += str(pds) + '\n'
    retcode = overallReturnCode(retcodes)
    summaryText = getSummaryText(pdc.sensorList, okaySensors, errorSensors, warnSensors, parameters['daysAgo'], pdc.date)
    print summaryText # OBSOLETE print summaryText + '\n' + textlines + callouts()
    sys.exit(retcode)

def demo1():
    pdc = PimsDayCache(sensorSubDirRx='.*_accel_(hirap|121f0[358]).*', date=datetime.date.today()-datetime.timedelta(2))
    print pdc

#demo1()
#print 'NOW GET RID OF DEMO LINES NEAR if __name__ == "__main__"'
#raise SystemExit

if __name__ == '__main__':
    main()
