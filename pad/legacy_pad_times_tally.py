#!/usr/bin/env python

# TODO
# if startDate>stopDate or stopDate>weekAgo, then nothing to do

import csv
import datetime
from string import *
import struct
import os, sys
import shutil
from padutils import *
from padpro import *

# set default command line parameters, times are always measured in seconds
defaults = {'padPath':'/misc/yoda/pub/pad',# the original PAD directory path
            'outputFile':'/misc/yoda/www/plots/batch/padtimes/padtimes.csv',# the destination path
            'sensorList':'all',# sensor directories to check
            'startDate': None, # Start date to process (None to resume based on csv last date);  or set manually to like '2001-05-03' 
            'stopDate': None,  # Will stop when no year directory is found (None for "two days ago"); or set manually to like '2029-01-01'
            'fileMode':'a'}    # use 'w' for write to start from scratch and not just append

parameters = defaults.copy()

def tail( csvFile, numLines=1 ):
    f = open(csvFile, 'rb')
    BUFSIZ = 1024
    f.seek(0, 2)
    bytes = f.tell()
    size = numLines
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if (bytes - BUFSIZ > 0):
            # Seek back one whole BUFSIZ
            f.seek(block*BUFSIZ, 2)
            # read BUFFER
            data.append(f.read(BUFSIZ))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            data.append(f.read(bytes))
        linesFound = data[-1].count('\n')
        size -= linesFound
        bytes -= BUFSIZ
        block -= 1
    f.close()
    return '\n'.join(''.join(data).splitlines()[-numLines:])

def getCsvFileStopDate(csvFile):
    """get csv file stop date from its last row"""
    s = tail(csvFile, numLines=1).split(',')[0]
    return datetime.datetime.strptime(s,'%Y-%m-%d').date()

def getDaysAgoDate(da=2):
    """get date from week ago"""
    return datetime.date.today()-datetime.timedelta(days=da)

def parametersOK():
    b = parameters['padPath']
    if not (os.path.isdir(b)):
        msg = ' Pad path does not exist'
        print msg
        return 0

    if not os.path.exists(parameters['outputFile']):
        print 'output file "%s" did not exist' % parameters['outputFile']
        myStartDate = datetime.datetime.strptime('2001-05-03','%Y-%m-%d').date()
    else:
        if parameters['startDate'] is None:
            csvFileStopDate = getCsvFileStopDate(parameters['outputFile'])
            myStartDate = csvFileStopDate + datetime.timedelta(1)
        else:
            myStartDate = datetime.datetime.strptime(parameters['startDate'],'%Y-%m-%d').date()

    daysAgoDate = getDaysAgoDate(da=2)
    if parameters['stopDate'] is None:
        myStopDate = daysAgoDate
    else:
        myStopDate = datetime.datetime.strptime(parameters['stopDate'],'%Y-%m-%d').date()
        
    if myStopDate<myStartDate:
        print ' stopDate=%s IS BEFORE...\nstartDate=%s\n---SO DO NOTHING---' % (myStopDate, myStartDate)
        return 0
    elif myStopDate>daysAgoDate:
        print ' stopDate=%s IS LESS THAN A WEEK AGO...\n  weekAgo=%s\n---SO CLAMP STOP AT WEEK AGO---' % (myStopDate, daysAgoDate)
        myStopDate = daysAgoDate
        return 0

    parameters['startDate'] = myStartDate.strftime('%Y-%m-%d')
    parameters['stopDate'] = myStopDate.strftime('%Y-%m-%d')

    b = parameters['sensorList']
    if b=='all':
        # this command gets superset (too many for what we want here though):
        # find /misc/yoda/pub/pad -maxdepth 4 -mindepth 4 -type d -printf "%f\n" | sort | uniq
        #parameters['sensorList']=['sams2_accel_121f02','sams2_accel_121f03','sams2_accel_121f04','sams2_accel_121f05','sams2_accel_121f06','sams2_accel_121f08','samses_accel_es05','samses_accel_es06','samses_accel_es08','mams_accel_ossbtmf','mams_accel_ossraw','mams_accel_hirap','iss_rad_radgse']
        parameters['sensorList']=[
            'sams2_accel_121f02','sams2_accel_121f03','sams2_accel_121f04','sams2_accel_121f05','sams2_accel_121f06','sams2_accel_121f08',
            'samses_accel_es03','samses_accel_es05','samses_accel_es06','samses_accel_es08',
            'mams_accel_ossbtmf','mams_accel_ossraw','mams_accel_hirap','iss_rad_radgse',
            'mma_accel_0bba','mma_accel_0bbb','mma_accel_0bbc','mma_accel_0bbd'
            ]
    else:
        parameters['sensorList'] = split(b,',')
    return 1

