#!/usr/bin/env python
# $Id$

import os
import re
import padutils
from padpro import * 
#import padpro
from string import *
import struct
import csv
from math import *
import numpy as na
#from numpy import *
#from Numeric import *
#import Numeric as na
from jaxaConnect import *
from jaxaException import *
from time import *
from commands import *
from syslog import *
#from packetWriter import *
from pims.files.utils import overwrite_file_with_non_ascii_chars_removed

#Instantiate logging
jflog = InitLogging()

# convert roll, pitch, yaw into a 3 by 3 Float32 rotation matrix, inverting if requested
# examples:
# [ x'							 [ x
#	y'	 = rotationMatrix(...) *   y
#	z' ]						   z ]
#
# [x' y' z'] = [x y z] * transpose(rotationMatrix(...))
#
# [ x0' y0' z0'   = [ x0 y0 z0	
#	x1' y1' z1'   =   x1 y1 z1	 * transpose(rotationMatrix(...))
#	x2' y2' z2'   =   x2 y2 z2
#	 .	 .	 .		   .  .  .
#	xn' yn' zn' ] =   xn yn zn ]
#

#def rotationMatrix(roll, pitch, yaw, invert=0):
def rotationMatrix(rpw):
		# initialize array of floats
		#data = array.array('f')
		
	r = rpw[0] * pi/180 # convert to radians
	p = rpw[1] * pi/180
	w = rpw[2] * pi/180
	#(roll,pitch,yaw) = rpw	
	#r = roll * pi/180 # convert to radians
	#p = pitch * pi/180
	#w = yaw * pi/180
	cr = cos(r)
	sr = sin(r)
	cp = cos(p)
	sp = sin(p)
	cw = cos(w)
	sw = sin(w)
	rot = na.array([[cp*cw,		   cp*sw,		   -sp	],
				  [sr*sp*cw-cr*sw, sr*sp*sw+cr*cw, sr*cp],
				  [cr*sp*cw+sr*sw, cr*sp*sw-sr*cw, cr*cp]], na.float32)
#	rot = array(( [cp*cw,		   cp*sw,		   -sp	],
#				  [sr*sp*cw-cr*sw, sr*sp*sw+cr*cw, sr*cp],
#				  [cr*sp*cw+sr*sw, cr*sp*sw-sr*cw, cr*cp] ), Float32)
	#if invert: # invert is the same as transpose for any rotation matrix
	#	rot = rot.T
	return rot

