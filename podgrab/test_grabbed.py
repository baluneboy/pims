#!/usr/bin/env python

import os
import sys
import sqlite3

_THIS_DIR = os.path.realpath(os.path.dirname(sys.argv[0]))

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

def insert_grabbed_podcast(cur, conn, artist, title):
    row = (artist, title)
    cur.execute('INSERT INTO podcasts(artist, title) VALUES (?, ?)', row)
    conn.commit()

def main():
    artist = 'Big Betty'
    title = 'Chomp Down Betty'
    conn, cur = get_db_connection_cursor()
    insert_grabbed_podcast(cur, conn, artist, title)

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
    n = count_match_artist_title('Big Betty', 'Chomp Down Betty')
    print n
