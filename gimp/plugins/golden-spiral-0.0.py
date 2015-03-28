#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# GIMP script to render an approcimate "golden spiral" path
# (c) Ofnuts 2011
#
#   History:
#
#   v0.0: 2012-01-25 :  first published version
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

import math, random, os, sys, time
from gimpfu import *

# Two useful math constants
KAPPA=(4./3.)*(math.sqrt(2)-1)
PHI=(math.sqrt(5)+1)/2

PATH_NAME='Golden Spiral'

# A bunch of static constants for the generation of the spirals.
# Obviously there is some logic in there, but I didn't dig the
# subject enough to come up with code that would be as readable
# and compact as the data tables.

# Name of areas for spiral center
SPIRALCENTER_FLAGS=['NE','SE','SW','NW']
SPIRALCENTER=SPIRALCENTER_FLAGS


# Sign of successive X,Y changes when going from one point to the next
#
#       CCW           CW
#        1            3
#      <----        ---->
#     |     A      A     |
#   2 |     | 0  2 |     | 0
#     V     |      |     V
#      ---->        <----
#        3            1
ROTATE_STEPS_CW=  [( 0,+1),(-1, 0),( 0,-1),(+1, 0)]
ROTATE_STEPS_CCW =[( 0,-1),(-1, 0),( 0,+1),(+1, 0)]

ROTATE_STEPS={'CW':ROTATE_STEPS_CW,'CCW':ROTATE_STEPS_CCW}

# Initial point, depending on spiral center position, and aspect ratio of rectangle
# Yes, the initial points for H and V are in opposite corners.
INITPOINTS_H={'NE':('MIN','MIN'),'SE':('MIN','MAX'),'SW':('MAX','MAX'),'NW':('MAX','MIN')}
INITPOINTS_V={'NE':('MAX','MAX'),'SE':('MAX','MIN'),'SW':('MIN','MIN'),'NW':('MIN','MAX')}
INITPOINTS={'H':INITPOINTS_H,'V':INITPOINTS_V}

# Rotation direction, depending on spiral center position, and aspect ratio of rectangle
# Yes, the directions for H and V opposite.
ROTATION_H={'NE':'CCW','SE':'CW','SW':'CCW','NW':'CW'}
ROTATION_V={'NE':'CW','SE':'CCW','SW':'CW','NW':'CCW'}
ROTATION={'H':ROTATION_H,'V':ROTATION_V}

# Initial rotation step, depending on spiral center position, and aspect ratio of rectangle
INITIALSTEP_H={'NE':2,'SE':2,'SW':0,'NW':0}
INITIALSTEP_V={'NE':1,'SE':1,'SW':3,'NW':3}
INITIALSTEP={'H':INITIALSTEP_H,'V':INITIALSTEP_V}

def initialPoint(bounds,aspect,spiralCenter):
	xmin,ymin,xmax,ymax=bounds
	pointX,pointY=INITPOINTS[aspect][spiralCenter]
	
	if pointX == 'MIN':
		x=xmin
	else:
		x=xmax
	
	if pointY == 'MIN':
		y=ymin
	else:
		y=ymax
	
	return (x,y)


def rectangleData(bounds):
	xmin,ymin,xmax,ymax=bounds
	width=xmax-xmin
	height=ymax-ymin
	if width < height:
		return (width,'V')
	else:
		return (height,'H')

def getSelectionBounds(image):
	selection=pdb.gimp_selection_bounds(image)
	selected,=selection[0:1]
	if selected:
		bounds=selection[1:5]
	else:
		bounds=(0,0,image.width,image.height)
	return bounds

# Compute our initial conditions, returns:
# - start point
# - size of initial quadrantPoints
# - rotation direction
# - rotation step

def initialConditions(image,spiralCenter):
	bounds=getSelectionBounds(image)
	print 'Bounds: %s' % (bounds,)
	size,aspect=rectangleData(bounds)
	print 'Size: %d, aspect: %s' % (size,aspect)
	startPoint=initialPoint(bounds,aspect,spiralCenter)
	print 'Start point: %s' % (startPoint,)
	rotationDirection=ROTATION[aspect][spiralCenter]
	rotationStep=INITIALSTEP[aspect][spiralCenter]
	print 'Rotation: %s, %d' % (rotationDirection,rotationStep)
	return bounds,size,aspect,startPoint,rotationDirection,rotationStep

def rotateStep(direction,step):
	return ROTATE_STEPS[direction][step%4]
	
# Generate quarter-circle arc within a quadrantPoint
# defined by three points
def arcPoints(start,corner,end):
	xs,ys=start
	xc,yc=corner
	xe,ye=end
	
	# forward handle of start point
	xhs=xs+(xc-xs)*KAPPA
	yhs=ys+(yc-ys)*KAPPA
	
	# backward handle of end point
	xhe=xe+(xc-xe)*KAPPA
	yhe=ye+(yc-ye)*KAPPA
	
	return [xs,ys,xs,ys,xhs,yhs,xhe,yhe,xe,ye,xe,ye]

