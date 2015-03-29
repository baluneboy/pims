#!/usr/bin/env python
version = '$Id'
# author: Kenneth Hrovat

import sys
import os
from xml.dom.minidom import *
from string import *
from commands import *

def get_sub_field(h, field, Lsubs):
	""" get sub fields using xml parser """
	d = {}	
	for k in Lsubs:
		theElement = h.documentElement.getElementsByTagName(field)[0]
		d[k] = str(theElement.getAttribute(k))
	return d

def parse_header(hdr_file):
	""" use xml parsing to build header """
	dHeader = { 'header_file': hdr_file }
	
	h = parse(dHeader['header_file'])
	
	L = ['SampleRate','CutoffFreq','DataQualityMeasure','SensorID','TimeZero','ISSConfiguration']
	for i in L:
		dHeader[i] = str(h.documentElement.getElementsByTagName(i)[0].childNodes[0].nodeValue)
		
	dHeader['DataType'] = str(h.documentElement.nodeName)
	#dHeader['BiasCoeff'] = get_sub_field(h,'BiasCoeff',['x','y','z']) # FIXME Hrovat commented this out bc headers (like 121f08) sometimes leave this out!?

	if not dHeader['SensorID'] in ['ossbtmf','radgse','ossraw']:
		dHeader['Gain'] = str(h.documentElement.getElementsByTagName('Gain')[0].childNodes[0].nodeValue)
		#dHeader['ScaleFactor'] = get_sub_field(h,'ScaleFactor',['x','y','z']) # FIXME Hrovat commented this out bc headers (like 121f08) sometimes leave this out!?
	
	Lcoord = ['x','y','z','r','p','w','name','time','comment']
	dHeader['SensorCoordinateSystem'] = get_sub_field(h,'SensorCoordinateSystem',Lcoord)
	dHeader['DataCoordinateSystem'] = get_sub_field(h,'DataCoordinateSystem',Lcoord)
	dHeader['GData'] = get_sub_field(h,'GData',['format','file'])
	
	if dHeader['SensorID'] == 'ossraw':
		dHeader['ElementsPerRec'] = 6
	elif dHeader['SensorID'] == 'radgse':
		dHeader['ElementsPerRec'] = 14
	else:
		dHeader['ElementsPerRec'] = 4
	
	return dHeader
