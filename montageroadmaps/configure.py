#!/usr/bin/env python

"""This module provides classes to configure roadmap montage PDFs."""

import os
import sys
import datetime
import subprocess
import shutil
from dateutil import parser

from pims.utils.datetime_ranger import hourrange, dayrange
from pims.utils.iterabletools import grouper
from pims.utils.pimsdateutil import datetime_to_roadmap_fullstub

from margparser import parse_inputs
from montager import full_name

#montage -density 150 -mode concatenate -tile 3x2 /misc/yoda/www/plots/batch/year2017/month10/day11/2017_10_11_??_00_00.000_121f03_spgs_roadmaps500.pdf \
#/misc/yoda/www/plots/batch/year2017/month10/day12/2017_10_12_??_00_00.000_121f03_spgs_roadmaps500.pdf out.pdf

#montage -density 150 -mode concatenate -tile 3x2 S1_H00 S1_H08 S1_H16 S2_H00 S2_H08 S2_H16 out.pdf


_MISSING8HR = '/home/pims/dev/programs/python/pims/montageroadmaps/missing8hr.pdf'
_MISSINGDAY = '/home/pims/dev/programs/python/pims/montageroadmaps/missingday.pdf'
_DEFAULT_MODULE = 'LAB'
_MODULES = {
    'LAB': ['121f03', 'es09'],
    'COL': ['121f04', '121f08'],
    'JEM': ['121f02', '121f05'],
}
_DEFAULT_SENSORS = _MODULES['LAB']
_TWODAYSAGO = datetime.date.today() + datetime.timedelta(days=-2)
_DEFAULT_START = datetime.datetime.combine(_TWODAYSAGO, datetime.time(0,0))
_DEFAULT_STOP = _DEFAULT_START + datetime.timedelta(days=1)


class LabModule(object):
    
    def __init__(self, lab):
        self.lab = lab.upper()
        self.sensors = MODULES[self.lab]
        
    def __str__(self):
        s = 'Module: %s' % self.lab
        s += ', Sensors:  ' + ', '.join(self.sensors)
        return s
        

class DailyMontage(object):
    
    def __init__(self, sensors, date_range, columns=3, rows=2):
        self.sensors = sensors
        self.date_range = date_range
        self.columns = columns
        self.rows = rows
        
    def __str__(self):
        s = 'columns: %d, ' % self.columns
        s += 'rows: %d' % self.rows
        return s
    

class RoadmapMontage(DailyMontage):
    
    def __init__(self, sensors=None, date_start=None, date_stop=None, ptype=None):

        if not sensors:
           sensors = _DEFAULT_SENSORS
        if len(sensors) != 2:
            raise Exception('need exactly 2 sensors')           
        self.sensors = sensors
        
        if not date_start:
           date_start = _DEFAULT_START
        if not date_stop:
           date_stop = _DEFAULT_STOP
        self.date_start = date_start
        self.date_stop = date_stop
        self.date_range = hourrange(_DEFAULT_START, _DEFAULT_STOP)

        if not ptype:
            ptype = 'spgs'
        self.ptype = ptype

        self.suffix1 = '_%s_%s_roadmaps*.pdf' % (self.sensors[0], self.ptype)
        self.suffix2 = '_%s_%s_roadmaps*.pdf' % (self.sensors[1], self.ptype)
        self.suffix3 = '_%s_%s_%s_roadmapsmont.pdf' % (self.sensors[0], self.sensors[1], self.ptype) 

        # now call super's init with sensors and date_range
        super(RoadmapMontage, self).__init__(self.sensors, self.date_range)
        
    def __str__(self):
        s = super(RoadmapMontage, self).__str__()
        s += '\nsensors:  ' + ', '.join(self.sensors)
        s += '\ndate_start:  %s' % self.date_start
        s += '\ndate_stop:   %s' % self.date_stop
        s += '\nptype:  %s' % self.ptype
        s += '\nsuffix1:  %s' % self.suffix1
        s += '\nsuffix2:  %s' % self.suffix2
        s += '\nsuffix3:  %s' % self.suffix3        
        s += '\n-------------'
        return s
    
    def demo_show(self):
        g = grouper(self.columns, self.date_range)
        
        for abc in g:
            outdir = '/tmp'
            day = abc[0].date()
            pdf = os.path.join(outdir, '%s%s' % (str(abc[0].date()), self.suffix3))
        
            s1 = self.sensors[0]
            s2 = self.sensors[1]
            
            files_sensor1 = [ full_name(x, self.suffix1) for x in abc ]
            files_sensor2 = [ full_name(x, self.suffix2) for x in abc ]
            files = files_sensor1 + files_sensor2
            
            if all([ f == _MISSING8HR for f in files ]):
                shutil.copy(_MISSINGDAY, pdf)
            else:
                subprocess.call(['montage', '-density', '150', '-mode', 'concatenate', '-tile', '3x2', files_sensor1[0], files_sensor1[1], files_sensor1[2], files_sensor2[0], files_sensor2[1], files_sensor2[2], pdf])
            
            #convert /tmp/2017_11_08_00_00_00.000_121f08_121f04_spgs_roadmapsmont.pdf -pointsize 36 -annotate +1250+40 '2017-09-22' -annotate +400+40 '121f02' -annotate +400+650 '121f05' /tmp/anndimdraw.pdf
            subprocess.call(['convert', pdf, '-pointsize', '36', '-annotate', '+1250+40', "%s" % day, '-annotate', '+400+40', "%s" % s1, '-annotate', '+400+650', "%s" % s2, pdf])
            
            print pdf     
    
    
if __name__ == '__main__':
    
    #m0 = RoadmapMontage()
    #m0.demo_show()
    
    #m1 = RoadmapMontage(sensors=['121f04', '121f05'])
    #print m1
    #m1.demo_show()
    
    week_ago = datetime.date.today() + datetime.timedelta(days=-7)
    start = week_ago
    stop = start + datetime.timedelta(days=3)
    
    m2 = RoadmapMontage(sensors=['121f02', '121f03'], date_start=start, date_stop=stop)
    print m2
    m2.demo_show()    


