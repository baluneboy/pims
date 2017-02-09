#!/usr/bin/env python

import os
import sys
import sqlite3
import datetime

from pims.podgrab.podutils import get_mp3_artist_title_genre, get_db_connection_cursor, insert_grabbed_podcast
from pims.podgrab.podutils import add_easy_tags

_THIS_DIR = os.path.realpath(os.path.dirname(sys.argv[0]))


def demo_one():
    artist2 = 'Charlie Chopsticks'
    title2 = 'Beat The Monkey'
    genre2 = 'md5-sum'
    conn2, cur2 = get_db_connection_cursor()
    dtm2 = datetime.datetime.now()
    time2 = dtm2.strftime('%Y-%m-%d %H:%M:%S')
    insert_grabbed_podcast(cur2, conn2, artist2, title2, genre2, time2)    
    

def count_match_artist_title(artist, title, table_name='podcasts', db_name='GrabbedPodcasts.db', db_dir='/Users/ken/dev/programs/python/pims/podgrab'):

    # Connecting to the database file
    conn, c = get_db_connection_cursor(db_dir=db_dir, db_name=db_name)

    # Row(s) that match a certain combo in artist and title columns
    c.execute('SELECT * FROM {tn} WHERE artist="{artstr}" and title="{titstr}"'.format(tn=table_name, artstr=artist, titstr=title))
    list_id_artist_title_tuples = c.fetchall()

    # Closing the connection to the database file
    conn.close()

    return len(list_id_artist_title_tuples)


if __name__ == "__main__":
    #n = count_match_artist_title('Big Betty', 'Chomp Down Betty')
    #print n
    demo_one()
