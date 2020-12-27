#!/usr/bin/env python
version = '$Id'

import os, sys
from padutils import *
from string import *
from commands import *
from math import *
import createheaderdict as chd
#import numarray as na
import Numeric as na
import copy
from fraction import *

def whichPadDir(padFileName):
    """Returns the directory structure that a PAD file should go into like yearYYYY/monthMM/dayDD/sensor"""
    #Only works on mma_accel files
    padFileName = split(padFileName, '.header')[0] # throw away '.header'
    sensor =  split(padFileName, '.')[-1]
    padFileName = join(split(padFileName, '.')[:-1], '.')
    pair = split(padFileName, '-')
    if len(pair) == 1:
        pair = split(padFileName, '+')
    (startDate,endDate) = pair
    (year,month,day,hour,minute,seconds) = startDate.split('_')

    return os.path.join('year%s'%year,'month%s'%month,'day%s'%day,'mma_accel_%s'%sensor)

def validDir(dirname):
    if os.path.isdir(dirname):
        return 1
    else:
        os.makedirs(dirname)
        return 1

def readPadFile(padFile,offsetRecs=0,numRecs=None,elementsPerRec=4):
	""" read binary PAD file and return data as numarray """
	import array # need array module for fromfile function
	from stat import ST_SIZE
	# initialize array of floats
	data = array.array('f')
	f = open(padFile, mode='rb')
	f.seek(offsetRecs*elementsPerRec*4) # offset into file
	if not numRecs:
		fileBytes = os.stat(padFile)[ST_SIZE]
		data.fromfile(f,fileBytes/4)			# read to end of file
	else:
		data.fromfile(f,numRecs*elementsPerRec) # read numRecs of file
	f.close()
	d = na.array(data,typecode=na.Float32)		# initialize output array
	d = na.reshape(d,(len(data)/elementsPerRec),elementsPerRec) # reshape array
	return d

class Pad(object):
	"""
	PIMS Acceleration Data (PAD) object created from file
	like this: p = Pad(filename)
	"""

	def __init__ (self,filename,offsetRecs=0,numRecs=None,elementsPerRec=4):
		""" initialize Pad """
		self.filename = filename
		self.header = PadHeader(filename)
		self.data = readPadFile(filename,offsetRecs,numRecs,elementsPerRec)
		self.dateStart = stringTimeToUnix(os.path.basename(filename)[:23]) + (offsetRecs/self.header.SampleRate)
		self.dateStop = self.dateStart + ((len(self.data)-1)/self.header.SampleRate)
		
	def __str__(self):
		s  = '\n filename: %s' % self.filename
		s += '\ndateStart: %s' % unixTimeToString(self.dateStart)
		s += '\n dateStop: %s' % unixTimeToString(self.dateStop)
		s += '\n*** header %s' % (44*'*')
		s += '\n%s' % str(self.header)
		s += '\n***  data: [ length is %d ] %s' % (len(self.data),22*'*')
		s += '\n%s' % str(self.data)
		return s

	def __len__(self):
		return len(self.data)

	def __sub__(self,other):
		""" return gap filled with relative time column and NaN xyz values (or overlap neg. number of pts) """
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
			print '2nd chunk start:', unixTimeToString(t2)
			print '1st chunk start:', unixTimeToString(t0)
			raise RuntimeError, '2nd chunk starts BEFORE 1st'
		elif ( (t2 >= t0) and (t3 <= t1) ):
			print '1st chunk start:', unixTimeToString(t0)
			print '2nd chunk start:', unixTimeToString(t2)
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
		T = na.arange(0,(N+1.0)/fs,(1.0/fs))  # overshoot to get around arange issue
		t = na.reshape(T[:N],(N,1))			  # truncate at needed number of pts (N)
		xyz = na.zeros((N,3),na.Float32) + (1e333333/1e333333) # Better way to get NaN array?
		gap.data = na.concatenate((t,xyz),1) # horizontal concatenation
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
		t = na.arange(0,newLen/fs,(1.0 / fs),shape=(newLen,1))
		xyz = na.concatenate((self.data[:,1:4],gap.data[:,1:4],other.data[:,1:4]),0)
		new.data = na.concatenate((t,xyz),1)
		return new

