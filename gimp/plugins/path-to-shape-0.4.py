#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# GIMP plugin to generate shapes uing reference points in paths
# (c) Ofnuts 2014
#
#   History:
#
#   v0.0: 2014-02-12 First published version
#   v0.1: 2014-02-15 Add circumcircle, star, double star, rectangle
#                    Harden the code
#   v0.2: 2014-02-18 Add tangents
#   v0.3: 2014-02-22 Add multiply/divide segments
#   v0.4: 2014-02-24 Add Star/Spokes
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

from gimpfu import *
import os,sys,math,time


# The famous constant for the computation of control points that create
# a spline that most closely matches a quarter of a circle.
kappa=4*(math.sqrt(2)-1)/3

def middle(p1,p2):
	x1,y1=p1
	x2,y2=p2
	return ((x1+x2)/2,(y1+y2)/2)

def angle(p1,p2):
	x1,y1=p1
	x2,y2=p2
	return math.atan2(y2-y1,x2-x1)
	
def distance(p1,p2):
	x1,y1=p1
	x2,y2=p2
	dx=x2-x1
	dy=y2-y1
	return math.sqrt(dx*dx+dy*dy)

def bisector(p1,p2):
	'''
	Computes the equation of the bisector of a segment, 
	Returns coefficients for equation ax+by=c, suitable for Cramer equation
	'''
	x1,y1=p1
	x2,y2=p2
	xm,ym=middle(p1,p2)
	if x1==x2: # segment is vertical: bisector is horizontal
		return (0,1,ym)
	elif y1==y2: # segment is horizontal: bisector is vertical
		return (1,0,xm)
	else: # general case, y=ax+b or ax-y=-b
		a=(x2-x1)/(y1-y2)
		b=ym-a*xm
		return (a,-1,-b)
		
def intersection(l1,l2):
	'''
	Computes the intersection of two lines by Cramer's rule
	'''
	a,b,e=l1
	c,d,f=l2
	det=a*d-b*c
	if abs(det)<.0001:
		print 'Determinant: %3.5f, a/c=%3.5f, b/d=%3.5f' % (det,a/c,b/d)
		raise Exception('No intersection found')
	else:
		x=(e*d-b*f)/det
		y=(a*f-e*c)/det
		return (x,y)
	
def circleCenterFromPoints(points):
	'''
	Determines the center of a circle going through 3 points. 
	This can be used for the circucmcirlce of three random points but will work just as well
	on a circle stroke (taking the first three points, that are accurately on the real circle),
	or on the vertices of a regular polygon (all vertices are on the same circle, so we can pick any three)
	'''
	
	if len(points)<3:
		raise Exception('Stroke starting at (%3.1f,%3.1f) should have at least 3 points' % (points[0][0],points[0][1]))
	bisector1=bisector(points[0],points[1])
	bisector2=bisector(points[1],points[2])
	try:
		center=intersection(bisector1,bisector2)
	except Exception as e:
		raise Exception('Stroke starting at (%3.1f,%3.1f) contains colinear or near-colinear segments' % (points[0][0],points[0][1]))
	return center

def flattenToStroke(points):
	'''
	Takes a list of points as tuples and flattens it to a list of coordinates 
	suitable for a stroke made of line segments (no handles)
	'''
	return [coord for point in points for coord in point]
	
def pointsFromStroke(stroke):
	'''
	Takes a list of stroke coordinates and extracts the anchors as (x,y) tuples
	'''
	p,c=stroke.points
	return [tuple(p[i:i+2]) for i in range(2,len(p),6)]

def pointAtRhoThetaFromOrigin(origin,rho,theta):
	xo,yo=origin
	x=xo+rho*math.cos(theta)
	y=yo+rho*math.sin(theta)
	return (x,y)

def tripletAtRhoThetaFromOrigin(origin,rho,theta):
	p=pointAtRhoThetaFromOrigin(origin,rho,theta)
	return [p,p,p]

def tripletAtXYFromOrigin(origin,dx,dy):
	x0,y0=origin
	p=(x0+dx,y0+dy)
	return [p,p,p]

