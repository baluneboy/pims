#!/usr/bin/env python
version = '$Id$'

# TODO write a record of processing results that includes:
# - number of PAD files written
# - total duration in hours (conservative, so text reads "more than XX hours")
# - GMT span
# - nice text form, maybe like following:
#   "Did processing to reformat, transform to SSA coordinates, and archive more than 20 hours of JAXA MMA (0bbd) data in 125 PAD files that span from GMT 26-Mar-2013,03:51:25 to 02-Apr-2013,06:19:21)."

from string import *
import struct
import os, sys
import shutil
from padutils import *
from padpro import *

#from jaxaData import *
from jaxaFile import *
#import logging,logging.config

from jaxaConnect import *
from jaxaException import *
from time import *
from commands import *
from syslog import *
from accelPacket import *
import math
import pickle
from MySQLdb import *
import traceback
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop

#Copying file: 2014_09_01_16_32_39.000+2014_09_01_17_32_39.000.0bbd
print pad_fullfilestr_to_start_stop('Copying file: 2014_09_01_16_32_39.000+2014_09_01_17_32_39.000.0bbd'); raise SystemExit

class JaxaSensorCounter(object):
    
    def __init__(self):
        self.days = set()
        self.file_count = 0
        
    def __str__(self):
        s = ''
        for day in self.days:
            s += '%s\n' % day
        s += 'count = %d' % self.count
        return s
    
    def _add(self, start_day, stop_day):
        self.days.add(start_day)
        self.days.add(stop_day)
        self.file_count += 1
        
class JaxaSummary(object):
    
    def __init__(self):
        self.sensors = dict()
    
    def __str__(self):
        s = 'wtf'
        return s
    
    def add_file(self, fname):
        sensor, start_day, stop_day = parse_pad_filename(fname)
        if sensor not in self.sensors:
            self.sensors[sensor] = JaxaSensorCounter()
        self.sensors[sensor]._add(start_day, stop_day)
    
jsummary = JaxaSummary()

#Instantiate logging
log = InitLogging()

# set default command line parameters, times are always measured in seconds
defaults = {'host':'localhost',                                                         # the name of the computer with the database
                                'database':'jaxa',                                                      # the name of the database to connect to
                                #'uploadDirectory':'/home/pims/mmadata',# the directory where JAXA uploads the MMA files
                                'uploadDirectory':'/misc/jaxa/mmadata', # the directory where JAXA uploads the MMA files
                                'convertToPad':'1',                                                     # Convert JAXA files to PAD files
                                'padDirectory':'/misc/yoda/pub/pad',    # the PIMS Acceleration data archive directory
                                #'padDirectory':'/home/pims/parchive',  # the PIMS Acceleration data archive directory
                                'archiveJaxa':'1',                                                      # Copy files to jaxaDirectory
                                'jaxaDirectory':'/misc/yoda/pub/jaxa',  # the directory where uploaded JAXA files will be archived
                                'jaxaCopyMethod':'ssh',                         #ssh,scp,copy or standard to let program choose
                                #'jaxaDirectory':'/home/pims/jarchive', # the directory where uploaded JAXA files will be archived
                                'delete':'0',                                                           # 0=delete Uploaded JAXA files when done
                                'logLevel':'0',                                                         # show or supress warning message
                                'quitWhenDone':'0',                                                     # end this program when all data is processed
                                'maxFileTime':'600'}                                            # maximum time span for a PAD file (0 means no limit)

parameters = defaults.copy()

