#!/usr/bin/env python

import os
import re
import sys
import time
import subprocess

from pims.lib.niceresult import NiceResult
from pims.files.utils import most_recent_file_with_suffix, filter_filenames, filter_dirnames
from pims.files.filter_pipeline import FileFilterPipeline, EndsWith, YoungFile, MinutesLongMp3File

# input parameters
defaults = {
'from_topdir':       '/Volumes/serverHD2/data/podcasts', # base path on macmini3 to copy podcasts from
'min_dur_minutes':   0.9,                                # min duration (minutes) for mp3 file
'max_age_minutes':   15.0,                               # max age (minutes) for mp3 file
'to_destpath':       '/Users/ken/podcasts',              # destination path to copy to
}
parameters = defaults.copy()

def get_podcast_dirs(topdir='/Volumes/serverHD2/data/podcasts'):
    subdirPattern = '.*'
    predicate = re.compile(os.path.join(topdir, subdirPattern)).match
    return list(filter_dirnames(topdir, predicate))
    
def get_mp3_files(mp3dir):
    fullfile_pattern = r'%s' % os.path.join(mp3dir, '.*\.mp3')
    return list(filter_filenames(mp3dir, re.compile(fullfile_pattern).match))
   
def get_big_young_mp3_files(topdir='/Volumes/serverHD2/data/podcasts', min_dur_minutes=0.5*1024*1024, max_age_minutes=15):
   
    # Initialize processing pipeline (prime the pipe with callables)
    ffp = FileFilterPipeline(MinutesLongMp3File(min_minutes=0.9), EndsWith('.mp3'), YoungFile(max_age_minutes=max_age_minutes))
    print ffp
    
    # Apply processing pipeline input #1 (now ffp is callable)
    mp3_files = []
    for d in get_podcast_dirs(topdir=topdir):
        print d
        file_list = get_mp3_files(d)
        for f in ffp(file_list):
            print ' -> %s' % f
            mp3_files.append(f)
    
    return mp3_files

# check for reasonableness of parameters
def parameters_ok():
    """check for reasonableness of parameters"""

    if not os.path.exists(parameters['from_topdir']):
        print 'base path (%s) does not exist' % parameters['from_topdir']
        return False
    
    try:
        parameters['min_dur_minutes'] = float(parameters['min_dur_minutes'])
    except Exception, e:
        print 'could not get min_dur_minutes as float: %s' % e.message
        return False

    try:
        parameters['max_age_minutes'] = float(parameters['max_age_minutes'])
    except Exception, e:
        print 'could not get max_age_minutes as float: %s' % e.message
        return False    

    return True # all OK; otherwise, return False somewhere above

# print helpful text how to run the program
def print_usage():
    """print helpful text how to run the program"""
    #FIXME with git keyword sub via following:
    # http://stackoverflow.com/questions/11534655/git-keyword-substitution-like-those-in-subversion
    #print version << BETTER GO AT THIS???
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def secure_copy(params):
    """scp mp3file(s) to destdir"""

    topdir = parameters['from_topdir']
    destdir = parameters['to_destpath']
    min_dur_minutes = parameters['min_dur_minutes']
    max_age_minutes = parameters['max_age_minutes']
    mp3_files = get_big_young_mp3_files(topdir=topdir, min_dur_minutes=min_dur_minutes, max_age_minutes=max_age_minutes)

    if not mp3_files:
        print 'no mp3 files match our criteria'
        return False
    
    for mp3file in mp3_files:
        dest = 'ken@192.168.0.199:' + destdir
        print 'start scp from %s to %s' % (mp3file, dest) #; continue
        scp_cmd = ['scp', mp3file, dest]
        retcode = subprocess.call(scp_cmd)
        if retcode != 0:
            raise Exception('problem with scp')

    return True

# describe main routine here
def main(argv):
    """describe main routine here"""

    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parameters_ok():
            nr = NiceResult(secure_copy, parameters)
            nr.do_work()
            result = nr.get_result()
            if result:
                return 0 # zero for unix success
            else:
                return -1

    print_usage()

# run main with cmd line args and return exit code
if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))