def circleTriplet(center,rho,theta):
	anchor=pointAtRhoThetaFromOrigin(center,rho,theta)
	bwdHandle=pointAtRhoThetaFromOrigin(anchor,rho*kappa,theta-math.pi/2)
	fwdHandle=pointAtRhoThetaFromOrigin(anchor,rho*kappa,theta+math.pi/2)
	return [bwdHandle,anchor,fwdHandle]

def circleStroke(center,radius):
	rho=distance(center,radius)
	theta=angle(center,radius)
	points=[]
	for i in range(4):
		triplet=circleTriplet(center,rho,theta+(i*math.pi/2))
		points.extend(triplet)
	return [coord for point in points for coord in point]

def segmentStroke(p1,p2):
	return [coord for point in [p1]*3+[p2]*3 for coord in point]

def circleFromRadius_core(image,path):
	circles=gimp.Vectors(image,'Circles from radius using <%s>' % (path.name))
	for stroke in path.strokes:
		points=pointsFromStroke(stroke)
		if len(points)<2:
			raise Exception('Stroke starting at (%3.1f,%3.1f) should have at least 2 points' % (points[0][0],points[0][1]))
		for point in points[1:]:
			circlePoints=circleStroke(points[0],point)
			gimp.VectorsBezierStroke(circles,circlePoints,True)
        pdb.gimp_image_add_vectors(image, circles, 0)
        circles.visible=True

def circleFromDiameter_core(image,path):
	circles=gimp.Vectors(image,'Circles from diameter using <%s>' % (path.name))
	for stroke in path.strokes:
		points=pointsFromStroke(stroke)
		if len(points)<2:
			raise Exception('Stroke starting at (%3.1f,%3.1f) should have at least 2 points' % (points[0][0],points[0][1]))

		for point in points[1:]:
			circlePoints=circleStroke(middle(points[0],point),point)
			gimp.VectorsBezierStroke(circles,circlePoints,True)
        pdb.gimp_image_add_vectors(image, circles, 0)	
        circles.visible=True
        
def circumcircle_core(image,path):
	circles=gimp.Vectors(image,'Circumcircle using <%s>' % (path.name))
	for stroke in path.strokes:
		points=pointsFromStroke(stroke)
		center=circleCenterFromPoints(points)
		circlePoints=circleStroke(center,points[0])
		gimp.VectorsBezierStroke(circles,circlePoints,True)
        pdb.gimp_image_add_vectors(image, circles, 0)	
        circles.visible=True
        
def star_core(image,path):
	star=gimp.Vectors(image,'Star using <%s>' % (path.name))
	for stroke in path.strokes:
		points=pointsFromStroke(stroke)
		if len(points)<4:
			raise Exception('Stroke starting at (%3.1f,%3.1f) should have at least 4 points' % (points[0][0],points[0][1]))
		center=points[0]
		rho1=distance(center,points[1])
		rho2=distance(center,points[2])
		theta=angle(center,points[1])
		count=len(points)-2
		alpha=(2*math.pi)/count
		starPoints=[]
		for i in range(count):
			starPoints.extend(tripletAtRhoThetaFromOrigin(center,rho1,theta+i*alpha))
			starPoints.extend(tripletAtRhoThetaFromOrigin(center,rho2,theta+i*alpha+alpha/2))
		gimp.VectorsBezierStroke(star,flattenToStroke(starPoints),True)
        pdb.gimp_image_add_vectors(image, star, 0)	
        star.visible=True

def doubleStar_core(image,path):
	star=gimp.Vectors(image,'Double star using <%s>' % (path.name))
	for stroke in path.strokes:
		points=pointsFromStroke(stroke)
		if len(points)<5:
			raise Exception('Stroke starting at (%3.1f,%3.1f) should have at least 5 points' % (points[0][0],points[0][1]))
		center=points[0]
		rho1=distance(center,points[1])
		rho2=distance(center,points[2])
		rho3=distance(center,points[3])
		theta=angle(center,points[1])
		count=len(points)-3
		alpha=(2*math.pi)/count
		starPoints=[]
		for i in range(count):
			starPoints.extend(tripletAtRhoThetaFromOrigin(center,rho1,theta+i*alpha))
			starPoints.extend(tripletAtRhoThetaFromOrigin(center,rho2,theta+i*alpha+alpha/4))
			starPoints.extend(tripletAtRhoThetaFromOrigin(center,rho3,theta+i*alpha+alpha/2))
			starPoints.extend(tripletAtRhoThetaFromOrigin(center,rho2,theta+i*alpha+alpha*3/4))
		gimp.VectorsBezierStroke(star,flattenToStroke(starPoints),True)
        pdb.gimp_image_add_vectors(image, star, 0)	
        star.visible=True