def parametersOK():
    b = parameters['convertToPad']
    if b != '0' and b != '1':
        msg = ' convertToPad must be 0 or 1'
        log.warning(msg)
        return 0
    else:
        parameters['convertToPad'] = atoi(parameters['convertToPad'])

    b = parameters['archiveJaxa']
    if b != '0' and b != '1':
        log.warning(' archiveJaxa must be 0 or 1')
        return 0
    else:
        parameters['archiveJaxa'] = atoi(parameters['archiveJaxa'])

    if parameters['archiveJaxa']!=1 and parameters['convertToPad']!=1:
        msg= ' Either archiveJaxa or convertToPad must be equal to 1'
        log.warning(msg)
        return 0

    b = parameters['delete']
    if b != '0' and b != '1':
        msg = ' delete must be 0 or 1'
        log.warning(msg)
        return 0
    else:
        parameters['delete'] = atoi(parameters['delete'])

    b = parameters['logLevel']
    if b != '0' and b != '1' and b != '2' and b != '3':
        msg = ' logLevel must be 0,1,2 or 3'
        log.warning(msg)
        return 0
    else:
        parameters['logLevel'] = atoi(parameters['logLevel'])

    b = parameters['quitWhenDone']
    if b != '0' and b != '1':
        msg = ' quitWhenDone must be 0 or 1'
        log.warning(msg)
        return 0
    else:
        parameters['quitWhenDone'] = atoi(parameters['quitWhenDone'])

    parameters['maxFileTime'] = atof(parameters['maxFileTime'])

    #Retrieve upload copy method
    if os.path.isdir(parameters['uploadDirectory']):
        parameters['uploadCopyMethod'] = parameters['uploadDirectory']
    else:
        log.debug ('%s does not exist' % parameters['uploadDirectory'])
    if not parameters['uploadCopyMethod']:
        return 0

    #Retrieve Pad copy method
    if parameters['convertToPad']==1:
        parameters['padCopyMethod'] = checkDir('padDirectory')
        if not parameters['padCopyMethod']:
            return 0

    #Retrieve archive copy method
    if parameters['archiveJaxa']==1:
        b = parameters['jaxaCopyMethod']
        if b == 'standard':
            parameters['jaxaCopyMethod'] = checkDir('jaxaDirectory')
            if not parameters['jaxaCopyMethod']:
                return 0
        elif b != 'ssh' and b!='copy':
            msg = ' jaxaCopyMethod must be ssh, copy or standard'
            log.warning(msg)
            return 0

    return 1

def checkDir(dirToCheck):
    """Checks the designated parameter for directory for copy/scp ability"""
    b = parameters[dirToCheck]
    dest = split(b, ':')
    if len(dest)==1:
        msg = UnixToHumanTime(time(), 1) + ' testing copy connection...'
        log.info(msg)
        directory, = dest
        #Destination is local or mounted drive
        if not os.path.isdir(directory):
            log.debug ('%s does not exist' % dirToCheck)
        else:
            #Test copy
            r = getoutput(" touch copytest; cp -p copytest %s" %(b))
            if len(r) != 0:
                log.error(' copy test failed')
                log.error('directory: %s, error: %s' % (directory,r))
                sys.exit()
            log.debug(' %s copy OK' % dirToCheck)
            return 'copy'

    elif len(dest)==2:
        log.info(UnixToHumanTime(time(), 1) + ' testing scp connection...')
        host,directory = dest
        r = getoutput(" touch scptest;scp -p scptest %s" % (b))
        if len(r) != 0:
            log.error(' scp test failed')
            log.error(' host: %s, directory: %s, error: %s' % (host,directory,r))
            sys.exit()
        log.debug(' %s scp OK' % dirToCheck)
        return 'scp'

    else:
        log.warning(' %s must be in copy (/directory/to/store/to) or ssh format (hostname:/directory/to/store/to)' % dirToCheck)
        return 0

def jaxaSetParameters(newParameters):
    global parameters
    parameters = newParameters.copy()

def printUsage():
    print version
    print 'usage: processJaxa.py [options]'
    print '           options (and default values) are:'
    for i in defaults.keys():
        print '                    %s=%s' % (i, defaults[i])

def filter_filenames(dirpath, predicate):
    """Usage:
           >>> filePattern = '/misc/jaxa/(\d{14}-\d{14}/\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3}[+-]\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})\.(\w{4}$|\w{4}.header$)'
           >>> for filename in filter_filenames('/misc/jaxa', re.compile(r'/misc/jaxa/' + filePattern).match):
           ....    # do something
    """
    for dir_, dirnames, filenames in os.walk(dirpath):
        for filename in filenames:
            abspath = os.path.join(dir_, filename)
            if predicate(abspath):
                yield abspath

def getFileList(fileDir, filePattern):
    """return files that match expected pattern"""
    fileList = []
    pat = os.path.join(fileDir, filePattern)
    for f in filter_filenames(fileDir, re.compile(pat).match):
        fileList.append(f)
    return fileList

