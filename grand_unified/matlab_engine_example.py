#!/usr/bin/env python

import sys
import numpy as np
import matlab.engine

def addpaths(eng):
    eng.addpath(r'/home/pims/dev/matlab/programs/webserver/templates',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/dailybackfill',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/datasets',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/editormacro',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/webserver',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/mym',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/vibratory/guifigs',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/vibratory',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/transform',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/figutils',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/fileutils',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/pimsuitools',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/pimsstrfun',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/pimsstats',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/pimssignal/outputresolution',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/pimssignal',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/pimslang',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/pimselmat',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/pimsdatafun',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/quasisteady/oare',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/quasisteady/guifigs',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/quasisteady',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/output/qthfun',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/output/oututils',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/output',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/mews',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/housekeeping',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/frontend/timeutils/convert1970',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/frontend/timeutils',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/frontend/parameters/edit',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/frontend/parameters',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/frontend/padutils',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/frontend/meta',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/frontend/guiutils',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/frontend/guifigs',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/frontend/general',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/frontend/debug',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/frontend/batch',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/frontend',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/data/batch/config',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/data/batch',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/data/reqs',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/data/config',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/data/color',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/data/ancillary',nargout=0)
    eng.addpath(r'/home/pims/dev/matlab/programs/pops',nargout=0)


def demo_old():
    
    eng = matlab.engine.start_matlab() # why doesn't "-r" work here to call startup.m?
    addpaths(eng) # add paths to PIMS code

    # pass a string into a matlab function, get new string out
    new_str = eng.foostr('abcde')
    print new_str
    
    # pass an array into matlab function, get new array out (as numpy array)
    arr = eng.magic(6)
    print arr
    new_arr = eng.fooarray(arr)
    print np.array(new_arr)

    #eng.eval("T = readtable('patients.dat');", nargout=0)
    eng.eval("T = readtable('/home/pims/Documents/grand_inputs_example1.dat');", nargout=0)
    eng.eval("S = table2struct(T, 'ToScalar', true);", nargout=0)
    eng.eval("disp(S)", nargout=0)
    eng.eval("S.Start", nargout=0)

def demo():
    
    eng = matlab.engine.start_matlab() # why doesn't "-r" work here to call startup.m?
    addpaths(eng) # add paths to PIMS code
    eng.eval("s = read_grand_table('/home/pims/Documents/grand_unified_inputs.dat');", nargout=0)
    eng.eval("disp(s)", nargout=0)
    eng.eval("datestr(s.sdnStart)", nargout=0)
    eng.eval("s.extras", nargout=0)
    
def main():
    
    demo()
    return 2

    # FIXME can we call startup.m using "-r" in engine start or not (it did not seem to work)
    eng = matlab.engine.start_matlab() # why doesn't "-r" work here to call startup.m?
    addpaths(eng) # bug with "-r" on start, so add paths to PIMS code base here
   
    # example of general function for grand unification
    start_gmt = '17-Feb-2015,14:00';
    stop_gmt =  '17-Feb-2015,14:20:00';
    eng.foofun('reboost', 'Progress 99P', start_gmt, stop_gmt, 'one', 'two', 39)
    eng.quit()

    return 0

if __name__ == '__main__':
    sys.exit(main())