class PadHeader(object):
	"""
	PIMS Acceleration Data (PAD) header object created from header file
	like this: h = PadHeader(filename)
	"""

	def __init__ (self,filename):
		""" initialize PadHeader """
		if split(filename,'.')[-1] != 'header': filename += '.header'
		dHeader = chd.main(['headerFile=' + filename])	  # get header dict
		for k,v in dHeader.iteritems(): setattr(self,k,v) # this does dynamic set attribute
		self.SampleRate = float(self.SampleRate)
		self.CutoffFreq = float(self.CutoffFreq)
		# parse coord sys info from subdict and convert xyz/rpy to float numarrays
		for coord in ['SensorCoordinateSystem','DataCoordinateSystem']:
			self.parseCoord(['x','y','z'],coord)
			self.parseCoord(['r','p','w'],coord)
		
	def __str__(self):
		s  = '\n  DataType: %s' % self.DataType
		s += '\n  SensorID: %s' % self.SensorID
		s += '\nSampleRate: %7.2f sa/sec' % self.SampleRate
		s += '\nCutoffFreq: %7.2f Hz' % self.CutoffFreq
		s += '\n%s' % self.showCoordSys('Data')
		s += '\n%s' % self.showCoordSys('Sensor')
		return s

	def __cmp__(self, other):
		""" compare instances of PadHeader (see http://www.python.org/doc/current/ref/customization.html) """
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
				if not na.alltrue(S == H):
					print '??? %sCoordinateSystem%s mismatch ???' % (c,ax)
					return -1
		return 0

	def parseCoord(self,L,coord):
		""" parse dict and convert xyz or rpy into float numarray """
		dCoord = getattr(self,coord)
		Lxyz = []
		for ax in L:
			Lxyz.append(float(dCoord.__getitem__(ax)))
		xyz = na.array(Lxyz,typecode=na.Float32)
		S = reduce(lambda x,y: x+y, L)
		setattr(self,coord + upper(S),xyz)
		setattr(self,coord + 'Name',dCoord['name'])
		setattr(self,coord + 'Comment',dCoord['comment'])
		setattr(self,coord + 'Time',dCoord['time'])
	
	def setCoordSysInfo(self,s,cs):
		"""Sets the approprate coordinate system info, expecting a string and a dictionary"""
		coord = '%sCoordinateSystem' % s
		setattr(self,'%sName' % coord,cs['name'])		
		setattr(self,'%sComment' % coord,cs['comment'])		
		setattr(self,'%sTime' % coord,cs['time'])		
		setattr(self,'%sXYZ' % coord,cs['xyz'])
		setattr(self,'%sRPW' % coord,cs['rpy'])
		
	def getCoordSysInfo(self,s):
		"""Returns a tuple with the appropriate coordinate system"""
		return (getattr(self,s + 'CoordinateSystemTime'),getattr(self,s + 'CoordinateSystemName'),getattr(self,s + 'CoordinateSystemComment'),
			tuple(getattr(self,s + 'CoordinateSystemRPW')),tuple(getattr(self,s + 'CoordinateSystemXYZ')))


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
	
	def buildCoordSys(self,s):
		""" Generate XML for coord sys """
		t = '<%sCoordinateSystem ' % s
		t += 'name="%s" ' % (getattr(self,s + 'CoordinateSystemName'))
		t += 'r="%.1f" p="%.1f" w="%.1f" ' % tuple(getattr(self,s + 'CoordinateSystemRPW'))
		t += 'x="%0.2f" y="%.2f" z="%.2f" ' % tuple(getattr(self,s + 'CoordinateSystemXYZ'))
		#t += 'comment="%s"' % (s + 'CoordinateSystemComment',getattr(self,s + 'CoordinateSystemComment'))
		t += 'comment="%s" ' % (getattr(self,s + 'CoordinateSystemComment'))
		t += 'time="%s"' % (getattr(self,s + 'CoordinateSystemTime'))
		t += '/>\n' 
		return t
	
	def buildBiasCoeff(self):
		""" Generate XML for BiasCoeff """
		t = '<BiasCoeff '
		t += 'x="%s" y="%s" z="%s"' % (self.BiasCoeff['x'],self.BiasCoeff['y'],self.BiasCoeff['z'])
		t += '/>\n' 
		return t
	
	def buildScaleFactor(self):
		""" Generate XML for ScaleFactor """
		t = '<ScaleFactor '
		t += 'x="%s" y="%s" z="%s"' % (self.ScaleFactor['x'],self.ScaleFactor['y'],self.ScaleFactor['z'])
		t += '/>\n' 
		return t
	
	def buildHeader(self):
		""" Generate XML header """
	
		strHeader = '<?xml version="1.0" encoding="US-ASCII"?>\n'
		strHeader = strHeader + '<%s>\n' % self.DataType
		strHeader = strHeader + '\t<SensorID>%s</SensorID>\n' % self.SensorID 
		strHeader = strHeader + '\t<TimeZero>%s</TimeZero>\n' % self.TimeZero
		strHeader = strHeader + '\t<SampleRate>%s</SampleRate>\n' % self.SampleRate
		strHeader = strHeader + '\t<CutoffFreq>%s</CutoffFreq>\n' % self.CutoffFreq
		strHeader = strHeader + '\t<GData format="%s" file="%s"/>\n' % (self.GData['format'],self.GData['file'])
		strHeader = strHeader + '\t' + self.buildBiasCoeff()
		strHeader = strHeader + '\t' + self.buildCoordSys('Sensor')
		strHeader = strHeader + '\t' + self.buildCoordSys('Data')
		strHeader = strHeader + '\t<DataQualityMeasure>%s</DataQualityMeasure>\n' % self.DataQualityMeasure
		strHeader = strHeader + '\t<ISSConfiguration>%s</ISSConfiguration>\n' % self.ISSConfiguration
		strHeader = strHeader + '\t' + self.buildScaleFactor()
		strHeader = strHeader + '</%s>\n' % self.DataType
		
		return strHeader