def OLDgetFileList(dir_name, subdir=True, *args):
    """Return a list of file names found in directory 'dir_name'
    If 'subdir' is True, recursively access subdirectories under 'dir_name'.
    Additional arguments, if any, are file extensions to match filenames. Matched
            file names are added to the list.
    If there are no additional arguments, all files found in the directory are
            added to the list.
    Example usage: fileList = getFileList(r'/junkP', False, 'txt', 'py')
            Only files with 'txt' and 'py' extensions will be added to the list.
    Example usage: fileList = getFileList(r'junk', True)
            All files and all the files in subdirectories under H:\TEMP will be added
            to the list.
    """
    fileList = []
    for file in os.listdir(dir_name):
        dirfile = os.path.join(dir_name, file)
        if os.path.isfile(dirfile):
            if not args:
                fileList.append(dirfile)
            else:
                if os.path.splitext(dirfile)[1][1:] in args:
                    fileList.append(dirfile)
        # recursively access file names in subdirectories
        elif os.path.isdir(dirfile) and subdir:
            fileList.extend(getFileList(dirfile, subdir, *args))
    return fileList

def getUploadList():
    """Gets a list of files from the upload directory"""
    import re
    from stat import ST_SIZE,ST_MTIME
    re.compile
    fileDir = parameters['uploadDirectory']
    #mmaFileNames = os.listdir(fileDir)

    #List of file files with complete path
    #mmaFileNames = getFileList(fileDir,True)
    filePattern = '(\d{14}-\d{14}/\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3}[+-]\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})\.(\w{4}$|\w{4}.header$)'
    mmaFileNames = getFileList(fileDir, filePattern)
    #mmaFileNames.sort()

    fn = {}
    mmaFileInfo = []

    for cf in mmaFileNames:
        (p,f) = os.path.split(cf)
        if isMMAFile(f):
            fn = {}
            fn['filename'] = f
            fn['path'] = p

            #File info
            info = os.stat(cf)
            fn['filesize'] = info[ST_SIZE]
            fn['lastmodified'] = info[ST_MTIME]
            fn['id'] = None
            fn['copied'] = None
            fn['processed'] = None

            #Check for header
            fn['hasheader'] =  int(os.path.isfile(cf + '.header'))

            mmaFileInfo.append(fn)

    return mmaFileInfo

def dbUpdateQueue(mmaFiles):
    #Step through the files and update the info
    for row in mmaFiles:
        dbUpdateFileStatus(row)

def dbUpdateFileStatus(mmaf):
    #Check for previous entry:

    dbmma = dbRetrieveQueueRecord(filename=mmaf['filename'])
    if dbmma:
        mmaf['id'] = dbmma['id']
        mmaf['copied'] = dbmma['copied']
        mmaf['processed'] = dbmma['processed']
        #Update the record
        cmd = """UPDATE filequeue SET filesize = %s, hasheader = %s, lastupdate = now() ,lastmodified = from_unixtime(%s) WHERE filename='%s'""" % \
                (mmaf['filesize'],mmaf['hasheader'],mmaf['lastmodified'],mmaf['filename'])
        results = sqlInsertOne(cmd,[])


    else:
        #Insert the record
        mmaf['copied'] = 0
        mmaf['processed'] = 0
        dbInsertQueue(mmaf)

        #Re-retrieve it to get the record.
        dbmma = dbRetrieveQueueRecord(filename=mmaf['filename'])
        mmaf['id'] = dbmma['id']
        mmaf['lastupdate'] = dbmma['lastupdate']

def dbRetrieveQueueRecord(id=None,filename=None):
    """Retrieve a record from the MMA Queue (filequeue)"""

    fn={}

    if id:
        cmd = """SELECT id,filename,path,hasheader,filesize,initdate,lastupdate,lastmodified,copied,processed FROM filequeue WHERE id = %s"""
        results = sqlFetchOne(cmd % id)

    if filename:
        cmd = """SELECT id,filename,path,hasheader,filesize,initdate,lastupdate,lastmodified,copied,processed FROM filequeue WHERE filename = '%s'"""
        results = sqlFetchOne(cmd % filename)

    if results:
        (fn['id'], fn['filename'],fn['path'],fn['hasheader'],fn['filesize'],fn['initdate'],fn['lastupdate'],fn['lastmodified'],fn['copied'],fn['processed']) = results

    return fn