###############################################################################    
# class to represent files from JAXA 
class jaxaFile(object):
	""" Class for JAXA File objects """
	def __init__ (self,filename,offsetRecs=0,numRecs=None,elementsPerRec=7,headerOnly=0):
		""" Initialize JAXA file """
		if filename:
			self.filename = filename
			# added quick fix for non-ascii characters (brute force remove and overwrite header file)
			#overwrite_file_with_non_ascii_chars_removed(filename + '.header') # << need this for Japanese chars in header files
			self.header = PadHeader(filename)
			self.separator =  os.path.basename(filename)[23]
			if headerOnly:
				#Read header and first lines of data file (not data)
				self.readHeaderLines(filename)
				self.data = []
				self.dateStart = stringTimeToUnix(os.path.basename(filename)[:23])
				self.dateStop = stringTimeToUnix(os.path.basename(filename)[24:47])
			else:
				#Get the data as well
				self.data = self.readFile(filename,offsetRecs,numRecs,elementsPerRec)
				self.dateStart = stringTimeToUnix(os.path.basename(filename)[:23]) + (offsetRecs/self.header.SampleRate)
				self.dateStop = self.dateStart + ((len(self.data)-1)/self.header.SampleRate)

	def __str__(self):
		s  = '\n filename: %s' % self.filename
		s += '\ndateStart: %s' % unixTimeToString(self.dateStart)
		s += '\ndateStop: %s' % unixTimeToString(self.dateStop)
		s += '\nseqCount: %d' % self.seqCount
		s += '\ndataNum: %d' % self.dataNum
		s += '\ndataNumHour: %d' % self.dataNumHour
		s += '\ncalc sampleRate: %5.1f' % self.sampleRate
		s += '\n*** header %s' % (44*'*')
		s += '\n%s' % str(self.header)
		s += '\n***  data: [ length is %d ] %s' % (len(self.data),22*'*')
		#s += '\n%s' % str(self.data)
		return s

	def remove_bad_chars(self, fname):
		"""remove non-ascii characters from header file"""
		print fname

	def readHeaderLines(self,filename):
		"""read only the information header from the data file"""

		#MMA data files have an information header
		headerLength = 16
		f = open(filename, mode='rb')
		s = f.read(headerLength)

		#fil is junk
		(self.seqCount,self.dataNum,self.dataNumHour,fil) = struct.unpack("<llll",s)
		self.sampleRate = float(self.dataNumHour)/3600
		f.close()

	def timeRange(self,units='sec'):
		"""Returns the total time of the file.	Based ont dateStart and dateStop"""
		uList = {'day':86400,'hr':3600,'min':60,'sec':1}
		if units not in uList.keys():
			units = 'sec'
		return (self.dateStop - self.dateStart)/uList[units]

	def getNumRecords(self,timeSpan=None,units='sec'):
		"""Gets the number of records based on a given timespan (in mseconds)"""
		if not timeSpan:
			return dataNum
		else:
			uList = {'day':86400,'hr':3600,'min':60,'sec':1}
			if units not in uList.keys():
				units = 'sec'
			return int(round(self.sampleRate*(timeSpan*uList[units])))


	def readFile(self,filename,offsetRecs=0,numRecs=None,elementsPerRec=7):
		""" read binary JAXA file as received by JAXA and return data as numarray 
			Returns an array of [t Tdacm Tx Ty Tz Ax Ay Az] where:
								[0	 1	 2	3  4  5  6	7 ]
				t is time in seconds
				T is temperature in Celsius
				A is acceleration in g
				x,y,z are Axes X, Y, Z respectively
				dacm is ?? 
		"""
		import array # need array module for fromfile function
		from stat import ST_SIZE

		# initialize array of floats
		#data = array.array('f')
		
		#MMA data files have an information header
		headerLength = 16
		f = open(filename, mode='rb')
		s = f.read(headerLength)
		
		#fil is junk
		(self.seqCount,self.dataNum,self.dataNumHour,fil) = struct.unpack("<llll",s)
		self.sampleRate = float(self.dataNumHour)/3600
		
		f.seek(headerLength +(offsetRecs*elementsPerRec*8)) # offset into file
		
		lf64 = na.dtype('<f8')

		if not numRecs:
			fileBytes = os.stat(filename)[ST_SIZE]
			data = na.fromfile(f,lf64,(fileBytes-headerLength)/8)			   # read to end of file
		else:
			data = na.fromfile(f,lf64,numRecs*elementsPerRec) # read numRecs of file
			
		f.close()

		#We need a time column in seconds
		numSamples = len(data)/elementsPerRec
		intA = na.arange(0,numSamples,1)
		t = na.reshape(intA.astype(lf64) / self.sampleRate,(-1,1))
		del intA

		data = na.reshape(data,(-1,elementsPerRec)) # reshape array

		#Update dataNum
		self.dataNum = numSamples

		#return (na.concatenate((t,d),axis=1))
		#DATA IN Micro-Gs!!
		# EK 05/25/2010 - Changing to G's.  
		return (na.concatenate((t,data),axis=1))
	
	def updateHeader(self,separator='+'):
		"""Updates the header with correct TimeZero, GData  file, ISSConfig etc"""
		
		#We need separator told to us, cant tell if it is after a gap or not
		if not (separator=='-' or separator == '+'):
			separator = '+' 

		#Fix the GData filename
		self.header.GData['file'] = '%s%s%s.%s' % (unixTimeToString(self.dateStart),separator,unixTimeToString(self.dateStop),self.header.SensorID.lower())
		self.header.GData['format'] = 'binary 32 bit IEEE float little endian' 
		
		#Set time zero
		self.header.TimeZero = unixTimeToString(self.dateStart)

		#Set the ISS Config from the database
		self.dbGetISSConfig()
	
	def writeAsPad(self,padRoot=None,separator=None):
		"""Writes the Jaxafile in PAD format"""
		import array # need array module for fromfile function
		from stat import ST_SIZE

		#Update the header stuff.	
		self.updateHeader(separator)
	
		if not padRoot:
			padRoot = os.getcwd()
		
		padPath = whichPadDir(self.header.GData['file'])
		padTargetDir = os.path.join(padRoot,padPath)
		self.filename = os.path.join(padTargetDir,self.header.GData['file'])

		if validDir(padTargetDir):
			#For PAD files we are only going to write t,x,y,z
			# initialize array of floats
			dout = array.array('f')
				
			#Transform the data
			self.transformCoord()
				
			#Write only t,x,y,z
			#Convert from microG to Gs
			#dslice = (1e-6)*self.data[:,[0,5,6,7]].copy()

			t = self.data[:,0].copy()
			t = t.reshape(t.shape[0],1)
			tempslice = (1e-6)*self.data[:,[5,6,7]].copy()
			dslice = (na.concatenate((t,tempslice),axis=1))
			del t
			del tempslice
		
			#Write data file
			try:
				fid = open(self.filename,mode='wb')
				dout.fromlist(dslice.flatten().tolist())
				dout.tofile(fid)
				fid.close()
			except IOError:
				jflog.error("Can not open %s for writing." % self.filename)
				return 0

			#Write the header
			headerFile = self.filename + '.header'
			try:
				fid = open(headerFile,mode='w')
				fid.write(self.header.buildHeader())
				fid.close()
			except IOError:
				jflog.error("Can not open %s for writing." % headerFile)
				return 0
			
			return self.filename	
		
		else:
			dflog.Critical('Not a valid target for PAD directory: %s' % padTargetDir)
			sys.exit()
		
	def transformCoord(self):
		"""Transforms acceleration data (if neeeded) to the designated coordinate system
			Expecting an entry for the sensor in the data_coord_system table on kyle 
		"""
		# Get the data coordinate system to write to
		csTo = self.dbGetDataCoordSys()
		
		#Get the current coordinate system from header info
		csFrom = self.getCoordinateSystem('Data')

		if (csTo['name'],csTo['time']) <> (csFrom['name'],csFrom['time']):
			#Transformation necessary	
			jflog.debug("Transforming from %s to %s" %(csFrom['name'],csTo['name']))
		
			#Matrix to go from SSA to Current Coord	
			T1 = rotationMatrix(csFrom['rpy']).round(10)

			# Matrix to go from SSA to Desired Coord
			T2 = rotationMatrix(csTo['rpy']).round(10)

			# Use inverse matrix of T1, since we are going from Current to SSA, 
			# Use T2 since we are then going from SSA to Desired 
			TM =  na.dot(T2,T1.T)
			TM =  TM.round(10)

			#Acceleration data
			dslice = self.data[:,5:8].copy()
			
			skip = 1	
			if skip:
				#Step through the data and perform the transformation
				count = 0
				for row in self.data:
					#Extract the accelerations
					A = row[5:8].reshape(3,1)
					#Transform
					Anew = na.dot(TM,A)
					#Insert New Values
					self.data[count,5:8] = Anew.reshape(1,3)

					count = count + 1

			#Update the header
			self.setCoordinateSystem('Data',csTo)
			
		else:
			jflog.debug("Coordinate systems are the same, no transformation")

	def setCoordinateSystem(self,s,cs):
		"""Sets a coordinate system (Seonsor or Data) to the header """
		if cs:
			if (s=='Data' or s =='Sensor'):
				self.header.setCoordSysInfo(s,cs)				
			else:
				dflog.error('Invalid option for setCoordinateSystem')
		else:
			dflog.error('No coordinate system information passed to setCoordianteSystem')

	def getCoordinateSystem(self,s):
		""" Retrieves a coordinate system (Sensor or Data) from the header"""
		cs ={}
		(cs['time'],cs['name'],cs['comment'],cs['rpy'],cs['xyz']) = self.header.getCoordSysInfo(s)
		return cs

	def dbGetISSConfig(self):
		"""Retrieves the ISS config for a given time period"""
		
		padConn = jaxaConnection(host='kyle', user='pims', passwd='YOUKNOW', db='pad')
		
		cmd = """SELECT iss_config FROM iss_config where time < %s ORDER BY TIME DESC LIMIT 1"""
		#print cmd
		results = sqlFetchOne(cmd % self.dateStart,padConn)
		if results:
			self.header.ISSConfiguration = results[0]
		
	def dbGetDataCoordSys(self):
		padConn = jaxaConnection(host='kyle', user='pims', passwd='YOUKNOW', db='pad')
		cmd = """SELECT coord_name FROM data_coord_system WHERE sensor = '%s' ORDER BY TIME DESC LIMIT 1"""
		results = sqlFetchOne(cmd % self.header.SensorID,padConn)
		
		#cmd = """SELECT coord_name FROM data_coord_system WHERE sensor = '121f02' ORDER BY TIME DESC LIMIT 1"""
		#results = sqlFetchOne(cmd,padConn)
		if results:
			dcs = results[0]
			cmd = """SELECT time,coord_name,r_orient,p_orient,y_orient,x_location,y_location,z_location,location_name FROM coord_system_db WHERE coord_name =  '%s' ORDER BY TIME DESC LIMIT 1"""
			results = sqlFetchOne(cmd % dcs,padConn)

			if results:
				cs = {}
				(cstime,cs['name'],r,p,w,x,y,z,cs['comment']) = results
				cs['time'] = unixTimeToString_NEW(cstime)
				cs['rpy'] = (r,p,w)
				cs['xyz'] = (x,y,z)
				return cs
			else:
				jflog.critical('Could not retrieve coordinate system info for sensor')
				sys.exit()
		else:
			jflog.critical('Could not retrieve Data coordinate system for sensor')
			sys.exit()
			

		#if results:
		#	 (fn['id'], fn['filename'],fn['path'],fn['hasheader'],fn['filesize'],fn['initdate'],fn['lastupdate'],fn['lastmodified'],fn['copied'],fn['processed']) = results

		return results



