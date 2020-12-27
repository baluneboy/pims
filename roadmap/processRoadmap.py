#!/usr/bin/env python

from string import *
import struct
import os, sys
from socket import gethostname
import shutil
from commands import *
from roadmapConnect import *
from roadmapFile import *
from jaxaException import *
from time import *
from datetime import *

from commands import *
from syslog import *
from MySQLdb import *

#Instantiate logging
log = InitLogging()

# set default command line parameters, times are always measured in seconds
defaults = {'host':'yoda',								# the name of the computer with the database
	'database':'pimsmap',							# the name of the database to connect to
	'roadmapDirectory':'/misc/yoda/www/plots/batch', # the directory where the roadmap files are located 
	'mode':'pave',								# pave or repair.  Pave starts at next day in the lastrun table entry.	repair looks for changes in all directories.	
	'paveLag':'1',								# Do not pave until 5 days have past. Roadmaps aren't made until 5 days later  
	'logLevel':'1',								# show or supress warning message
	'repairYear':'0',							#Repairs operate on a per-year-basis.  Set to 0 for current year.
	'repairModTime':'0',						#Number of days since the file was modified, needs to be a positive integer.  Mandatory when repairing. 
	'quitWhenDone':'0'}

parameters = defaults.copy()


def parametersOK():

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
	
	b = parameters['mode']
	if b != 'pave' and b != 'repair':
		msg = ' mode must be pave or repair'
		log.warning(msg)
		return 0
	
	b = parameters['paveLag']
	parameters['paveLag'] = atoi(parameters['paveLag'])
	
	b = parameters['repairYear']
	if b == '0':
		dtNow = date.today()
		parameters['repairYear'] = str(dtNow.year)
		log.debug('No repairYear provided, defaulting to current (%s)' % parameters['repairYear'])
	
	b = parameters['repairModTime']
	if b == '0' and parameters['mode'] == 'repair':
		msg = 'repairModtime must be a positive integer when mode is repair.'
		log.warning(msg)
		return 0
	parameters['repairModTime'] = atoi(parameters['repairModTime'])

	b = parameters['roadmapDirectory']
	if not os.path.isdir(b):
		msg = ' roadmapDirectory is not a directory or does not exist'
		log.warning(msg)
		return 0
	parameters['roadmapDirectory']	= os.path.abspath(b)	

	return 1

def jaxaSetParameters(newParameters):
	global parameters
	parameters = newParameters.copy()

def printUsage():
	print 'usage: packetWriter.py [options]'
	print '		  options (and default values) are:'
	for i in defaults.keys():
		print '			   %s=%s' % (i, defaults[i])

def getYMDPath(year,month,day):
	return os.path.join('year%04d/month%02d/day%02d'%(year,month,day))

def date2Path(dtTime):
	return getYMDPath(dtTime.year,dtTime.month,dtTime.day)

def getFileList(dir_name, subdir=False, *args):
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

def getDayList(dirPath=None,year=None,month=None,day=None):
	"""Gets a list of plots from a day directory"""
	if not dirPath: 
		if (year and month and day):
			fileDir = parameters['roadmapDirectory']
			fullPath  = os.path.join(fileDir,getYMDPath(year,month,day))
		else:
			log.critical("Bad input to getDayList")
	else:
		fullPath = dirPath

	if not os.path.isdir(fullPath):
		log.critical("Directory inputted to getDayList does not exist: %s" % fullPath)
	
	#List of plot files
	rmFiles = getFileList(fullPath,False,'pdf','jpg')
	return rmFiles

def dbGetCurrentState(): 
	"""Gets the last day the paver processed from the lastrun table, based on roadmap directory """
	cmd = """SELECT id,lrdate,year,month,day FROM lastrun WHERE rootdir = '%s' AND mode='pave'"""
	results = sqlFetchOne(cmd % parameters['roadmapDirectory'])
	
	if results:
		(id,lastRunDate,lastRunYear,lastRunMonth,lastRunDay) = results

		dtLastDirDate = date(lastRunYear,lastRunMonth,lastRunDay)
		return (id,dtLastDirDate)
	else:
		log.critical("No entry in the lastrun table for the current directory: %s.	Is path correct?" % parameters['roadmapDirectory'])
		sys.exit()

def dbUpdateCurrentState(stateId,dirDate): 
	"""Updates the last day the paver processed from the lastrun table, based on lastrun id """
	hostname = gethostname()

	cmd = """UPDATE lastrun SET lrdate=now(),year=%s,month=%s,day=%s,host='%s' WHERE id = %s"""
	results = sqlFetchOne(cmd%(dirDate.year,dirDate.month,dirDate.day,hostname,stateId))