def listMedian(L):
	isEven = lambda n: (n%2 == 0)
	length = len(L)
	if isEven(length):
		i = int(round(length / 2) - 1)
		j = int(i + 1)
		return ( L[i] + L[j] ) / 2.0
	else:
		i = int(length / 2)
		return L[i]

if __name__ == '__main__':
	""" utils for pad processing """
	from stat import ST_SIZE

	# Get list of pad header files that cover span of interest
	dateStart = sys.argv[1]
	dateStop  = sys.argv[2]
	sensor	  = sys.argv[3]
	padPath = getoutput('echo ${PADPATH}')
	padFiles,sampleRate,dataColumns = getPadHeaderFiles(padPath,dateStart,dateStop,sensor)
	if not(padFiles):
		print 'no pad files'
		raise SystemExit
	print 'There are %d PAD files.' % len(padFiles)
	pts,dur = [],[]
	for i in range(0,len(padFiles)-1):
		f1 = split(padFiles[i],'.header')[0]
		f2 = split(padFiles[i+1],'.header')[0]
		fileBytes = os.stat(f1)[ST_SIZE]
		fileRecs = fileBytes / (dataColumns * 4.0)
		p = Pad(f1,offsetRecs=fileRecs-5,numRecs=5)
		q = Pad(f2,offsetRecs=0,numRecs=5)
		try:
			ptsGap = len(q-p)
			pts.append(ptsGap)
			dur.append(float(ptsGap)/p.header.SampleRate)
			print '%4d,%7.3f' % (ptsGap,float(ptsGap)/p.header.SampleRate)
		except:
			print f1
			print f2
			print '%.3f sec.\n' % (p.dateStop-q.dateStart)
##			  print p
##			  print q
##			  raise SystemExit
##		  s = p + q
##		  print s
	pts.sort()
	dur.sort()
	print 'Median number of points: %.3f' % listMedian(pts)
	print 'Median duration in secs: %.3f' % listMedian(dur)
	raise SystemExit

##	  from matplotlib.matlab import *
##	  q = Pad(sys.argv[1],offsetRecs=0,numRecs=3)
##	  print unixTimeToString(q.dateStart)
##	  print unixTimeToString(q.dateStop)
##	  print q.data
##	  q = Pad(sys.argv[1])
##	  print unixTimeToString(q.dateStart)
##	  print unixTimeToString(q.dateStop)
##	  print q.data

##	  plot(q.data[:,1],q.data[:,2])
##	  from matplotlib import mlab
##	  padFile=sys.argv[1]
##	  d = readPadFile(padFile,numRecs=512,offsetRecs=3)
##	  print d
##	  pxx,f = mlab.psd(d[:,1])
##	  print pxx[:11], f[:11]
##	  sys.exit()
