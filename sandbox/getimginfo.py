#!/usr/bin/python
version = '$Id'

import os
import sys
import struct

with open(strFile,'rb') as f:
	# first word
	f.seek(28)
	TR = struct.unpack('I',f.read(4))[0] / 1e6

	# Number of vols
	f.seek(147700)
	Nimgs=struct.unpack('f',f.read(4))[0]

	# Disdaqs
	f.seek(147716)
	disdaq=struct.unpack('f',f.read(4))[0]

	# Number of slices
	f.seek(68)
	Nslices = struct.unpack('H',f.read(2))[0]

	# Series description
	f.seek(145762)
	seriesDesc = struct.unpack('65s',f.read(65))[0]

	# Date
	f.seek(16)
	tmp=struct.unpack('10s',f.read(10))[0]
	tmp2=tmp[0:10]
	strDate = tmp2[:6] + tmp2[7:]

	# Time
	f.seek(26)
	strTime = struct.unpack('8s',f.read(8))[0]

	# Exam number
	f.seek(143516)
	examNum = struct.unpack('H',f.read(2))[0]

	# Slice order
	f.seek(145873)
	slOne = struct.unpack('s',f.read(1))[0]
	if slOne == "I":
		sliceOrder = "Inferior --> Superior"
		strOrder = "bu"
	elif slOne == "S":
		sliceOrder = "Superior --> Inferior"
		strOrder = "td"

print "\nSeries information read from %s:\n" % strFile
print "Exam number:  %d" % examNum
print "Date:  %s" % strDate
print "Time:  %s" % strTime
print "Series description:  %s" % seriesDesc
print "Number of images: %d" % Nimgs
print "Number of slices: %d" % Nslices
print "Slice order: %s" % sliceOrder
print "TR (sec): %d" % TR
print "disdaqs: %d" % disdaq
print ""
