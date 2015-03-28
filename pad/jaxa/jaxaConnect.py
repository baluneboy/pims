from MySQLdb import *
from jaxaException import *
from _mysql_exceptions import *
from time import *
from commands import *
from string import *
from syslog import *
#import sys, string, time, logging
import sys
import logging,logging.config

# SQL helper routines ---------------------------------------------------------------
# create a connection (with possible defaults), submit command, return all results
# try to do all connecting through this function to handle exceptions

# write message to jaxa log or syslog and console
def printLog(message,debugLevel=1):
	#if debugLevel
	print message
	syslog(LOG_WARNING|LOG_LOCAL0, message)

# convert "Unix time" to "Human readable" time
def UnixToHumanTime(utime, altFormat = 0):
	fraction = utime - int(utime)
	cmd = 'date -u -d "1970-01-01 %d sec" +"%%Y %%m %%d %%H %%M %%S"' % int(utime)
	try:
		result = getoutput(cmd)
		s = split(result)
		s[5] = atoi(s[5]) + fraction
	except ValueError, err:
		t = 'date conversion error\ndate command was: %sdate command returned: %s' % (cmd, result)
		printLog(t)
		raise 'ValueError', err
	if not altFormat:
			return "%s_%s_%s_%s_%s_%06.3f" % tuple(s)
	else:
		return "%s/%s/%s %s:%s:%06.3f" % tuple(s)

# convert "Human readable" to "Unix time" time
def HumanToUnixTime(month, day, year, hour, minute, second, fraction = 0.0):
	cmd = 'date -u -d "%d/%d/%d %d:%d:%d UTC" +%%s' % tuple((month, day, year, hour, minute, second))
	try:
		result=int(getoutput(cmd)) + fraction
	except ValueError, err:
		t = 'date conversion error\ndate command was: %sdate command returned: %s' % (cmd, result)
		printLog(t)
		raise 'ValueError', err
	return result

def jaxaConnection(host='localhost', user='pims', passwd='YOUKNOW', db='jaxa',init_command = 'SET sql_mode=STRICT_ALL_TABLES'):
	try:
		con = Connection(host=host, user=user, passwd=passwd, db=db)
		return con
	except MySQLError, msg:
		t = UnixToHumanTime(time(), 1) + '\n' + msg[1]
		printLog(t)
	
def sqlFetchAll(command,scon=None,returnDescription=None):
		if scon:
			con = scon
		else:
			con = jaxaConnection()
			
		try:
			cursor = con.cursor()
			cursor.execute(command)
			description = cursor.description
			results = cursor.fetchall()
			cursor.close()
		except MySQLError, msg:
			results = None
			t = UnixToHumanTime(time(), 1) + '\n' + msg[1] + '\nMySQL call failed for %s' % command
			printLog(t)
		if returnDescription:
			return (results,description)
		else:
			return results

def sqlFetchOne(command,scon=None):
		if scon:
			con = scon
		else:
			con = jaxaConnection()

		try:
			cursor = con.cursor()
			cursor.execute(command)
			results = cursor.fetchone()
			cursor.close()
		except MySQLError, msg:
			results = None
			t = UnixToHumanTime(time(), 1) + '\n' + msg[1] + '\nMySQL call failed for %s' % command
			printLog(t)
		return results

def sqlInsertOne(command, cmdparms,scon=None):

		if scon:
			con = scon
		else:
			con = jaxaConnection()
		
		try:
			cursor = con.cursor()
			numInserted = cursor.execute(command,cmdparms)
		except MySQLError, msg:
			t = UnixToHumanTime(time(), 1) + '\n' + msg[1] + '\nMySQL call failed for %s' % command
			printLog(t)
			numInserted=None
		
		cursor.close()
		if numInserted != 1: 
			con.rollback()
			return 0
		else:
			con.commit()
			return numInserted

def sqlInsertMany(command, cmdparms,scon=None):
		if scon:
			con = scon
		else:
			con = jaxaConnection()
		
		try:
			cursor = con.cursor()
			numInserted = cursor.executemany(command,cmdparms)
		except MySQLError, msg:
			t = UnixToHumanTime(time(), 1) + '\n' + msg[1] + '\nMySQL call failed for %s' % command
			printLog(t)
			numInserted=None
		
		cursor.close()
		if numInserted != len(cmdparms):
			con.rollback()
			return 0
		else:
			con.commit()
			return numInserted

def isNotNone(x):
	#Returns true if not none
	return x is not None

class DBHandler(logging.Handler):
	"""Handler class to log to the database"""
	def __init__(self, dsn, uid='', pwd='',scon=None):
		logging.Handler.__init__(self)

		self.dsn = dsn
		self.uid = uid
		self.pwd = pwd

		if scon:
			self.conn = scon
		else:
			self.conn = jaxaConnection()

		self.SQL = """INSERT INTO log ( created, relativecreated, name, levelno, levelname, message, filename, pathname, lineno,msecs,exc_text,thread) VALUES ( '%(dbtime)s', %(relativeCreated)d, '%(name)s', %(levelno)d, '%(levelname)s', '%(message)s', '%(filename)s', '%(pathname)s', %(lineno)d,%(msecs)d,'%(exc_text)s','%(thread)s');
				   """
		self.cursor = self.conn.cursor()

	def formatDBTime(self, record):
		record.dbtime = strftime("%Y-%m-%d %H:%M:%S", localtime(record.created))

	def emit(self, record):
		try:
			#use default formatting
			self.format(record)
			#now set the database time up
			self.formatDBTime(record)
			if record.exc_info:
				record.exc_text = logging._defaultFormatter.formatException(record.exc_info)
			else:
				record.exc_text = ""
				
			sql = self.SQL % record.__dict__
			self.cursor.execute(sql)
			self.conn.commit()
		except:
			import traceback
			ei = sys.exc_info()
			traceback.print_exception(ei[0], ei[1], ei[2], None, sys.stderr)
			del ei

	def close(self):
		self.cursor.close()
		self.conn.close()
		logging.Handler.close(self)

logging.jaxaHandler = DBHandler

def InitLogging():
	#Instantiate logging
	logging.config.fileConfig('jaxalog.conf')
	dblog = logging.getLogger('log02.log03')
	return dblog

#dh = DBHandler('Logging')
#logger = logging.getLogger("")
#logger.setLevel(logging.DEBUG)
#logger.addHandler(dh)
#logger.info("Jackdaws love my big %s of %s", "sphinx", "quartz")
#logger.debug("Pack my %s with five dozen %s", "box", "liquor jugs")
#try:
#	import math
#	math.exp(1000)
#except:
#	logger.exception("Problem with %s", "math.exp")
#logging.shutdown()
		