# Generate the three quadrant points given
# Initial point
# Size of side
# Rotation direction, and rotation step
def quadrantPoints(point,size,direction,step):
	xs,ys=point
	
	dx,dy=rotateStep(direction,step)
	xc=xs+size*dx
	yc=ys+size*dy
	
	dx,dy=rotateStep(direction,step+1)
	xe=xc+size*dx
	ye=yc+size*dy
	
	return ((xs,ys),(xc,yc),(xe,ye))
	
def addSpiralStrokes(path,size,start,direction,step):
	while size >= 2:
		ps,pc,pe=quadrantPoints(start,size,direction,step)
		points=arcPoints(ps,pc,pe)
		pdb.gimp_vectors_stroke_new_from_points(path,0, len(points), points, False)
		start=pe
		step=step+1
		size=size/PHI

def addFrameStroke(path,size,start,direction,step):
	points=[]
	x,y=start
	points.extend([x,y]*3)
	dx,dy=rotateStep(direction,step)
	x=x+size*dx
	y=y+size*dy
	points.extend([x,y]*3)
	dx,dy=rotateStep(direction,step+1)
	x=x+size*PHI*dx
	y=y+size*PHI*dy
	points.extend([x,y]*3)
	dx,dy=rotateStep(direction,step+2)
	x=x+size*dx
	y=y+size*dy
	points.extend([x,y]*3)
	
	pdb.gimp_vectors_stroke_new_from_points(path,0, len(points), points, True)

def goldenSpiral(image,spiralCenter,frame):
	spiralCenter=SPIRALCENTER_FLAGS[spiralCenter]
	bounds,size,aspect,startPoint,rotationDirection,rotationStep=initialConditions(image,spiralCenter)	

	# drop existing PATH_NAME path
	for path in image.vectors:
		if path.name==PATH_NAME:
			pdb.gimp_image_remove_vectors(image,path)
			break

	path=pdb.gimp_vectors_new(image,PATH_NAME)
	path.visible=True
	pdb.gimp_image_add_vectors(image, path, 0)
	
	addSpiralStrokes(path,size,startPoint,rotationDirection,rotationStep)
	if frame:
		addFrameStroke(path,size,startPoint,rotationDirection,rotationStep)
	

def goldenSpiralLayer(image,layer,spiralCenter,frame):
	goldenSpiral(image,orientation,frame)

def goldenSpiralPath(image,path,spiralCenter,frame):
	goldenSpiral(image,spiralCenter,frame)

# -----------------------------------------------------------------------------
# Registrations
# -----------------------------------------------------------------------------
AUTHOR='Ofnuts'
YEAR='2012'

whoiam='\n'+os.path.abspath(sys.argv[0])

REGISTRATION_IMAGE=(PF_IMAGE, 'image', 'Input image', None)
REGISTRATION_LAYER=(PF_VECTORS, 'layer', 'Input layer', None)
REGISTRATION_PATH=(PF_VECTORS, 'refpath', 'Input path', None)
REGISTRATION_SPIRALCENTER=(PF_OPTION, 'spiralCenter', 'Spiral Center:', 0, SPIRALCENTER)
REGISTRATION_FRAME=(PF_TOGGLE, 'frame', 'Frame:', 1)

REGISTRATION_NAME_MENU='Golden spiral on selection...'
REGISTRATION_NAME_MENU_POPUP='Golden spiral on selection'+whoiam
REGISTRATION_NAME_DIALOG_TITLE='Golden spiral on selection'

register(
	'golden-spiral',
	REGISTRATION_NAME_MENU_POPUP,
	REGISTRATION_NAME_DIALOG_TITLE,
	AUTHOR,
	AUTHOR,
	YEAR,
	REGISTRATION_NAME_MENU,
	'RGB*,GRAY*',
	[
		REGISTRATION_IMAGE,
		REGISTRATION_SPIRALCENTER,
		REGISTRATION_FRAME,
	],
	[],
	goldenSpiral,
	menu='<Image>/Select',
)

#register(
	#'golden-spiral-path',
	#REGISTRATION_NAME_MENU_POPUP,
	#REGISTRATION_NAME_DIALOG_TITLE,
	#AUTHOR,
	#AUTHOR,
	#YEAR,
	#REGISTRATION_NAME_MENU,
	#'RGB*,GRAY*',
	#[
		#REGISTRATION_IMAGE,
		#REGISTRATION_PATH,
		#REGISTRATION_SPIRALCENTER,
		#REGISTRATION_FRAME,
	#],
	#[],
	#goldenSpiralPath,
	#menu='<Vectors>',
#)

main()
print whoiam+': registration OK'