def spokes_core(image,path):
	spokes=gimp.Vectors(image,'Spokes using <%s>' % (path.name))
	for stroke in path.strokes:
		points=pointsFromStroke(stroke)
		if len(points)<3:
			raise Exception('Stroke starting at (%3.1f,%3.1f) should have at least 3 points' % (points[0][0],points[0][1]))
		rho=distance(points[0],points[1])
		theta=angle(points[0],points[1])
		count=len(points)-1
		alpha=(2*math.pi)/count
		for i in range(count):
			spokePoints=([points[0]]*3)+tripletAtRhoThetaFromOrigin(points[0],rho,theta+i*alpha)
			gimp.VectorsBezierStroke(spokes,flattenToStroke(spokePoints),False)
        pdb.gimp_image_add_vectors(image, spokes, 0)	
        spokes.visible=True

def polygonFromCenterCircumradiusAngle(center,rho,theta,count):
	points=[]
	alpha=(2*math.pi)/count
	for i in range(count):
		points.extend(tripletAtRhoThetaFromOrigin(center,rho,theta+i*alpha))
	return flattenToStroke(points)

def polygonFromCircumradius_core(image,path):
	polygon=gimp.Vectors(image,'Polygon from circumradius using <%s>' % (path.name))
	for stroke in path.strokes:
		points=pointsFromStroke(stroke)
		if len(points)<4:
			raise Exception('Stroke starting at (%3.1f,%3.1f) should have at least 4 points' % (points[0][0],points[0][1]))
		rho=distance(points[0],points[1])
		theta=angle(points[0],points[1])
		count=len(points)-1
		polygonPoints=polygonFromCenterCircumradiusAngle(points[0],rho,theta,count)
		gimp.VectorsBezierStroke(polygon,polygonPoints,True)
        pdb.gimp_image_add_vectors(image, polygon, 0)	
        polygon.visible=True

def polygonFromApothem_core(image,path):
	polygon=gimp.Vectors(image,'Polygon from apothem using <%s>' % (path.name))
	for stroke in path.strokes:
		points=pointsFromStroke(stroke)
		if len(points)<4:
			raise Exception('Stroke starting at (%3.1f,%3.1f) should have at least 4 points' % (points[0][0],points[0][1]))
		apothemRho=distance(points[0],points[1])
		apothemTheta=angle(points[0],points[1])
		count=len(points)-1
		alpha=math.pi/count # half-angle
		polygonPoints=polygonFromCenterCircumradiusAngle(points[0],apothemRho/math.cos(alpha),apothemTheta+alpha,count)
		gimp.VectorsBezierStroke(polygon,polygonPoints,True)
        pdb.gimp_image_add_vectors(image, polygon, 0)	
        polygon.visible=True

def polygonFromSide_core(image,path):
	polygon=gimp.Vectors(image,'Polygon from side using <%s>' % (path.name))
	for stroke in path.strokes:
		points=pointsFromStroke(stroke)
		count=len(points)
		sideLength=distance(points[0],points[1])
		sideAngle=angle(points[0],points[1])
		apothemFoot=middle(points[0],points[1])
		alpha=math.pi/count # half-angle
		apothemLength=sideLength/(2*math.tan(alpha))
		center1=pointAtRhoThetaFromOrigin(apothemFoot,apothemLength,sideAngle+math.pi/2)
		center2=pointAtRhoThetaFromOrigin(apothemFoot,apothemLength,sideAngle-math.pi/2)
		# Find which center is closest to third point in stroke
		d1=distance(center1,points[2])
		d2=distance(center2,points[2])
		if d1 < d2:
			polygonPoints=polygonFromCenterCircumradiusAngle(center1,sideLength/(2*math.sin(alpha)),sideAngle+alpha-math.pi/2,count)
		else:
			polygonPoints=polygonFromCenterCircumradiusAngle(center2,sideLength/(2*math.sin(alpha)),sideAngle+alpha+math.pi/2,count)
		gimp.VectorsBezierStroke(polygon,polygonPoints,True)
        pdb.gimp_image_add_vectors(image, polygon, 0)	
        polygon.visible=True

