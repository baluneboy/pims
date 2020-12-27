#!/usr/bin/env python
# $Id$

import os
import re
from string import *
import struct
import csv
from roadmapConnect import *
from time import *
from commands import *
from syslog import *

#Instantiate logging
rmlog = InitLogging()

###############################################################################
# class to represent files from JAXA
class roadmapFile(object):
	""" Class for roadmapFile objects """
	def __init__ (self,filename):
		""" Initialize roadmap file """
		self.id = 0

		if filename:
			self.filename = os.path.basename(filename)
			self.fullpath = os.path.abspath(filename)
			self.directory = os.path.dirname(filename)
			if not self.directory:
				rmlog.critical('Filename requires full path: %s' % filename)
				sys.exit()

				#self.dateStart = stringTimeToUnix(os.path.basename(filename)[:23])
				#self.dateStop = stringTimeToUnix(os.path.basename(filename)[24:47])
		if (self.filename):
			#rmlog.debug('Working on file: %s' % self.filename)
			#r =  split(self.filename, '_')

			#Look for Cold Atom Lab gvt3 daily plots; e.g. 2018_06_01_00_00_00.000_121f04_gvt3_daily500.pdf
			if self.filename.find('gvt3_daily') >= 0:
				[self.year,self.month,self.day,self.hour,self.minute,self.second,self.sensor,self.plot,theRest] =  split(self.filename, '_')
				[dailyFs,junk2] =  split(theRest, '.')
				self.samplerate = dailyFs.replace('daily', '')
			#Look for zbot special quasi-steady estimate
			elif self.filename.find('ossbtmf_gvt3_historical_time-shifted_quasi-steady_estimate') >= 0:
				[self.year,self.month,self.day,self.hour,self.minute,self.second,self.sensor,self.plot,junk1,junk2,junk3,junk4] =  split(self.filename, '_')
				self.samplerate = '0.0625' # FIXME this naively assumes what it should not due to poor filename convention...tsk...tsk...tsk
			#Look for ossbtmf, they don't have minutes, seconds or samplerate in the file name
			elif self.filename.find('ossbtmf') >= 0:
				[self.year,self.month,self.day,self.hour,self.sensor,theRest] =  split(self.filename, '_')
				[self.plot,junkme] =  split(theRest,'.')
				self.samplerate = '0.01'
				self.minute = 0
				self.second = 0
			#One-third octave has extrah 8h field and a Hz on the samplerate
			elif self.filename.find('_otos_') >= 0:
				[self.year,self.month,self.day,self.hour,self.minute,self.second,self.sensor,self.plot,plotlength,theRest] =  split(self.filename, '_')
				#theRest is like 200hz.pdf
				[self.samplerate,junkme]  = split(theRest,'hz')
			# FIXME as quick-fix, Hrovat added this "elif" condition to capture ugrms summary plots (for now)
			# LIKE 2012_01_31_00_00_00.000_121f02_ug030d04h000p000-010p000hz.pdf
			elif self.filename.find('_ug') >= 0:
				self.plot = 'ugrmsd'
				[self.year,self.month,self.day,self.hour,self.minute,self.second,self.sensor,theRest] =  split(self.filename, '_')
			# theRest is LIKE ug030d04h000p000-010p000hz.pdf
				self.samplerate = '0'
			elif self.filename.endswith('_ann.pdf'):
				[self.year,self.month,self.day,self.hour,self.minute,self.second,self.sensor,self.plot,theRest,trash_ann] =  split(self.filename, '_')
				[junkme,theRest]  = split(theRest,'roadmaps') # gives theRest LIKE 1000_ann.pdf
				self.samplerate = theRest.replace('p','.')
			# FIXME as quick-fix, Hrovat added this "elif" condition to capture mams_temps plots (for now)
			elif self.filename.find('_mams_temps')>=0:
				self.plot = 'tmp'
				[self.year, self.month, theRest] =  split(self.filename, '-')
			# theRest is LIKE 26_mams_temps.pdf (with day of month as prefix here)
				[self.day, junk, theRest] = split(theRest, '_')
				self.hour = self.minute = self.second = 0
				self.sensor = 'mamstemp'
				self.samplerate = '0.001'
			else:
				[self.year,self.month,self.day,self.hour,self.minute,self.second,self.sensor,self.plot,theRest] =  split(self.filename, '_')
				if self.filename.find('gsummary')>=0:
					[junkme,theRest]  = split(theRest,'gsummary')
				elif self.filename.find('ccaacdra')>=0:
					[junkme,theRest]  = split(theRest,'ccaacdra')
				elif self.filename.find('hrfrack')>=0:
					[junkme,theRest]  = split(theRest,'hrfrack')
				elif self.filename.find('tvis')>=0:
					[junkme,theRest]  = split(theRest,'tvis')
				elif self.filename.find('otgs')>=0:
					[junkme,theRest]  = split(theRest,'otgs')
				elif self.filename.find('nyquist')>=0:
					#SAMS FF can have "raodmapsnyquist" as well as roadmaps
					[junkme,theRest]  = split(theRest,'roadmapsnyquist')
				else:
					[junkme,theRest]  = split(theRest,'roadmaps')
				#theRest could be samplerate.pdf or sampleratep7.pdf.
				[theRest,junkme] =  split(theRest,'.')
				#now theRest could be [sampleratep7] or [samplerate]
				self.samplerate = theRest.replace('p','.')
			self.date = '%s-%s-%s' % (self.year,self.month,self.day)
			#theRest =  split(theRest,'p7')

			#if len(theRest) == 2:
			#               self.samplerate = theRest[0]
			#       else:
			#               self.samplerate = split(theRest[0],'.')[0]

	def __str__(self):
		s  = '\nFilename: %s' % self.filename
		s  += '\nId: %s' % self.id
		s  += '\nPath: %s' % self.fullpath
		s  += '\nDirectory: %s' % self.directory
		s  += '\nPlot Type: %s' % self.plot
		s += '\nDate: %s/%s/%s' % (self.year,self.month,self.day)
		s += '\nTime: %s:%s:%s' % (self.hour,self.minute,self.second)
		s += '\nSensor: %s' % self.sensor
		s += '\nCutoff: %s' % self.samplerate
		return s

	def dbGetId(self):

		cmd = """SELECT id FROM roadmap WHERE name = '%s'"""
		results = sqlFetchOne(cmd % self.filename)

		if results:
			self.id = results[0]
		else:
			self.id = 0

		return self.id

	def dbInsertFile(self):
		plotId = []
		sensorId = []

		if (self.id == 0):
			# Get plot id
			cmd = """SELECT id FROM plottype WHERE abbr = '%s' """
			results = sqlFetchOne(cmd % self.plot)
			if results:
				plotId = results[0]
			else:
				rmlog.warning('Unknown plottype : %s' % self.sensor)
				sys.exit()

			# Get sensor id
			cmd = """SELECT id FROM sensor WHERE abbr = '%s' """
			results = sqlFetchOne(cmd % self.sensor)
			if results:
				sensorId = results[0]
			else:
				rmlog.warning('Unknown sensor : %s.  Insertion failed.' % self.sensor)
				#sys.exit()

			#Insert record
			try:
				#cmd = """INSERT INTO roadmap (name,plot_id,sensor_id,year,month,day,samplerate) VALUES('%s',%s,%s,%s,%s,%s,%s) """ % (self.filename,plotId,sensorId,self.year,self.month,self.day,self.samplerate)
				cmd = """INSERT INTO roadmap (name,plot_id,sensor_id,year,month,day,samplerate,date) VALUES('%s',%s,%s,%s,%s,%s,%s,'%s') """ % (self.filename,plotId,sensorId,self.year,self.month,self.day,self.samplerate,self.date)
				results = sqlInsertOne(cmd,[])
			except:
				rmlog.critical("Problem inserting file into database: %s" % cmd)

			self.dbGetId()




###############################################################################
# MAIN
if __name__ == '__main__':
	#from apihelper import info

	#s =jaxaFile(filename ='/misc/yoda/pub/jaxa/year2008/month08/day06/mma_accel_0bbc/2008_08_06_00_49_02.000+2008_08_06_01_49_02.000.0bbc',offsetRecs=0,numRecs=732420)
	s = roadmapFile(filename ='/misc/yoda/www/plots/batch/year2003/month01/day01/2003_01_01_00_00_00_121f03_otos_8h_200hz.pdf')
	s = roadmapFile(filename ='/misc/yoda/www/plots/batch/year2018/month06/day01/2018_06_01_08_00_00.000_121f04_gvt3_daily500.pdf')
	print s
	#print s.dbGetId()
	#s.dbInsertFile()

#       print s
	#s = jaxaFile(filename='/home/pims/jaxa/20070919144726-20070919144825.0bb9')