###############################################################################    
# MAIN 
if __name__ == '__main__':
	#from apihelper import info
	#s = jaxaFile(filename='/home/pims/2008_08_05_19_49_02.000+2008_08_05_20_49_02.000.0bbd') 
	#s = jaxaFile(filename='/home/pims/2008_08_05_19_49_02.000+2008_08_05_20_49_02.000.0bbd',headerOnly=1) 

	#s =jaxaFile(filename ='/misc/yoda/pub/jaxa/year2008/month08/day06/mma_accel_0bbc/2008_08_06_00_49_02.000+2008_08_06_01_49_02.000.0bbc',offsetRecs=0,numRecs=732420)
	s =jaxaFile(filename ='/misc/yoda/pub/jaxa/year2008/month08/day06/mma_accel_0bbb/2008_08_06_23_55_38.000+2008_08_07_00_55_38.000.0bbb',offsetRecs=0,numRecs=732420)
	#s =jaxaFile(filename ='/misc/yoda/pub/jaxa/year2008/month08/day06/mma_accel_0bbb/2008_08_06_23_55_38.000+2008_08_07_00_55_38.000.0bbb',offsetRecs=0,numRecs=100000)
	#s = jaxaFile(filename='/home/pims/2008_08_05_19_49_02.000+2008_08_05_20_49_02.000.0bbd',offsetRecs=0,numRecs=732420) 

	#print s.data.shape
	#s.writeAsPad('/home/pims/tmp','+')
	#s.dbGetDataCoordSys()
	s.dbGetISSConfig()
	print s.header.buildHeader()
#	print s
	#s = jaxaFile(filename='/home/pims/jaxa/20070919144726-20070919144825.0bb9')