def rectangleUpright_core(image,path):
	rectangle=gimp.Vectors(image,'Rectangle using <%s>' % (path.name))
	for stroke in path.strokes:
		points=pointsFromStroke(stroke)
		if len(points)<2:
			raise Exception('Stroke starting at (%3.1f,%3.1f) should have at least 2 points' % (points[0][0],points[0][1]))
		x1,y1=points[0]
		x2,y2=points[1]
		xMin=min(x1,x2)
		xMax=max(x1,x2)
		yMin=min(y1,y2)
		yMax=max(y1,y2)
		
		tl=(xMin,yMin)
		tr=(xMax,yMin)
		br=(xMax,yMax)
		bl=(xMin,yMax)
		
		rectanglePoints=[]
		if len(points)==2:
			rectanglePoints=[tl,tl,tl,tr,tr,tr,br,br,br,bl,bl,bl]
			
		elif len(points)==3: # with rounded corners
 			r=distance(points[1],points[2]) # radius of corner
			h=r*(1-kappa) # handle distance from corner

			# Top side (left to right) 
			rectanglePoints.append((xMin+h,yMin))
			rectanglePoints.append((xMin+r,yMin))
			rectanglePoints.append((xMin+r,yMin))
			rectanglePoints.append((xMax-r,yMin))
			rectanglePoints.append((xMax-r,yMin))
			rectanglePoints.append((xMax-h,yMin))
			
			# Right side (top to bottom)
			rectanglePoints.append((xMax,yMin+h))
			rectanglePoints.append((xMax,yMin+r))
			rectanglePoints.append((xMax,yMin+r))
			rectanglePoints.append((xMax,yMax-r))
			rectanglePoints.append((xMax,yMax-r))
			rectanglePoints.append((xMax,yMax-h))

			# Bottom side (right to left)
			rectanglePoints.append((xMax-h,yMax))
			rectanglePoints.append((xMax-r,yMax))
			rectanglePoints.append((xMax-r,yMax))
			rectanglePoints.append((xMin+r,yMax))
			rectanglePoints.append((xMin+r,yMax))
			rectanglePoints.append((xMin+h,yMax))
			
			# Left side (bottom to top)
			rectanglePoints.append((xMin,yMax-h))
			rectanglePoints.append((xMin,yMax-r))
			rectanglePoints.append((xMin,yMax-r))
			rectanglePoints.append((xMin,yMin+r))
			rectanglePoints.append((xMin,yMin+r))
			rectanglePoints.append((xMin,yMin+h))
		else:
			pass
			
		gimp.VectorsBezierStroke(rectangle,flattenToStroke(rectanglePoints),True)
		
        pdb.gimp_image_add_vectors(image, rectangle, 0)	
        rectangle.visible=True
        
def circleCenterRadius(stroke):
	points=pointsFromStroke(stroke)
	if len(points)==2:
		return points[0],distance(points[0],points[1])
	elif len(points)>=3:
		center=circleCenterFromPoints(points)
		return center,distance(center,points[0])
	else:
		raise Exception('Stroke starting at (%3.1f,%3.1f) should have at least 2 points' % (points[0][0],points[0][1]))
	
def tangentSegments(center,radius,point,tangentSets):
	dist=distance(center,point)
	if dist < radius:
		raise Exception('Point at (%3.1f,%3.1f) is inside circle centered at (%3.1f,%3.1f) with radius %3.1f' % (point[0],point[1],center[0],center[1],radius))
	axisAngle=angle(center,point)
	radiusAngle=math.acos(radius/dist)
	tp=pointAtRhoThetaFromOrigin(center,radius,axisAngle+radiusAngle)
	gimp.VectorsBezierStroke(tangentSets[0],segmentStroke(tp,point),False)
	tp=pointAtRhoThetaFromOrigin(center,radius,axisAngle-radiusAngle)
	gimp.VectorsBezierStroke(tangentSets[1],segmentStroke(tp,point),False)
	