def dbRetrieveQueue():
    #cmd = """SELECT id,filename,path,hasheader,filesize,initdate,lastupdate,lastmodified,copied,processed,hold FROM filequeue order by filename ASC"""
    #cmd = """SELECT id,filename,path,hasheader,filesize,initdate,lastupdate,lastmodified,copied,processed,hold FROM filequeue WHERE copied = 0 OR processed = 0 AND hold IS NULL order by filename ASC"""
    cmd = """SELECT id,filename,path,hasheader,filesize,initdate,lastupdate,lastmodified,copied,processed,hold FROM filequeue WHERE copied = 0 OR processed = 0 or copied IS NULL or processed IS NULL AND hold IS NULL order by filename ASC"""
    (results,description) = sqlFetchAll(cmd,returnDescription=1)

    thequeue = []
    if results:
        colnames = [desc[0] for desc in description]
        #thequeue = []
        for row in results:
            newdict = {}
            for name, val in zip(colnames, row):
                newdict[name] = val
            thequeue.append(newdict)
    else: # Hrovat added else clause for graceful nothing to do
        print 'nothing in thequeue from following query'
        print cmd
    return thequeue

#def dbSaveMMA(mmaf):
#       jf = jaxaFile(mmaf['filename'],headerOnly=1)
#
#       if jf.header:
#               cmd = """SELECT id FROM mmafile filequeue WHERE filename = '%s'"""
#               results = sqlFetchOne(cmd % mmaf['filename'])
#
#               if not results:
#                       jf.dbSave()

def dbInsertQueue(mmaf):
    cmd = """INSERT INTO filequeue (filename,path,hasheader,filesize,initdate,lastupdate,lastmodified) VALUES ('%s','%s','%s',%s,now(),now(),from_unixtime(%s))""" % \
            (mmaf['filename'],mmaf['path'],mmaf['hasheader'],mmaf['filesize'],mmaf['lastmodified'])
    results = sqlInsertOne(cmd,[])

def archiveMMA(mmaFiles):
    """Archive the MMA files to the jaxaDirectory"""
    uploadDir = parameters['uploadDirectory']
    jaxaDir = parameters['jaxaDirectory']

    for mmaf in mmaFiles:
        if not mmaf['copied']:
            log.debug('Copying file: %s' % mmaf['filename'])
            #The yearYYYY/monthMM/dayDD/sensor part of the path
            padPath = whichPadDir(mmaf['filename'])

            #Source files
            mmaDataSource = os.path.join(mmaf['path'],mmaf['filename'])
            mmaHeaderSource = os.path.join(mmaf['path'],mmaf['filename'] + '.header')

            #Target files
            mmaTargetDir = os.path.join(jaxaDir,padPath)
            mmaDataTarget = os.path.join(mmaTargetDir,mmaf['filename'])
            mmaHeaderTarget = os.path.join(mmaTargetDir,mmaf['filename']+'.header')

            #Make the directory if needed
            if validDir(mmaTargetDir):
                if parameters['jaxaCopyMethod'] == 'copy':
                    #Copy the header file
                    shutil.copyfile(mmaHeaderSource,mmaHeaderTarget)

                    #Copy the data file
                    log.debug('copying now')
                    shutil.copyfile(mmaDataSource,mmaDataTarget)

                    #Update the queue record
                    cmd = """UPDATE filequeue SET copied = now() WHERE id = %s""" % (mmaf['id'])
                    results = sqlInsertOne(cmd,[])

                elif parameters['jaxaCopyMethod'] == 'ssh':
                    #Originally planned as everything being scp, but now a kluge. Only implementing because
                    #copy through nfs is so slow
                    #Rebuild the paths
                    #Source files
                    mmaDataSource = os.path.join(mmaf['path'].replace('/misc','/sdds'),mmaf['filename'])
                    mmaHeaderSource = os.path.join(mmaf['path'].replace('/misc','/sdds'),mmaf['filename'] + '.header')

                    #Target files
                    mmaTargetDir = os.path.join('/sdds/pims/pub/jaxa',padPath)
                    mmaDataTarget = os.path.join(mmaTargetDir,mmaf['filename'])
                    mmaHeaderTarget = os.path.join(mmaTargetDir,mmaf['filename']+'.header')

                    #Create the ssh/cp string
                    copyCommand = """ssh yoda "cp '%s' '%s'" """

                    print copyCommand % (mmaHeaderSource,mmaHeaderTarget)
                    log.debug('copying via SSH')

                    #Copy the header file
                    os.system(copyCommand % (mmaHeaderSource,mmaHeaderTarget))

                    #Copy the data file
                    os.system(copyCommand % (mmaDataSource,mmaDataTarget))

                    #Update the queue record
                    cmd = """UPDATE filequeue SET copied = now() WHERE id = %s""" % (mmaf['id'])
                    results = sqlInsertOne(cmd,[])

                else:
                    #Not implemented
                    log.critical('Error Should not be here, scp not implemented.')

