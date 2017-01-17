#!/usr/bin/env python

from mutagen.mp3 import MP3

def get_mp3_dur_sec(fname):
    audio = MP3(fname)
    return audio.info.length

def demo():
    f = '/tmp/m/song.mp3'
    print get_mp3_dur_sec(f)