def tangentSegmentsForStroke(center,radius,stroke,tangentSets):			
	points=pointsFromStroke(stroke)
	for point in points:
		segments=tangentSegments(center,radius,point,tangentSets)
	
def tangentCircleFromPoint_core(image,path):
	tangentSetL=gimp.Vectors(image,'Tangents (L) using <%s>' % (path.name))
	tangentSetR=gimp.Vectors(image,'Tangents (R) using <%s>' % (path.name))
	tangentSets=[tangentSetL,tangentSetR]
	strokes=path.strokes
	center,radius=circleCenterRadius(strokes[0])
	sourcePaths=filter(lambda v: v.linked,image.vectors)
	if sourcePaths: # use linked paths if any
		for sourcePath in sourcePaths:
			for stroke in sourcePath.strokes:
				tangentSegmentsForStroke(center,radius,stroke,tangentSets)
	else: # else use other strokes
		if len(strokes) < 2:
			raise Exception('At least two strokes or one linked path are required')
		for stroke in path.strokes[1:]:
			tangentSegmentsForStroke(center,radius,stroke,tangentSets)
	for tangentSet in tangentSets:
		pdb.gimp_image_add_vectors(image,tangentSet, 0)	
		tangentSet.visible=True

def tangentsCircleToCircleForStroke(center1,radius1,stroke,tangents):
	center2,radius2=circleCenterRadius(stroke)
	# Normalize cases by usin c1,r1 for smallest circle
	if (radius2 < radius1):
		c1,r1=center2,radius2
		c2,r2=center1,radius1
	else:
		c1,r1=center1,radius1
		c2,r2=center2,radius2
		
	dist=distance(c1,c2)
	axisAngle=angle(c2,c1)
	
	if dist > (r1+r2): #circles don't intersect, there are inner tangents
		radiusAngle=math.acos((r2+r1)/dist)
		p1=pointAtRhoThetaFromOrigin(c1,r1,axisAngle+math.pi+radiusAngle)
		p2=pointAtRhoThetaFromOrigin(c2,r2,axisAngle+radiusAngle)
		gimp.VectorsBezierStroke(tangents[0],segmentStroke(p1,p2),False)
		p1=pointAtRhoThetaFromOrigin(c1,r1,axisAngle+math.pi-radiusAngle)
		p2=pointAtRhoThetaFromOrigin(c2,r2,axisAngle-radiusAngle)
		gimp.VectorsBezierStroke(tangents[1],segmentStroke(p1,p2),False)

	if dist >= (r2-r1): # circles intersect or are outside each other, there are outer tangents
		radiusAngle=math.acos((r2-r1)/dist)
		p1=pointAtRhoThetaFromOrigin(c1,r1,axisAngle+radiusAngle)
		p2=pointAtRhoThetaFromOrigin(c2,r2,axisAngle+radiusAngle)
		gimp.VectorsBezierStroke(tangents[2],segmentStroke(p1,p2),False)
		p1=pointAtRhoThetaFromOrigin(c1,r1,axisAngle-radiusAngle)
		p2=pointAtRhoThetaFromOrigin(c2,r2,axisAngle-radiusAngle)
		gimp.VectorsBezierStroke(tangents[3],segmentStroke(p1,p2),False)
	
	if dist < (r2-r1): # smaller circle entirely inside the bigger one: no tangents
		raise Exception('Circles centered at (%3.1f,%3.1f) and (%3.1f,%3.1f) are completely with each other, there are no tangents' % (c1[0],c1[1],c2[0],c2[1])) 
	
	
