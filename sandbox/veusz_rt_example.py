#!/usr/bin/env python

import time
import numpy
import veusz.embed as veusz

# construct a Veusz embedded window
# many of these can be opened at any time
g = veusz.Embedded('window title')
g.EnableToolbar()

# construct the plot
g.To( g.Add('page') )
g.To( g.Add('graph') )

g.Add('xy', marker='tiehorz', MarkerFill__color='green')

# this stops intelligent axis extending
#g.Set('x/autoExtend', False)
#g.Set('x/autoExtendZero', False)

# zoom out
g.Zoom(0.8)

# loop, changing the values of the x and y datasets
for i in range(100000):
    x = numpy.arange(0+i/2., 7.+i/2., 0.05)
    y = numpy.sin(x)
    g.SetData('x', x)
    g.SetData('y', y)
    print "tick "
    # wait to animate the graph
    time.sleep(0.2)

# close the window (this is not strictly necessary)
g.Close()