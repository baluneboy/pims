#!/usr/bin/env python

import sys
import copy
import math
import lxml
import inkex
import simpletransform
import simplestyle
import traceback
from inkex import NSS
from lxml import etree
import datetime
from simpletransform import computeBBox

class SsaCoordsEffect(inkex.Effect):

    def __init__(self):
        inkex.Effect.__init__(self)
        self.log = False
        self.OptionParser.add_option("-s", "--subscript",
                                     action="store", type="string", 
                                     dest="subscript", default="1",
                                     help="Subscript of coord. sys. to generate")       
        self.OptionParser.add_option('-l', '--log', action = 'store',
                                     type = 'string', dest = 'logfile')
        self.OptionParser.add_option("-u", "--units",
                                    action="store", type="string", 
                                    dest="units", default="px",
                                    help="The unit of measurement for length.")        
        self.OptionParser.add_option('-x', '--translatex', 
                                    action='store', type='float', 
                                    dest='tx', default=2.0, 
                                    help='Horizontal distance?')
        self.OptionParser.add_option('-y', '--translatey', 
                                    action='store', type='float', 
                                    dest='ty', default=8.0, 
                                    help='Vertical distance?')
        self.OptionParser.add_option('-c', '--centerx', 
                                    action='store', type='string', 
                                    dest='cx', default='0', 
                                    help='x coordinate of center')
        self.OptionParser.add_option('-d', '--centery', 
                                    action='store', type='string', 
                                    dest='cy', default='0', 
                                    help='y coordinate of center')        
        self.OptionParser.add_option("-r", "--rotation",
                                     action="store", type="string", 
                                     dest="rotation", default="0",
                                     help="Rotation (deg) CCW.")           
        self.OptionParser.add_option('-b', '--bricks',
                                     action = 'store',
                                     type = 'string',
                                     dest = 'bricks',
                                     default = False)

    def logwrite(self, msg):
        if not self.log and self.options.logfile:
            self.log = open(self.options.logfile, 'w')
        if self.log:
            self.log.write(msg)

    def get_guides(self, doc_height): 
        # get parent's tag of the guides
        nv = self.document.xpath('/svg:svg/sodipodi:namedview', namespaces=inkex.NSS)[0]

        # get all the guides
        children = self.document.xpath('/svg:svg/sodipodi:namedview/sodipodi:guide', namespaces=inkex.NSS)

        # build dict of expected guides
        dg = {}
        for element in children:
            gid = element.get('id')
            if gid in ['guideAy', 'guideAx', 'guide1x', 'guide2x', 'guideSx']:
                pos = element.get('position').split(',')
                posx, posy = float(pos[0]), float(pos[1])
                oristr = element.get('orientation')
                # note we flip the flippin' y-coordinate for usefulness
                dg[gid] = (posx, doc_height - posy, oristr)
        
        return dg

    def change_visible(self, bln_on, node_from, obj_str):
        """use bln_on to change node_from's display attribute to: none (hidden) or inline (visible)"""
        # use this for like groupAcrisscross or groupAdot
        group_id_str = 'group%s%s' % (node_from, obj_str)
        self.logwrite('group_id_str is %s\n' % group_id_str)
        node_obj = self.getElementById(group_id_str)
        if node_obj is not None:
            if node_obj.tag == inkex.addNS('g', 'svg'):
                self.logwrite('found %s\n' % group_id_str)
                dstyle = simplestyle.parseStyle(node_obj.get('style'))
                
                for ke, va in dstyle.iteritems():
                    self.logwrite( '\tkey: ' + str(ke) + ', val: ' + str(va) + '\n')
                    
                if bln_on:
                    dstyle['display'] = 'inline'
                else:
                    dstyle['display'] = 'none'
                node_obj.set('style', simplestyle.formatStyle(dstyle))
                self.logwrite('turn %s ON = %s\n' % (obj_str, str(bln_on)))
            else:
                self.logwrite('unrecognized node_obj.tag "%s"\n' % node_obj.tag)
        else:
            self.logwrite('could not find node for "%s"\n' % group_id_str)   

    def is_group_visible(self, group_id_str):
        """return boolean for node's display attribute: True if visible; else False"""
        node_obj = self.getElementById(group_id_str)
        if node_obj is not None:
            if node_obj.tag == inkex.addNS('g', 'svg'):
                dstyle = simplestyle.parseStyle(node_obj.get('style'))
                bln = dstyle['display'] == 'inline'
                #self.logwrite('%s is visible: %s\n' % (group_id_str, str(bln)))
                return bln
            else:
                inkex.errormsg("Unrecognized group_id_str %s" % group_id_str)
        else:
            inkex.errormsg("Could not getElementById for group_id_str %s" % group_id_str)

    def get_group(self):
        """return str single char for group to manipulate"""
        groups = ['A', '1', '2', 'S']
        grpvis = [ self.is_group_visible('group' + i) for i in groups ]
        self.logwrite('grpvis = %s\n' % str(grpvis))
        if grpvis == [True, False, False, False]:
            grp = '1'
        elif grpvis == [True, True, False, False]:
            grp = '2'
        elif grpvis == [True, True, True, False]:
            grp = 'S'
        else:
            inkex.errormsg('could not determine group to manipulate based on visibility check')
        return grp

    def do_transforms(self, node, tx, ty, cx, cy, r, u, s=1.0):
        
        strtranslation = 'translate(' + str(self.unittouu(str(tx) + u)) + ', ' + str(self.unittouu(str(ty) + u))  + ')' 
        translation = simpletransform.parseTransform(strtranslation)

        strtranslation2= 'translate(' + str(self.unittouu(str(-1*cx) + u)) + ', ' + str(self.unittouu(str(-1*cy) + u))  + ')'
        translation2 = simpletransform.parseTransform(strtranslation2)

        strtranslation3= 'translate(' + str(self.unittouu(str(cx) + u)) + ', ' + str(self.unittouu(str(cy) + u))  + ')'
        translation3 = simpletransform.parseTransform(strtranslation3)

        strrotation = 'rotate(' + str(r)  +  ')'
        rotation = simpletransform.parseTransform(strrotation)

        strscaling = 'scale(' + str(s)  +  ')'
        scaling = simpletransform.parseTransform(strscaling)

        self.logwrite("transforms (%s):\n" % u)
        self.logwrite(' -> translation2 %s\n' % strtranslation2)
        self.logwrite(' -> rotation %s\n' % strrotation)        
        self.logwrite(' -> scale %s\n' % strscaling)        
        self.logwrite(' -> translation3 %s\n' % strtranslation3)        
        self.logwrite(' -> translation  %s\n' % strtranslation)        

        newNode = copy.deepcopy(node)
        simpletransform.applyTransformToNode(translation2, newNode)
        simpletransform.applyTransformToNode(rotation, newNode)
        simpletransform.applyTransformToNode(scaling, newNode)
        simpletransform.applyTransformToNode(translation3, newNode)
        simpletransform.applyTransformToNode(translation, newNode)

        self.current_layer.append(newNode)       

    def effect(self):

        try:
            self.logwrite('%s\n' % str(datetime.datetime.now()))
    
            # get doc size info
            svg = self.document.xpath('//svg:svg' , namespaces=NSS)[0]
            width = float(self.unittouu(svg.get('width')))
            height = float(self.unittouu(svg.get('height')))
            self.logwrite("w, h : %f, %f\n" % (width, height))
            
            # get guides
            dguides = self.get_guides(height)
           
            # determine which group to manipulate
            #grp = self.get_group()
            grp = '2'
            xpos = dguides['guide' + grp + 'x'][0]
            ypos = dguides['guideAy'][1]
            
            self.logwrite('group to manipulate is %s\n' % grp)        
            self.logwrite('this groups has xpos = %f and ypos = %f\n' % (xpos, ypos))
            inkex.errormsg('this groups has xpos = %f and ypos = %f\n' % (xpos, ypos))
            
            # get inputs and cast some as types
            #to_subscript = self.options.subscript
            u = self.options.units
            tx = float(self.options.tx)
            ty = float(self.options.ty)
            cx = float(self.options.cx)
            cy = float(self.options.cy)            
            r = -int(self.options.rotation)
            bricks = self.options.bricks == "true"
      
            #self.logwrite("subscript change to: %s\n" % to_subscript)
            self.logwrite("translation (%s):\n" % u)
            self.logwrite("  -> TX = %0.3f\n" % tx)
            self.logwrite("  -> TY = %0.3f\n" % ty)
            self.logwrite("center (%s):\n" % u)
            self.logwrite("  -> CX = %0.3f\n" % cx)
            self.logwrite("  -> CY = %0.3f\n" % cy)            
            self.logwrite("rotation CCW (deg): %d\n" % r)
    
            # FIXME this does not belong here like this
            node_obj = self.getElementById('group%s' % grp)
            #bbox = computeBBox(node_obj)
            #self.logwrite('bbox is %s\n' % str(bbox))
            
            for tup in [ (0.0,0.0), (-150.0, -90.0), (-300.0, -180.0), (-450.0, -270.0) ]:
                ty, r = tup[0], tup[1]
                self.do_transforms(node_obj, tx, ty, cx, cy, r, u, s=1.0/2.0)
            
            # translation
            #str_translation = 'translate(' + str(self.unittouu(str(tx) + units)) + ', ' + str(self.unittouu(str(ty) + units))  + ')' 
            #translation = simpletransform.parseTransform(str_translation)
            #simpletransform.applyTransformToNode(translation, node_obj)
            #self.logwrite("str_translation: %s\n" % str_translation)

            # rotation    
            #str_rotation = 'rotate(' + str(rotation)  +  ')'
            #rotation = simpletransform.parseTransform(str_rotation)
            #simpletransform.applyTransformToNode(rotation, node_obj)
            #xval = self.unittouu(str(tx) + units)
            #yval = self.unittouu(str(ty) + units)
            #str_rotation = 'rotate(-%d, %f, %f)' % (rotation, xval, yval)
            #rotation = simpletransform.parseTransform(str_rotation)
            #node_obj.set('transform', str_rotation)
            #self.logwrite("str_rotation: %s\n" % str_rotation)
            
            # change vis of group to be manipulated
            #self.change_visible(True, grp, '')

            # change color
            #self.logwrite('find node "%s", and change color from %s to %s\n' % (node_from, color_from, color_to))
        
            # handle crisscross and dot
            #bln_dot_on = not bricks
            #self.change_visible(bricks, grp, 'crisscross')
            #self.change_visible(bln_dot_on, grp, 'dot')
       
            # unrotate xyz subscripted labels
    
        except:
            if self.log: traceback.print_exc(file=self.log)
    
        finally:
            if self.log:
                self.logwrite('%s\n' % str(datetime.datetime.now()))
                self.logwrite("done\n")
                self.log.close()
      
effect = SsaCoordsEffect()
effect.affect()
