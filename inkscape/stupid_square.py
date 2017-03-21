#!/usr/bin/env python 
'''
Copyright (C) 2007 John Beard john.j.beard@gmail.com

##This extension allows you to draw a Cartesian grid in Inkscape.
##There is a wide range of options including subdivision, subsubdivions
## and logarithmic scales. Custom line widths are also possible.
##All elements are grouped with similar elements (eg all x-subdivs)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''

import inkex
import subprocess
import simplestyle, sys
from math import *
import traceback
import os

def draw_SVG_line(x1, y1, x2, y2, width, name, parent):
    style = { 'stroke': '#000000', 'stroke-width':str(width), 'fill': 'none' }
    line_attribs = {'style':simplestyle.formatStyle(style),
                    inkex.addNS('label','inkscape'):name,
                    'd':'M '+str(x1)+','+str(y1)+' L '+str(x2)+','+str(y2)}
    inkex.etree.SubElement(parent, inkex.addNS('path','svg'), line_attribs )
    
def draw_SVG_rect(x,y,w,h, width, fill, name, parent):
    style = { 'stroke': '#000000', 'stroke-width':str(width), 'fill':fill}
    rect_attribs = {'style':simplestyle.formatStyle(style),
                    inkex.addNS('label','inkscape'):name,
                    'x':str(x), 'y':str(y), 'width':str(w), 'height':str(h)}
    inkex.etree.SubElement(parent, inkex.addNS('rect','svg'), rect_attribs )

class Line_Rectangle(inkex.Effect):

    def __init__(self):

        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--line_len",
                        action="store", type="int", 
                        dest="line_len", default=55,
                        help="Integer Length of Line to Draw")
        self.OptionParser.add_option("--width_rect",
                        action="store", type="float", 
                        dest="width_rect", default=100.1,
                        help="Width of Rect to Draw")
        self.OptionParser.add_option("--height_rect",
                        action="store", type="float", 
                        dest="height_rect", default=60.234,
                        help="Height of Rect to Draw")        
        self.OptionParser.add_option("--draw_sq",
                        action="store", type="inkbool", 
                        dest="draw_sq", default=False,
                        help="Draw Square (if true)")

    def effect(self):
        py_file = os.path.basename(__file__)
        #log_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'logs')
        log_path = '/tmp'
        log_file = os.path.join(log_path, py_file.replace('.py', '.txt'))
        fid = open(log_file, "w")
        try:
            
            # get some inputs in px
            self.options.width_rect = self.unittouu(str(self.options.width_rect) + 'px')
            self.options.height_rect = self.unittouu(str(self.options.height_rect) + 'px')
            self.options.line_len = self.unittouu(str(self.options.line_len) + 'px')
            
            # get crisscross element (node) by id
            group_id_str = 'groupAcrisscross'
            node_crisscross = self.getElementById(group_id_str)
            if node_crisscross is not None:
                if node_crisscross.tag == inkex.addNS('g', 'svg'):
                    fid.write('found %s\n' % group_id_str)
                    dstyle = simplestyle.parseStyle(node_crisscross.get('style'))
                    for ke, va in dstyle.iteritems():
                        fid.write( '\tkey: ' + str(ke) + ', val: ' + str(va) + '\n')
                    if self.options.draw_sq:
                        dstyle['display'] = 'inline'
                    else:
                        dstyle['display'] = 'none'
                    node_crisscross.set('style', simplestyle.formatStyle(dstyle))
                    fid.write('Turn CrissCross ON = %s\n' % str(self.options.draw_sq))
                elif node_crisscross.tag == inkex.addNS('rect', 'svg'):
                    fid.write('rect\n')
                else:
                    fid.write('unrecognized tag\n')
            
            # Embed rectangle and line in Group
            # Put in in the center of the current view
            t = 'translate(' + str( self.view_center[0] -  self.options.width_rect / 2.0) + ',' + \
                               str( self.view_center[1] - self.options.height_rect / 2.0) + ')'
            # # Put in in the center of the document
            # t = 'translate(' + str( doc_width -  self.options.width_rect / 2.0) + ',' + \
            #                    str( doc_height - self.options.height_rect / 2.0) + ')'
            g_attribs = {inkex.addNS('label','inkscape'):'LineRectangle:W' + \
                         str( self.options.width_rect ) + ':H' + str( self.options.height_rect ),
                         'transform':t }
            grid = inkex.etree.SubElement(self.current_layer, 'g', g_attribs)
            
            border_th = 5
            draw_SVG_rect(0, 0, self.options.width_rect, self.options.height_rect, border_th, 'none', 'Border', grid) # border rectangle

            dx = 11
            th = 3
            num_lines = 3
            for i in range(0, num_lines): # lines to be drawn
                if i > 0: # don't draw first line (we made a proper border)
                    draw_SVG_line(dx*i, 0,
                                  dx*i, self.options.height_rect,
                                  th,
                                  'Line' + str(i), grid)  
                    fid.write('line%02d\n' % i)

        except:
           traceback.print_exc(file=fid)
        finally:
            fid.close()
        
if __name__ == '__main__':
    e = Line_Rectangle()
    e.affect()

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