def dbUpdateLastRepairRun(year): 
	"""Gets the last day the repair process ran for the year the lastrun table. If no record, inputs todays date"""
	
	hostname = gethostname()
	roadmapDir = parameters['roadmapDirectory']
	#cmd = """SELECT id,lrdate,year,month,day FROM lastrun WHERE rootdir = '%s' AND year='%s' AND mode='repair'"""
	cmd = """SELECT id,lrdate FROM lastrun WHERE rootdir = '%s' AND year='%s' AND mode='repair'"""
	results = sqlFetchOne(cmd % (roadmapDir,year))
	
	if results:
		(id,dtLastRunDate) = results
		cmd = """UPDATE lastrun set lrdate=now() WHERE id = %s"""
		results = sqlFetchOne(cmd % id)
		log.debug ('Updated lastrun record for %s, year%s' % (roadmapDir,year))	
	else:
		cmd = """INSERT INTO lastrun (lrdate,host,year,rootdir,mode) VALUES(now(),'%s',%s,'%s','repair')"""
		results = sqlFetchOne(cmd % (hostname,year,roadmapDir))
		log.debug ('Inserted lastrun record for %s, year%s' % (roadmapDir,year))	

def getModifiedFiles():
	"""Gets a list of modified miles based on year directory, roadmap root and repairModTime"""
	repairModTime = parameters['repairModTime']
	repairYear = parameters['repairYear']
	roadmapDir = parameters['roadmapDirectory']

	fullPath  = os.path.join(roadmapDir,'year%s' % repairYear)
	
	#Get a list of files that have changed, 
	#Command will take the form of:
	#cmd = """find /misc/yoda/www/plots/batch/year2009/ -mtime -7 -regex '.*[pdf|jpg]'"""
	cmd = """find %s -mtime -%s -regex '.*[pdf|jpg]'""" % (fullPath,repairModTime)

	txtFiles = getoutput(cmd) 
	modFiles = txtFiles.split('\n');
	for mf in modFiles:
		print mf
		if os.path.exists(mf):
			rmFile = roadmapFile(mf)
			if not rmFile.dbGetId():
				rmFile.dbInsertFile()
				log.debug("Inserted: %s" % rmFile.filename)
				if not rmFile.id:
					log.critical("Problem inserting %s" % rmFile) 
					sys.exit()
	dbUpdateLastRepairRun(repairYear)

def processDirectory(dirPath):
	numFiles = 0
	rmFiles = getDayList(dirPath)
	for pf in rmFiles:
		rmFile = roadmapFile(pf)
		#print rmFile.dbGetId()	
		if not rmFile.dbGetId():
			#print "rmFile.dbInsertFile()"
			rmFile.dbInsertFile()
			if not rmFile.id:
				log.critical("Problem inserting %s" % rmFile) 
				#Removed exit on failure -- just log the failures and keep going
				#sys.exit()
		#log.debug("Inserted: %s" % rmFile.filename)
		numFiles = numFiles + 1
		#print "The rmFile %s:" % rmFile
	print '.',
	return numFiles

def mainLoop():
	#print 'Main Loop'
	numFiles = 0
	roadmapDir = parameters['roadmapDirectory']
	if parameters['mode'] == 'pave':
		log.debug('Roadmap paving starting')
		
		(stateId,dtLastDirDate) = dbGetCurrentState() 
		dtCurrDirDate = dtLastDirDate + timedelta(days=1);
		
		dtNow = date.today()
		
		while ((dtNow-dtCurrDirDate).days > parameters['paveLag']):
			dirPath  = os.path.join(roadmapDir,date2Path(dtCurrDirDate))
			if os.path.isdir(dirPath):
				numFiles = numFiles + processDirectory(dirPath)
			dbUpdateCurrentState(stateId,dtCurrDirDate)	
			dtCurrDirDate = dtCurrDirDate + timedelta(days=1);
		log.info('%d files processed.' % numFiles)
		#if ((dtNow-dtCurrDirDate).days < parameters['paveLag']):
		log.info('Roadmap cataloging process up to date.  Paving halted.')
		sys.exit()
	
	elif parameters['mode'] == 'repair':
	
		log.debug('Roadmap repair starting')
		#dtNow = date.today()
		#repairYear = parameters['repairYear']
		
		
		#Get (or input) last run for that year
		#(id,dtDateLastRun) = dbGetLastRepairRun(repairYear)
		getModifiedFiles()	
			
	else:
		log.warning ('Invalid mode sent to roadmap process: %s' % parameters['mode'])
		

if __name__ == '__main__':

	for p in sys.argv[1:]:	# parse command line
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
			mainLoop()
			sys.exit(0)

	printUsage()
