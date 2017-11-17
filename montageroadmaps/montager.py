#!/usr/bin/env python

"""This module produces roadmap montage PDFs."""

import os
import sys
import datetime
import subprocess
import shutil
from dateutil import parser

from pims.utils.datetime_ranger import hourrange
from pims.utils.iterabletools import grouper
from pims.utils.pimsdateutil import datetime_to_roadmap_fullstub

from margparser import parse_inputs

#montage -density 150 -mode concatenate -tile 3x2 /misc/yoda/www/plots/batch/year2017/month10/day11/2017_10_11_??_00_00.000_121f03_spgs_roadmaps500.pdf \
#/misc/yoda/www/plots/batch/year2017/month10/day12/2017_10_12_??_00_00.000_121f03_spgs_roadmaps500.pdf out.pdf

#montage -density 150 -mode concatenate -tile 3x2 S1_H00 S1_H08 S1_H16 S2_H00 S2_H08 S2_H16 out.pdf


MISSING8HR = '/home/pims/dev/programs/python/pims/montageroadmaps/missing8hr.pdf'
MISSINGDAY = '/home/pims/dev/programs/python/pims/montageroadmaps/missingday.pdf'
BATCHDIR = '/misc/yoda/www/plots/batch'
OUTDIR = '/tmp'


def full_name(f, suffix, replace=MISSING8HR):
    fname = datetime_to_roadmap_fullstub(f) + suffix
    if os.path.exists(fname):
        out = fname
    else:
        if replace:
            out = replace
        else:
            out = None
    return out


def main(h0, h1, s1, s2, suffix1, suffix2, suffix3, ptype='spgs', outdir='/tmp'):
    
    g = grouper(3, hourrange(h0, h1))
    
    for abc in g:
        day = abc[0].date()
        pdf = os.path.join(outdir, '%s%s' % (day, suffix3))
    
        files_sensor1 = [ full_name(x, suffix1) for x in abc ]
        files_sensor2 = [ full_name(x, suffix2) for x in abc ]
        files = files_sensor1 + files_sensor2
        
        if all([ f == MISSING8HR for f in files ]):
            shutil.copy(MISSINGDAY, pdf)
        else:
            subprocess.call(['montage', '-density', '150', '-mode', 'concatenate', '-tile', '3x2', files_sensor1[0], files_sensor1[1], files_sensor1[2], files_sensor2[0], files_sensor2[1], files_sensor2[2], pdf])
        
        #convert /tmp/2017_11_08_00_00_00.000_121f08_121f04_spgs_roadmapsmont.pdf -pointsize 36 -annotate +1250+40 '2017-09-22' -annotate +400+40 '121f02' -annotate +400+650 '121f05' /tmp/anndimdraw.pdf
        subprocess.call(['convert', pdf, '-pointsize', '36', '-annotate', '+1250+40', "%s" % day, '-annotate', '+400+40', "%s" % s1, '-annotate', '+400+650', "%s" % s2, pdf])
        
        print pdf

    # TODO for each month's worth, do like this:
    # cd /tmp; pdfunite 2017-11-*roadmapsmont.pdf 2017-11_121f03_es09_spgs_roadmapsmont.pdf; rm 2017-11-*roadmapsmont.pdf


if __name__ == '__main__':
    
    args = parse_inputs()
    print args
    
    h0 = args.date 
    h1 = h0 + datetime.timedelta(days=1)

    ptype = 'spgs'
    
    g = grouper(3, hourrange(h0, h1))
    
    for abc in g:

        s1 = args.sensors[0]
        s2 = args.sensors[1]
        
        suffix1 = '_%s_%s_roadmaps500.pdf' % (s1, ptype)
        suffix2 = '_%s_%s_roadmaps500.pdf' % (s2, ptype)
        suffix3 = '_%s_%s_%s_roadmapsmont.pdf' % (s1, s2, ptype)
    
        pdf = os.path.join(OUTDIR, '%s%s' % (str(h0), suffix3))
    
        files_sensor1 = [ full_name(x, suffix1) for x in abc ]
        files_sensor2 = [ full_name(x, suffix2) for x in abc ]
        files = files_sensor1 + files_sensor2
        
        #if all([ f == MISSING8HR for f in files ]):
        #    shutil.copy(MISSINGDAY, pdf)
        #else:
        #    subprocess.call(['montage', '-density', '150', '-mode', 'concatenate', '-tile', '3x2', files_sensor1[0], files_sensor1[1], files_sensor1[2], files_sensor2[0], files_sensor2[1], files_sensor2[2], pdf])
        #
        ##convert /tmp/2017_11_08_00_00_00.000_121f08_121f04_spgs_roadmapsmont.pdf -pointsize 36 -annotate +1250+40 '2017-09-22' -annotate +400+40 '121f02' -annotate +400+650 '121f05' /tmp/anndimdraw.pdf
        #subprocess.call(['convert', pdf, '-pointsize', '36', '-annotate', '+1250+40', "%s" % day, '-annotate', '+400+40', "%s" % s1, '-annotate', '+400+650', "%s" % s2, pdf])
        
        print pdf        
    

    ###s1 = sys.argv[1]
    ###s2 = sys.argv[2]
    ###
    ###h0 = parser.parse(sys.argv[3])
    ###h1 = parser.parse(sys.argv[4])
    ###
    ###ptype = 'spgs'
    ###
    ###suffix1 = '_%s_%s_roadmaps500.pdf' % (s1, ptype)
    ###suffix2 = '_%s_%s_roadmaps500.pdf' % (s2, ptype)
    ###suffix3 = '_%s_%s_%s_roadmapsmont.pdf' % (s1, s2, ptype)
    ###
    ####h0 = datetime.datetime(2017,  9,  22)
    ####h1 = datetime.datetime(2017,  9,  24)
    ####h0 = datetime.datetime(2017,  9,   1)
    ####h1 = datetime.datetime(2017, 11,  12)
    ###
    ###outdir = '/tmp'    
    ###
    ###main(h0, h1, s1, s2, suffix1, suffix2, suffix3, ptype=ptype, outdir=outdir)
    