#!/usr/bin/env python

import sys
import math
import lxml
import inkex
#import simpletransform
#import simplestyle
import numpy as np
import traceback
from inkex import NSS
from lxml import etree
import datetime
from vector import ChattyVector, rotation_matrix

class SsaTransformEffect(inkex.Effect):

    def __init__(self):
        inkex.Effect.__init__(self)
        self.log = False
        self.OptionParser.add_option("-c", "--coordsys",
                                     action="store", type="string", 
                                     dest="coordsys", default="A",
                                     help="Coordinate System to change.")
        self.OptionParser.add_option("-t", "--text1",
                                     action="store", type="string", 
                                     dest="text1", default="NE",
                                     help="Compass setting for into/outta plane axis text label.")
        self.OptionParser.add_option("-a", "--axis1",
                                     action="store", type="string", 
                                     dest="axis1", default="Y",
                                     help="Axis that is into or out of page.")
        self.OptionParser.add_option("-b", "--arrow1",
                                     action="store", type="string", 
                                     dest="arrow1", default="Dot",
                                     help="Arrow that is into/cross or outta/dot page.")
        self.OptionParser.add_option("-d", "--axis2",
                                     action="store", type="string", 
                                     dest="axis2", default="X",
                                     help="In-plane axis #2.")
        self.OptionParser.add_option("-e", "--arrow2",
                                     action="store", type="string", 
                                     dest="arrow2", default="E",
                                     help="Arrow that is into/cross or outta/dot page.")
        self.OptionParser.add_option("-f", "--axis3",
                                     action="store", type="string", 
                                     dest="axis3", default="X",
                                     help="In-plane axis #3.")
        self.OptionParser.add_option("-g", "--arrow3",
                                     action="store", type="string", 
                                     dest="arrow3", default="E",
                                     help="Arrow that is into/cross or outta/dot page.")
        self.OptionParser.add_option('-l', '--log',
                                     action = 'store', type = 'string',
                                     dest = 'logfile', default='/Users/ken/temp/ssaxformlog.txt',
                                     help="Log filename.")

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
    
    def effect(self):

        try:
            self.logwrite('%s BEGIN\n' % str(datetime.datetime.now()))
    
            #cv = ChattyVector(1,1,0)
            #self.logwrite('v = %s\n' % str(cv))
    
            i = [1, 0, 0]
            j = [0, 1, 0]
            k = [0, 0, 1]
            oa = [i, j, k]
            for yaw in range(0, 360, 90):
                zaxis = [0, 0, 1]
                yaw_rad = yaw*np.pi/180.0
                a = np.dot(rotation_matrix(zaxis, yaw_rad), oa)
                r = np.rint(a)
                self.logwrite("\nYaw = %.1f, m' =\n%s\n" % (yaw, r))
                
                #for pitch in range(0, 360, 90):
                #    pitch_rad = pitch*np.pi/180.0
                #
                #for roll in range(0, 360, 90):
                #    roll_rad = pitch*np.pi/180.0
                                    
    
            # get doc size info
            svg = self.document.xpath('//svg:svg' , namespaces=NSS)[0]
            width = float(self.unittouu(svg.get('width')))
            height = float(self.unittouu(svg.get('height')))
            self.logwrite("\nw, h : %f, %f\n" % (width, height))
            
            # get guides
            dguides = self.get_guides(height)
           
            # determine which group to manipulate
            #grp = self.get_group()
            #xpos = dguides['guide' + grp + 'x'][0]
            #ypos = dguides['guideAy'][1]
            
            # get inputs
            coordsys = self.options.coordsys
            axis1    = self.options.axis1
            arrow1   = self.options.arrow1
            text1    = self.options.text1
            axis2    = self.options.axis2
            arrow2   = self.options.arrow2
            axis3    = self.options.axis3
            arrow3   = self.options.arrow3            
      
            #self.logwrite("subscript change to: %s\n" % to_subscript)
            self.logwrite("coordsys: %s\n" % coordsys)
            self.logwrite("text1: %s\n" % text1)
            self.logwrite("axis1: %s\n" % axis1)
            self.logwrite("arrow1: %s\n" % arrow1)
            self.logwrite("axis2: %s\n" % axis2)
            self.logwrite("arrow2: %s\n" % arrow2)
            self.logwrite("axis3: %s\n" % axis3)
            self.logwrite("arrow3: %s\n" % arrow3)
      
        except:
            if self.log: traceback.print_exc(file=self.log)
    
        finally:
            if self.log:
                self.logwrite('%s END\n' % str(datetime.datetime.now()))
                self.log.close()
      
effect = SsaTransformEffect()
effect.affect()
