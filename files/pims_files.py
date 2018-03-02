#!/usr/bin/env python

import re
import glob

# TODO always expect top to be a dirname (basepath) so start with file sep and end without filesep
# TODO always expect OPTIONAL sub to be intermediate path so start and end without file sep
# TODO can we validate glob acceptable versus regex acceptable pattern strings?
# TODO should we be using getter/setter type approach to build PimsFiles class?
# FIXME use 

class PimsFiles(object):
    
    def __init__(self, top, pat, sub=None, isglob=True):
        self.top = top
        self.sub = sub
        self.pat = pat
        self.isglob = isglob

    def run(self):
        print self.top
        print self.sub
        print self.pat
        print self.isglob


if __name__ == '__main__':

    #/misc/yoda/pub/pad/year2018/month02/day25/samses_accel_es09/2018_02_25_23_34_45.689+2018_02_25_23_44_45.747.es09
    top = '/misc/yoda/pub/pad'
    sub = 'year2018/month02/day25/samses_accel_es09'
    pat = '*es09'
    isglob = True
    pf = PimsFile(top, sub, pat, isglob)
    pf.run()