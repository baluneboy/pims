#!/usr/bin/env python

import os
import re
import sys
import time
import random # FIXME once we have good "fit_to_dur" algorithm to fill 15 minutes
import subprocess

from pims.database.podcasts import get_db_con, db_insert_podcast, db_record_exists, PodcastFile
from pims.lib.niceresult import NiceResult
from pims.files.utils import most_recent_file_with_suffix, filter_filenames, filter_dirnames
from pims.files.filter_pipeline import FileFilterPipeline, ExtensionStartsWith, YoungFile, MinutesLongMp3File
#from pims.podgrab.podutils import NotInGrabbedPodcastsDb # specialized for filter pipeline
from pims.files.fit_duration import fit_to_dur

# input parameters
defaults = {
#'from_topdir':   '/Volumes/serverHD2/data/podcasts', # base path on macmini3 to copy podcasts from
'from_topdir':   '/Users/ken/Music/iTunes/iTunes Media/Podcasts', # base path on macmini3 to copy podcasts from
'want_minutes':     12,                               # integer total duration desired in minutes
'min_minutes':     0.9,                               # min duration (minutes) for any given mp3 file
'max_minutes':    10.0,                               # max duration (minutes) for any given mp3 file
'to_destpath':   '/Users/ken/podcasts',               # destination path to copy to
'db_file':       '/Users/ken/Databases/podcasts.db',  # full path to podcasts sqlite db file
}
parameters = defaults.copy()


def get_podcast_dirs(topdir='/Users/ken/Music/iTunes/iTunes Media/Podcasts'):
    subdirPattern = '.*'
    predicate = re.compile(os.path.join(topdir, subdirPattern)).match
    return list(filter_dirnames(topdir, predicate))

    
def get_mp3_files(mp3dir):
    fullfile_pattern = r'%s' % os.path.join(mp3dir, '.*\.mp3')
    return list(filter_filenames(mp3dir, re.compile(fullfile_pattern).match))

   
def get_many_mp3_files(con, topdir='/Users/ken/Music/iTunes/iTunes Media/Podcasts', min_minutes=0.5, max_minutes=10.0):
   
    # Initialize processing pipeline (prime the pipe with callables)
    ffp = FileFilterPipeline(
        MinutesLongMp3File(min_minutes=min_minutes, max_minutes=max_minutes),
        #YoungFile(max_age_minutes=max_age_minutes),
        #NotInGrabbedPodcastsDb(),
        )
    print ffp
    
    mp3_files = []
    for d in get_podcast_dirs(topdir=topdir):
        print d
        file_list = get_mp3_files(d)
        # apply processing pipeline to perhaps prune input list of files
        for f in ffp(file_list):
            if db_record_exists(con, f):
                print ' -> SKIP %s since db record exists already' % f
                continue            
            print ' -> KEEP %s' % f
            mp3_files.append(f)
    
    return mp3_files


def parameters_ok():
    """check for reasonableness of parameters"""

    if not os.path.exists(parameters['from_topdir']):
        print 'base path (%s) does not exist' % parameters['from_topdir']
        return False
    
    if not os.path.exists(parameters['db_file']):
        print 'db_file (%s) does not exist' % parameters['db_file']
        return False
    
    try:
        parameters['min_minutes'] = float(parameters['min_minutes'])
    except Exception, e:
        print 'could not get min_minutes as float: %s' % e.message
        return False

    try:
        parameters['max_minutes'] = float(parameters['max_minutes'])
    except Exception, e:
        print 'could not get max_minutes as float: %s' % e.message
        return False    

    try:
        parameters['want_minutes'] = int(parameters['want_minutes'])
    except Exception, e:
        print 'could not get want_minutes as integer: %s' % e.message
        return False
    
    return True # all OK; otherwise, return False somewhere above


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
    want_minutes = parameters['want_minutes']
    min_minutes = parameters['min_minutes']
    max_minutes = parameters['max_minutes']
    db_file = parameters['db_file']
    
    # get list of suitable mp3 podcast filenames
    con = get_db_con(db_file)
    mp3_files = get_many_mp3_files(con, topdir=topdir, min_minutes=min_minutes, max_minutes=max_minutes)

    if not mp3_files:
        print 'no mp3 files match our criteria'
        con.close()
        # FIXME why not copy over a few energizing songs that span 15 minutes here for fill?
        return False

    # get chosen ones that in aggregate will "fit to duration"
    chosen_files = fit_to_dur(mp3_files, total_minutes=want_minutes)
        
    total_minutes = 0.0
    dest = 'ken@macmini2:' + destdir
    for mp3_file in chosen_files:
        # FIXME next few lines are total crap, we need to refactor
        print 'attempting scp from %s to %s' % (mp3_file, dest) #; continue
        scp_cmd = ['scp', mp3_file, dest]
        retcode = subprocess.call(scp_cmd)
        if retcode == 0:
            print 'scp okay'
            pf = PodcastFile(mp3_file)
            total_minutes += pf.minutes
            insert_ok = db_insert_podcast(con, mp3_file)
            if not insert_ok:
                print 'could not insert record for %s' % mp3_file
            else:
                print 'inserted record for %s' % mp3_file
        else:
            print 'skip %s, could not do scp for whatever reason' % mp3_file
    con.close()

    return True


def main(argv):
    """describe main routine here"""

    # parse command line
    for p in argv[1:]:
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
                return 2 # non-zero for failure

    print_usage()

# run main with cmd line args and return exit code
if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))
