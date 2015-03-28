#! /usr/bin/python
# -*- coding: utf-8 -*-

# GIMP plugin to import paths from CSV files
# (c) Ofnuts 2011
#
#   History:
#
#   v0.0: 2011-11-12 first published version
#   v0.1: 2012-04-11 remove some trace statements that can create problems under Windows
#                    handle file I/O in a more pythonic way
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


# Warning: this script completely ignores number formatting issues (decimal and thousands separator).
# It has only be tested with CSV files from OpenOffice.

# CSV file format
# ---------------
# Lines should contains eight items:
#
# 1) a Path name
# 2) a Stroke label (a stroke is a sequence of connected points)
# 3) 6 coordinates for a control "triplet":
#  	- X and Y coordinate of the "backward" handle
#  	- X and Y coordinate of the anchor point 
#  	- X and Y coordinate of the "forward" handle
#
# A new path is started whenever a new name appears in column 1
#
# A new stroke is started whenever a new name appears in column 2
#
# It is an error to reuse a path name
#
# It is an error to reuse a stroke label within the same pathName
#
# A closed stroke is implied if the first row of the stroke is stricly identical 
# to the last. In this case the last row isn't used to create a point in the 
# Gimp stroke and the Gimp stroke is marked closed instead. Conversely, for export, 
# closed strokes are designated by ending them with a copy of their first triplet.

import csv,os,sys

from gimpfu import *

debug=False
def trace(s):
	if debug:
		print s
	
# Stroke is considered closed if the last anchor/handles triplet is identical to the firzt
def isClosed(stroke):
	return stroke[:6] == stroke[-6:] 
	
# If stroke is assumed closed drop last triplet
def strokePoints(stroke):
	if isClosed(stroke):
		return stroke[:-6]
	return stroke
	
def dumpPaths(paths):
	for p,path in paths.iteritems():
		trace( 'Path "%s":' % p)
		for s,stroke in path.iteritems():
			trace( 'Stroke "%s": closed: %s: %s' % (s,isClosed(stroke), strokePoints(stroke)))
			
def csv2paths(csvFile,paths):
	trace( 'Reading paths from %s' % csvFile)
	with open(csvFile, 'rb') as f:
		reader=csv.reader(f)
		currentPath={}
		currentPathName=''
		currentStroke=[]
		currentStrokeName=''
		for row in reader:
			# Test for valid row,ignore others  (header, etc..)
			if len(row) < 8:
				trace( 'Row ignored (not enough columns): %s' % row)
				continue
			if row[0]=='' or row[1]=='':
				trace( 'Row ignored (empty path/stroke): %s' % row)
				continue
			try:
				for item in row[2:8]:
					float(item)
			except ValueError:
				trace( 'Row ignored (invalid numeric values): %s' % row)
				continue 
			#Valid row
			pathName=row[0]
			# Create new path if path name changed
			if pathName != currentPathName:
				if pathName in paths:
					raise Exception(1,'Duplicate path %s: aborting' % pathName)
					return
				trace( 'Creating path: "%s"' % pathName)
				currentPathName=pathName
				currentPath={}
				paths[currentPathName]=currentPath
				currentStroke=[]
				currentStrokeName=''
			strokeName=row[1]
			# Create new stroke if stroke name changed
			if strokeName != currentStrokeName:
				if strokeName in currentPath:
					raise Exception(2,'Duplicate stroke "%s" in path "%s": aborting' % (strokeName, currentPathName))
					return
				trace( 'Creating stroke "%s" in path "%s"' % (strokeName,currentPathName))
				currentStrokeName=strokeName
				currentStroke=[]
				currentPath[currentStrokeName]=currentStroke
			currentStroke.extend([float(i) for i in row[2:8]])
		
def createPaths(image,paths):
	for pathName,strokes in paths.iteritems():
		path=pdb.gimp_vectors_new(image, pathName)
		pdb.gimp_image_add_vectors(image, path, 0)

		for strokeName,stroke in strokes.iteritems():
			closed=isClosed(stroke)
			points=strokePoints(stroke)
			sid = pdb.gimp_vectors_stroke_new_from_points(path,0, len(points),points,closed)
		path.visible=True
		trace( 'Path "%s"created OK' % pathName)
		

def importCSV(image,refpath,csvFile):
	# Dictionary of existing paths
	# A path is a dictionary of strokes
	# Strokes are just arrays of floats (multiple of 6)
	# If the last 6 elements are equal to the first 6, the stroke
	# is assumed closed and the last 6 elements aren't copied
	paths={}

	try:
		#trace( (image,refpath,csvFile))
		csv2paths(csvFile,paths)
		#dumpPaths(paths)
		createPaths(image,paths)
        except Exception as e:
		trace( '%s: %s' % (type(e), e.args))
		pdb.gimp_message('%s' % (e.args,))

	pdb.gimp_displays_flush()
	return;

def exportCSV(image,path,csvFile):
	strokesCount=0
	if path==None:
		trace( 'No active path in image')
		return 
	if not path :
		trace( 'No elements in active path')
		return
		
	trace( 'Dumping path %s' % path.name)

	data=[]
		
	try:
		for stroke in path.strokes:
			strokesCount=strokesCount+1
			(strokePoints,closed)=stroke.points
			data.append([None,None,None,None,None,None,None,None])
			# copy triplets
			for triplet in range(0,len(strokePoints),6):
				row=[path.name,strokesCount]
				row.extend(strokePoints[triplet:triplet+6])
				data.append(row)
				trace( row)
			# for closed stroke, close with first triplet
			if closed:
				row=[path.name,strokesCount]
				row.extend(strokePoints[:6])
				data.append(row)
				trace( ' %s (closure)' % row )
		trace( data)
		with open(csvFile, 'wb') as f:
			writer=csv.writer(f)
			for row in data:
				writer.writerow(row)
        except Exception as e:
		trace( '%s: %s' % (type(e), e.args))
		pdb.gimp_message('%s' % (e.args,))

	pdb.gimp_displays_flush()

	# file closed by exiting



### Registration
whoiam='\n'+os.path.abspath(sys.argv[0])

register(
        "path-csv-import",
        N_("Import path from CSV"+whoiam),
        "Import path from CSV",
        "Ofnuts",
        "Ofnuts",
        "2011",
        N_("Import CSV"),
        "RGB*,GRAY*",
        [
                (PF_IMAGE, "image", "Input image", None),
                (PF_VECTORS, "refpath", "Input path", None),
                (PF_FILE, "csvFile", "File", 0),
        ],
        [],
        importCSV,
        menu="<Vectors>/Tools/CSV",
        domain=("gimp20-python", gimp.locale_directory)
        )

register(
        "path-csv-export",
        N_("Export path to CSV"+whoiam),
        "Export path to CSV",
        "Ofnuts",
        "Ofnuts",
        "2011",
        N_("Export CSV"),
        "RGB*,GRAY*",
        [
                (PF_IMAGE, "image", "Input image", None),
                (PF_VECTORS, "refpath", "Input path", None),
                (PF_FILENAME, "csvFile", "File", 0),
        ],
        [],
        exportCSV,
        menu="<Vectors>/Tools/CSV",
        domain=("gimp20-python", gimp.locale_directory)
        )
        
main()        
