#!/usr/bin/env python

import os
import sys
import sqlite3

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3

from pims.files.utils import get_md5

_THIS_DIR = os.path.realpath(os.path.dirname(sys.argv[0]))


def count_match_artist_title(artist, title, table_name='podcasts', db_name='GrabbedPodcasts.db', db_dir='/Users/ken/dev/programs/python/pims/podgrab'):

    # Connecting to the database file
    conn, c = get_db_connection_cursor(db_dir=db_dir, db_name=db_name)

    # Row(s) that match a certain combo in artist and title columns
    c.execute('SELECT * FROM {tn} WHERE artist="{artstr}" and title="{titstr}"'.format(tn=table_name, artstr=artist, titstr=title))
    list_id_artist_title_tuples = c.fetchall()

    # Closing the connection to the database file
    conn.close()

    return len(list_id_artist_title_tuples)


#FIXME for robustness, maybe artist is subdir in podcasts, title is title, and genre is md5sum
def add_easy_tags(mp3_file, artist=None, title=None, genre=None):
    """this adds artist, title and genre tags if needed"""
    md5sum = get_md5(mp3_file)
    try:
        # if we can get common tags (like artist and title, so be it)
        meta = EasyID3(mp3_file)

    except mutagen.id3.ID3NoHeaderError:
        # otherwise, let's shove our own in there
        meta = mutagen.File(mp3_file, easy=True)
        meta.add_tags()
        
        if title:
            meta['title'] = title
        else:
            meta['title'] = os.path.basename(mp3_file)[:8]
        
        if artist:
            meta['artist'] = artist
        else:
            meta['artist'] = os.path.basename(os.path.dirname(mp3_file))

    
    # no matter what, we are stealing the genre to hold md5 sum...
    if genre:
        # ...unless this function is called with specified genre
        meta['genre'] = genre
    else:
        meta['genre'] = 'md5-' + md5sum
    
    meta.save()


#---------------------------------------------------
# for filter pipeline, a file callable class
class NotInGrabbedPodcastsDb(object):

    def __init__(self, table_name='podcasts', db_name='GrabbedPodcasts.db', db_dir='/Users/ken/dev/programs/python/pims/podgrab'):
        self.table_name = table_name
        self.db_name = db_name
        self.db_dir = db_dir
        
    def __call__(self, file_list):
        for f in file_list:
            artist, title = get_mp3_artist_title(f)
            num = count_match_artist_title(artist, title, table_name=self.table_name, db_name=self.db_name, db_dir=self.db_dir)
            if num == 0:
                yield f

    def __str__(self):
        return 'is a file with (artist, title) not already in %s' % self.db_name


def does_db_exist(db_dir=_THIS_DIR, db_name='GrabbedPodcasts.db'):
    if os.path.exists(db_dir + os.sep + db_name):
        return True
    else:
        return False

    
def connect_db(db_dir=_THIS_DIR, db_name='GrabbedPodcasts.db'):
    conn = sqlite3.connect(db_dir + os.sep + db_name)
    return conn


def get_db_connection_cursor(db_dir=_THIS_DIR, db_name='GrabbedPodcasts.db'):
    if does_db_exist(db_dir, db_name=db_name):
        connection = connect_db(db_dir, db_name=db_name)
        if not connection:
            error_string = "Could not connect to %s database file!" % db_name
            connection, cursor = None, None
        else:
            cursor = connection.cursor()
    return connection, cursor


def insert_grabbed_podcast(cur, conn, artist, title, genre, time):
    row = (artist, title, genre, time)
    cur.execute('INSERT INTO podcasts(artist, title, genre, time) VALUES (?, ?, ?, ?)', row)
    conn.commit()


def get_mp3_dur_sec(fname):
    audio = MP3(fname)
    return audio.info.length


def get_mp3_artist_title_genre(path):
    """"""
    audio = ID3(path)
    #print "Release Year: %s" % audio["TDRC"].text[0]
    artist = "%s" % audio['TPE1'].text[0]
    title = "%s" % audio['TIT2'].text[0]
    genre = "%s" % audio['TCON'].text[0]
    return artist, title, genre


def demo():
    f = '/Volumes/serverHD2/data/podcasts/Hourly-News-Summary/20170113newscast040632.mp3orgId1d300p500005story50.mp3'
    f = '/Volumes/serverHD2/data/podcasts/Scientific-American-Podcast-60-Second-Science/20170118podcast.mp3fileIdC73B6AFF-1C3E-48D1-927F01ED445F.mp3'
    
    artist, title, genre = get_mp3_artist_title_genre(f)
    print artist
    print title
    print genre
    
    #add_easy_tags(f, artist=None, title=None, genre=None)   


if __name__ == '__main__':
    demo()