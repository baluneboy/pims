#!/usr/bin/env python

import os
import sys
import datetime
import sqlite3
import subprocess
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

from pims.lib.niceresult import NiceResult
from pims.files.utils import filter_filenames, filter_dirnames


# input parameters
defaults = {
'top_dir': '/Users/ken/Music/iTunes/iTunes Media/Podcasts', # base path on macmini3 to copy podcasts from
'db_file': '/Users/ken/Databases/podcasts.db',              # full path to podcasts sqlite db file
}
parameters = defaults.copy()


def parameters_ok():
    """check for reasonableness of parameters"""

    if not os.path.exists(parameters['top_dir']):
        print 'top_dir (%s) does not exist' % parameters['top_dir']
        return False
    
    if not os.path.exists(parameters['db_file']):
        print 'db_file (%s) does not exist' % parameters['db_file']
        return False
   
    return True # all OK; otherwise, return False somewhere above

    
class PodcastFile(object):

    def __init__(self, mp3_file):
        self.mp3_file = mp3_file
        self.basename = os.path.basename(mp3_file)
        self.dirname = os.path.dirname(mp3_file)
        self.subdir = os.path.basename(self.dirname)
        self.minutes = self.get_mp3_minutes()
        self.year, self.artist, self.title, self.genre = self.get_id3_info()
    
    def __str__(self):
        s =  'mp3_file: %s' % self.mp3_file
        s += '\nbasename: %s' % self.basename
        s += '\nminutes: %0.1f' % self.minutes
        s += '\nyear: %s' % self.year        
        s += '\nartist: %s' % self.artist        
        s += '\ntitle: %s' % self.title        
        s += '\ngenre: %s' % self.genre
        return s
    
    def get_mp3_minutes(self):
        audio = MP3(self.mp3_file)
        return audio.info.length / 60.0
    
    def get_id3_info(self):
        """"""
        audio = ID3(self.mp3_file)
        year, artist, title, genre = 'YEAR', 'ARTIST', 'TITLE', 'GENRE'
        try:
            year =   "%s" % audio["TDRC"].text[0]
            artist = "%s" % audio['TPE1'].text[0]
            title =  "%s" % audio['TIT2'].text[0]
            genre =  "%s" % audio['TCON'].text[0]
        except:
            print 'could not get some or all of these from ID3: [year, artist, title, genre]'
        return year, artist, title, genre


def get_db_con(db_file):
    return sqlite3.connect(db_file)


def db_record_exists(con, mp3_file):
    pf = PodcastFile(mp3_file)
    rec_exists = True
    # context manager, so if successful, then con.commit() is called automatically afterwards
    # con.rollback() is called after the with block finishes with an exception, the
    # exception is still raised and must be caught
    try:
        with con:
            cursor = con.cursor()
            cursor.execute('SELECT count(*) FROM podcasts WHERE basename = ? AND subdir = ?', (pf.basename, pf.subdir))
            data = cursor.fetchone()[0]
            if data == 0:
                rec_exists = False
    except sqlite3.IntegrityError, ei:
        print "integrity issue, could not do query"
    except sqlite3.OperationalError, eo:
        print "operational issue, could not do query"
    return rec_exists


def db_insert_podcast(con, mp3_file):
    pf = PodcastFile(mp3_file)
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = (time, pf.basename, pf.subdir, pf.dirname, pf.minutes)
    insert_ok = False
    # context manager, so if successful, then con.commit() is called automatically afterwards
    # con.rollback() is called after the with block finishes with an exception, the
    # exception is still raised and must be caught
    try:
        with con:
            con.execute('insert into podcasts(time, basename, subdir, dirname, minutes) VALUES (?, ?, ?, ?, ?)', row)
            insert_ok = True
    except sqlite3.IntegrityError, ei:
        print "integrity issue, could not do db insert for %s (%s)" % (mp3_file, ei.message)
    except sqlite3.OperationalError, eo:
        print "operational issue, could not do db insert for %s (%s)" % (mp3_file, eo.message)
    return insert_ok


def demo():
    
    db_file = '/Users/ken/Databases/podcasts.db'
    con = get_db_con(db_file)
    
    mp3_file = '/Users/ken/Music/iTunes/iTunes Media/Podcasts/60-Second Tech/Keurig Coffee Drinkers Hack Back.mp3'
    print db_record_exists(con, mp3_file)

def print_usage():
    """print helpful text how to run the program"""
    #FIXME with git keyword sub via following:
    # http://stackoverflow.com/questions/11534655/git-keyword-substitution-like-those-in-subversion
    #print version << BETTER GO AT THIS???
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])
    

def process_data(params):
    """process data with parameters here (should already been checked)"""

    # gather list of podcast files below top_dir
    
   
    # emit start message
    print '%03d candidate files were found under %s' % parameters['top_dir'] 
    
    # get target based on output section of cfg_file using target parameter there
    demo()


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
            nr = NiceResult(process_data, parameters)
            nr.do_work()
            result = nr.get_result()
            if result:
                return 0 # zero for unix success
            else:
                return 2 # non-zero means failed on unix
        
    print_usage()  


if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))
