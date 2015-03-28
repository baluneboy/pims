#!/usr/bin/env python

from numpy import *

import pylab as p
import matplotlib.axes as a
import mpl_toolkits.mplot3d.axes3d as a3d

# Pass format as first key and frame number as second.
# EXAMPLES:
# python plot_helix3d.py pdf 100
# python plot_helix3d.py png 200
import sys
format=sys.argv[1]
frame=float(sys.argv[2])

# Define array of values for parameter t (time)
t=r_[0.:frame/10:300j]

'''any possibility to define exact number of elements as variable?
Something like: x=r_[0:10:(y/z)j]'''

# Define main variables of function
x=t
y=sin(t)
z=cos(t)

# Create main figure
fig=p.figure(figsize=(12,8))
fig.suptitle('Spiral Example', fontsize=14, fontweight='bold')

# Include 3D graph as rectangle using 60% width and 100% height in
# figure space
ax = a3d.Axes3D(fig,rect=[0,0,0.6,1])
ax.set_autoscale_on(False)
ax.set_xlim3d((0,30))
ax.set_ylim3d((-1,1))
ax.set_zlim3d((-1,1))
ax.set_xlabel('X = t')
ax.set_ylabel('Y = sin(t)')
ax.set_zlabel('Z = cos(t)')
ax.plot3D(x,y,z)

# Adjust area for common subplots to not overlap 3D graph
fig.subplots_adjust(left=0.66,bottom=0.05,top=0.95)

# Add subplots to figure one by one. Value passed to add_subplot 411
# should be read as (4 rows, 1 column, 1st plot)
bx = fig.add_subplot(414)
bx.set_autoscale_on(False)
bx.set_ylabel('z')
bx.set_xlabel('t')
bx.set_xlim((0,30))
bx.set_ylim((-1,1))
bx.plot(t,z)

cx = fig.add_subplot(413)
cx.set_autoscale_on(False)
cx.set_xlim((0,30))
cx.set_ylabel('y')
cx.set_ylim((-1,1))
cx.plot(t,y)

dx = fig.add_subplot(412)
dx.set_autoscale_on(False)
dx.set_ylabel('x')
dx.set_xlim((0,30))
dx.set_ylim((0,30))
dx.plot(t,x)

fx = fig.add_subplot(411)
fx.set_autoscale_on(False)
fx.text(5, 15, 'x: %s'% x[299], fontsize=12)
fx.text(5, 10, 'y: %s'% y[299], fontsize=12)
fx.text(5,  5, 'z: %s'% z[299], fontsize=12)
fx.set_xlim((0,30))
fx.set_ylim((0,20))
for tick in fx.yaxis.get_major_ticks():
    tick.label1On = False
    tick.label2On = False
    tick.tick1On = False
    tick.tick2On = False
for tick in fx.xaxis.get_major_ticks():
    tick.label1On = False
    tick.label2On = False
    tick.tick1On = False
    tick.tick2On = False

# Uncomment this line to check the result in GUI
# p.show()

# Save result to file in format like 0001.png
p.savefig('/tmp/%04d.%s'% (frame, format))