def tangentCircleToCircle_core(image,path):
	tangentSetIL=gimp.Vectors(image,'Tangents (IR) using <%s>' % (path.name))
	tangentSetIR=gimp.Vectors(image,'Tangents (IL) using <%s>' % (path.name))
	tangentSetOL=gimp.Vectors(image,'Tangents (OL) using <%s>' % (path.name))
	tangentSetOR=gimp.Vectors(image,'Tangents (OR) using <%s>' % (path.name))
	tangentSets=[tangentSetIL,tangentSetIR,tangentSetOL,tangentSetOR]
	strokes=path.strokes
	center,radius=circleCenterRadius(strokes[0])
	sourcePaths=filter(lambda v: v.linked,image.vectors)
	if sourcePaths: # use linked paths if any
		for sourcePath in sourcePaths:
			for stroke in sourcePath.strokes:
				tangentsCircleToCircleForStroke(center,radius,stroke,tangentSets)
	else: # else use other strokes
		if len(strokes) < 2:
			raise Exception('At least two strokes or one linked path are required')
		for stroke in path.strokes[1:]:
			tangentsCircleToCircleForStroke(center,radius,stroke,tangentSets)
	for tangentSet in tangentSets:
		pdb.gimp_image_add_vectors(image,tangentSet, 0)	
		tangentSet.visible=True

def multiplySegment_core(image,path):
	line=gimp.Vectors(image,'Multiplied segment using <%s>' % (path.name))
	for stroke in path.strokes:
		points=pointsFromStroke(stroke)
		if len(points)<3:
			raise Exception('Stroke starting at (%3.1f,%3.1f) should have at least 3 points' % (points[0][0],points[0][1]))
		multiplyFactor=len(points)-1
		p0=points[0]
		p1=points[1]
		dx=(p1[0]-p0[0])
		dy=(p1[1]-p0[1])
		linePoints=[p0,p0,p0,p1,p1,p1]
		for i in range(1,multiplyFactor):
			linePoints.extend(tripletAtXYFromOrigin(p0,dx*(i+1),dy*(i+1)))
		gimp.VectorsBezierStroke(line,flattenToStroke(linePoints),True)
        pdb.gimp_image_add_vectors(image, line, 0)	
        line.visible=True

def divideSegment_core(image,path):
	line=gimp.Vectors(image,'Divided segment using <%s>' % (path.name))
	for stroke in path.strokes:
		points=pointsFromStroke(stroke)
		if len(points)<3:
			raise Exception('Stroke starting at (%3.1f,%3.1f) should have at least 3 points' % (points[0][0],points[0][1]))
		divideFactor=len(points)-1
		p0=points[0]
		p1=points[-1]
		dx=(p1[0]-p0[0])/divideFactor
		dy=(p1[1]-p0[1])/divideFactor
		linePoints=[p0,p0,p0]
		for i in range(1,divideFactor):
			linePoints.extend(tripletAtXYFromOrigin(p0,dx*i,dy*i))
		linePoints.extend([p1,p1,p1])	
		gimp.VectorsBezierStroke(line,flattenToStroke(linePoints),True)
        pdb.gimp_image_add_vectors(image, line, 0)	
        line.visible=True
	
def protect(function,image,path):
	try:
		function(image,path)
	except Exception as e:
                print e.args[0]
                pdb.gimp_message(e.args[0])

def circleFromRadius(image,path):
	protect(circleFromRadius_core,image,path)
	
def circleFromDiameter(image,path):
	protect(circleFromDiameter_core,image,path)
	
def circumcircle(image,path):
	protect(circumcircle_core,image,path)
	
def star(image,path):
	protect(star_core,image,path)
	
def doubleStar(image,path):
	protect(doubleStar_core,image,path)
	
def spokes(image,path):
	protect(spokes_core,image,path)
	
def polygonFromCircumradius(image,path):
	protect(polygonFromCircumradius_core,image,path)
	
def polygonFromApothem(image,path):
	protect(polygonFromApothem_core,image,path)
	
def polygonFromSide(image,path):
	protect(polygonFromSide_core,image,path)
	
def rectangleUpright(image,path):
	protect(rectangleUpright_core,image,path)

def tangentCircleFromPoint(image,path):
	protect(tangentCircleFromPoint_core,image,path)