def padProcess():
    """Process the queue to Convert MMA files to PAD format and move to pad directory"""
    uploadDir = parameters['uploadDirectory']
    jaxaDir = parameters['jaxaDirectory']
    padDir = parameters['padDirectory']

    mmaFiles = dbRetrieveQueue()
    for mmaf in mmaFiles:
        try:
            if not mmaf['processed']:
                log.info('Processing file: %s , path: %s' % (mmaf['filename'], mmaf['path']))
    
                sourceFile = os.path.join(mmaf['path'],mmaf['filename'])
                #Load the MMA File, header only
                jfh = jaxaFile(filename=sourceFile,headerOnly=1)
    
                #Break up if greater than 10 minutes
                numRecs = jfh.getNumRecords(10,'min')
                offsetRecs = 0 #Number of records already read
                totalRecs = jfh.dataNum  #Number of records to read
    
                while offsetRecs < totalRecs:
    
                    #Read to end of file only
                    if offsetRecs + numRecs > totalRecs:
                        numRecs = totalRecs - offsetRecs
    
                    log.debug("offsetRecs: %d  numRecs: %d totalRecs: %d" % (offsetRecs,numRecs,totalRecs))
    
                    jf = jaxaFile(sourceFile,offsetRecs,numRecs)
    
                    #If this is the first chunk to be written and it is not
                    #contiguous, mark it as such, otherwise it is marked as contiguous.
                    if (jf.separator == '-' and (offsetRecs==0)):
                        sep = jf.separator
                    else:
                        sep = '+'
    
                    results = jf.writeAsPad(padDir,sep)
                    if results:
                        log.info('Wrote PAD file: %s' % results)
    
                    else:
                        log.Critical('Error writing PAD file. Aborting processing')
                        sys.exit()
    
                    #Advance the number of records
                    offsetRecs = offsetRecs + numRecs
    
                    #Update the queue record
                    cmd = """UPDATE filequeue SET processed = now() WHERE id = %s""" % (mmaf['id'])
                    results = sqlInsertOne(cmd,[])
                    
        except Exception:
            print 'Tried to processing file: %s , path: %s' % (mmaf['filename'], mmaf['path'])
            print '*** CAUGHT ', traceback.format_exc()

def convert2Pad(jf):
    """Convert a jaxaFile object to Pad file and write to disk """
    uploadDir = parameters['uploadDirectory']
    jaxaDir = parameters['jaxaDirectory']

    jf.writeAsPad(padroot)
    #print '%s => %s \t %s %d' % (jf.filename,unixTimeToString(jf.dateStart),unixTimeToString(jf.dateStop),jf.dataNum)


def validDir(dirname):
    if os.path.isdir(dirname):
        return 1
    else:
        os.makedirs(dirname)
        return 1

#def createFileDir(dirname=None,filename=None):
##      """Recursively creates the directory from the directory or the complete path of the file"""

def isMMAFile(f):
    """Checks filename to assure it is an MMA file, but not a header file"""
    import re

    if f.endswith('.header'):
        return 0
    else:
        #Only limited checking to verify that files are in YYYY_DD.... format
        #Note this script only works until 2999
        p = re.compile("2\d\d\d_\d\d_\d\d_\d\d_\d\d_\d\d.\d\d\d(\+|\-)2\d\d\d_\d\d_\d\d_\d\d_\d\d_\d\d.\d\d\d")
        m = p.match(f)

        if m:
            return 1
        else:
            return 0

def mainLoop():
    print 'Main Loop'

    mmaFiles = getUploadList()
    dbUpdateQueue(mmaFiles)

    if parameters['archiveJaxa'] == 1:
        log.debug("Archiving Jaxa Files")
        archiveMMA(mmaFiles)

    if parameters['convertToPad'] == 1:
        log.debug("Converting to PAD Files")

        #Retrieve list of mmaFiles from queue
        padProcess()

if __name__ == '__main__':
    for p in sys.argv[1:]:  # parse command line
        pair = split(p, '=', 1)
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        if not parameters.has_key(pair[0]):
            print 'bad parameter: %s' % pair[0]
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parametersOK():
            log.info('processJaxa starting')
            #print 'processJaxa starting'
            mainLoop()
            sys.exit()

    printUsage()