def printUsage():
    #print version
    print 'usage: packetWriter.py [options]'
    print '           options (and default values) are:'
    for i in defaults.keys():
        print '                    %s=%s' % (i, defaults[i])

def getFileList(dir_name, subdir=True, *args):
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

def validDir(dirname):
    if os.path.isdir(dirname):
        return 1
    else:
        os.makedirs(dirname)
        return 1

def mainLoop():

    #Input and output paths
    padPath = parameters['padPath']
    outPath = parameters['outputFile']

    #Parse start and stop times
    astart = split(parameters['startDate'],'-');
    startY, startM, startD = map(int, astart)
    astop = split(parameters['stopDate'],'-');
    stopY, stopM, stopD = map(int, astop)

    #Setup loop to cycle through days
    y, m, d = startY, startM, startD
    tStart = mktime((y,m,d,0,0,0,0,0,0))
    tStop  = mktime((stopY,stopM,stopD,0,0,0,0,0,0))

    outfile = open(outPath,parameters['fileMode'])
    if parameters['fileMode']=='w':
        temp= 'Date,Year,Month,Day,' + ',Bytes,'.join(parameters['sensorList']) + ',MB'
        print >> outfile, temp

    while tStart <= tStop:
        yearPath = '%s/year%s' % (padPath, y)
        if not (os.path.isdir(yearPath)):
            print 'No year %s directory found.  Processing complete.'%y
            sys.exit()

        padDayPath = '%s/year%s/month%02d/day%02d' % (padPath, y, m, d)

        #Initialize dictionary
        dayHrs={}
        dayMB={}
        for sensor in parameters['sensorList']:
            dayHrs[sensor]=0
            dayMB[sensor]=0

        print 'Date: %s-%02d-%02d'%(y,m,d)
        strOut = '%s-%02d-%02d,%s,%02d,%02d'%(y,m,d,y,m,d)
        if (os.path.isdir(padDayPath)):
            for sensor in parameters['sensorList']:
                padSensorPath = '%s/year%s/month%02d/day%02d/%s' % (padPath, y, m, d,sensor)
                if os.path.isdir(padSensorPath):
                    print '    Found %s'%sensor
                    fileList = getFileList(padSensorPath, False, 'header')
                    fileList.sort()
                    prevEndTime = 0
                    for hfn in fileList:
                        fn = padFileName = split(hfn, '.header')[0]
                        if(os.path.exists(fn)):
                            startTime,junk,endTime = fileTimeRange(hfn)
                            ### FIXME added this part quickly to check for gaps
                            if sensor.endswith('samses_accel_es06'):
                                diffTime = startTime - prevEndTime
                                prevEndTime = endTime
                                print ">", diffTime/60, startTime, endTime, hfn
                            ###
                            dayHrs[sensor] = dayHrs[sensor] + (endTime-startTime)/3600 #Hours
                            dayMB[sensor] = dayMB[sensor] + os.path.getsize(fn) #bytes
                strOut = strOut + ',%.4f,%d' % (dayHrs[sensor],dayMB[sensor])
                #print '%s,%.4f,%d' % (sensor,dayHrs[sensor],dayMB[sensor])
        else:
            for sensor in parameters['sensorList']:
                strOut = strOut + ',%.4f,%.4f' % (dayHrs[sensor],dayMB[sensor])
        print >> outfile, strOut

        #Increment the day
        y, m ,d = nextDate(y, m, d)
        tStart = mktime((y,m,d,0,0,0,0,0,0))

    outfile.close()
    print 'done'

if __name__ == '__main__':
    for p in sys.argv[1:]: # parse command line
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
            print 'Pad times processing starting'
            mainLoop()
            sys.exit(0)

    printUsage()