def tangentCircleToCircle(image,path):
	protect(tangentCircleToCircle_core,image,path)

def multiplySegment(image,path):
	protect(multiplySegment_core,image,path)

def divideSegment(image,path):
	protect(divideSegment_core,image,path)

### Registration
author='Ofnuts'
year='2014'
menu='<Vectors>/Shapes'
circleMenu=menu+'/Circle'
starMenu=menu+'/Star'
polygonMenu=menu+'/Polygon'
rectangleMenu=menu+'/Rectangle'
tangentMenu=menu+'/Tangent'
lineMenu=menu+'/Line'
images='*'
parameters=[(PF_IMAGE,'image','Input image', None),(PF_VECTORS,'path','Input path', None),]
whoiam='\n'+os.path.abspath(sys.argv[0])
    
register(
	'circle-from-radius',
	'Create circles taking a path as their radiuses'+whoiam,
	'Circle from radius',
	author,author,year,
	'Circle from radius',
	images,parameters,[],
	circleFromRadius,
	menu=circleMenu,
)

register(
	'circle-from-diameter',
	'Create circles taking a path as their diameter'+whoiam,
	'Circle from diameter',
	author,author,year,
	'Circle from diameter',
	images,parameters,[],
	circleFromDiameter,
	menu=circleMenu,
)

register(
	'circumcircle',
	'Create circumcircle (circle going through three points)'+whoiam,
	'Circumcircle',
	author,author,year,
	'Circumcircle',
	images,parameters,[],
	circumcircle,
	menu=circleMenu,
)

register(
	'star',
	'Create stars'+whoiam,
	'Star',
	author,author,year,
	'Star',
	images,parameters,[],
	star,
	menu=starMenu,
)

register(
	'double-star',
	'Create double stars'+whoiam,
	'Double star',
	author,author,year,
	'Double star',
	images,parameters,[],
	doubleStar,
	menu=starMenu,
)

register(
	'spokes',
	'Create spokes'+whoiam,
	'Spokes',
	author,author,year,
	'Spokes',
	images,parameters,[],
	spokes,
	menu=starMenu,
)

register(
	'polygon-from-circumradius',
	'Create polygons taking a path as their circumradius'+whoiam,
	'Polygon from circumradius',
	author,author,year,
	'Polygon from circumradius',
	images,parameters,[],
	polygonFromCircumradius,
	menu=polygonMenu,
)

register(
	'polygon-from-apothem',
	'Create polygons taking a path as their apothem'+whoiam,
	'Polygon from apothem',
	author,author,year,
	'Polygon from apothem',
	images,parameters,[],
	polygonFromApothem,
	menu=polygonMenu,
)

register(
	'polygon-from-side',
	'Create polygons taking a path as their side'+whoiam,
	'Polygon from side',
	author,author,year,
	'Polygon from side',
	images,parameters,[],
	polygonFromSide,
	menu=polygonMenu,
)

register(
	'rectangle-upright',
	'Create rectangle'+whoiam,
	'Rectangle with optional rounded corners',
	author,author,year,
	'Rectangle with optional rounded corners',
	images,parameters,[],
	rectangleUpright,
	menu=rectangleMenu,
)

register(
	'tangents-circle-with-point',
	'Create tangents to circle from point'+whoiam,
	'Tangents to circle from point',
	author,author,year,
	'Tangents to circle from point',
	images,parameters,[],
	tangentCircleFromPoint,
	menu=tangentMenu,
)

register(
	'tangents-betwen-circles',
	'Create tangents between circles'+whoiam,
	'Tangents betwen circles',
	author,author,year,
	'Tangents betwen circles',
	images,parameters,[],
	tangentCircleToCircle,
	menu=tangentMenu,
)

register(
	'multiply-segment',
	'Multiply segment'+whoiam,
	'Multiply segment',
	author,author,year,
	'Multiply segment',
	images,parameters,[],
	multiplySegment,
	menu=lineMenu,
)

register(
	'divide-segment',
	'Divide segment evenly'+whoiam,
	'Divide segment',
	author,author,year,
	'Divide segment',
	images,parameters,[],
	divideSegment,
	menu=lineMenu,
)


main()
