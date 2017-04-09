#!/usr/bin/env python

import sys, copy

sys.path.append('/Applications/Inkscape.app/Contents/Resources/extensions')
import inkex, simpletransform
import numpy as np

from math import sin, cos, pi, pow

class DuplicateMultiple(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('-b', '--begin',
                action='store', type='int', 
                dest='begin', default=0, 
                help='n starts here')
        self.OptionParser.add_option('-e', '--end', 
                action='store', type='int',
                dest='end', default=10, 
                help='n stops here')
        self.OptionParser.add_option('-x', '--horizontal', 
                action='store', type='string', 
                dest='horizontal', default='n', 
                help='Horizontal distance?')
        self.OptionParser.add_option('-y', '--vertical', 
                action='store', type='string', 
                dest='vertical', default='n^2', 
                help='Vertical distance?')
        self.OptionParser.add_option('-c', '--centerx', 
                action='store', type='string', 
                dest='cx', default='0', 
                help='x coordinate of center')
        self.OptionParser.add_option('-d', '--centery', 
                action='store', type='string', 
                dest='cy', default='0', 
                help='y coordinate of center')
        self.OptionParser.add_option("-u", "--unit",
                action="store", type="string", 
                dest="unit", default="px",
                help="The unit of the measurement")
        self.OptionParser.add_option('-s', '--scale', 
                action='store', type='string', 
                dest='scale', default="n/2", 
                help='Scale Factor')
        self.OptionParser.add_option('-r', '--rotate', 
                action='store', type='string', 
                dest='rotate', default='-90', 
                help='Degrees rotated CW')

    def effect(self):
        cx = eval(self.options.cx)
        cy = eval(self.options.cy)
        if self.selected:
            for id, node in self.selected.iteritems():
                for n in range(self.options.begin, self.options.end+1):
                    horiz = eval(self.options.horizontal)
                    vert = eval(self.options.vertical)
                    strtranslation = 'translate(' + str(self.unittouu(str(horiz) + self.options.unit)) + ', ' + str(self.unittouu(str(vert) + self.options.unit))  + ')' 
                    translation = simpletransform.parseTransform(strtranslation)

                    strtranslation2= 'translate(' + str(self.unittouu(str(-1*cx) + self.options.unit)) + ', ' + str(self.unittouu(str(-1*cy) + self.options.unit))  + ')'

                    translation2 = simpletransform.parseTransform(strtranslation2)

                    strtranslation3= 'translate(' + str(self.unittouu(str(cx) + self.options.unit)) + ', ' + str(self.unittouu(str(cy) + self.options.unit))  + ')'

                    translation3 = simpletransform.parseTransform(strtranslation3)

                    strrotation = 'rotate(' + str(eval(self.options.rotate))  +  ')'
                    rotation = simpletransform.parseTransform(strrotation)
                    strscaling = 'scale(' + str(eval(self.options.scale))  +  ')'
                    scaling = simpletransform.parseTransform(strscaling)

                    newNode = copy.deepcopy(node)
                    simpletransform.applyTransformToNode(translation2, newNode)
                    simpletransform.applyTransformToNode(rotation, newNode)
                    simpletransform.applyTransformToNode(scaling, newNode)
                    simpletransform.applyTransformToNode(translation3, newNode)
                    simpletransform.applyTransformToNode(translation, newNode)

                    self.current_layer.append(newNode)
                    node = newNode
                    cx += horiz
                    cy += vert

effect = DuplicateMultiple()
effect.affect()