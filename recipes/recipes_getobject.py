#!/usr/bin/env python

import abc
import os

def getObject(ext, pth, f):
    object = globals()[ext]
    return object(pth,f)

class LogLineMatcher(object):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, abspath, filename):
        self.abspath = abspath
        self.filename = filename
        self.getInfo()

    def getInfo(self):
        self.title = None
        self.time = None
        self.artist = None
        self.album = None
        self.genre = None

    def show(self):
        print '%s\t%s\t%s\t%s\t%s\t"%s"' % (self.__class__.__name__, self.title, self.artist, self.album, self.genre, self.abspath)
    
    @abc.abstractmethod
    def save(self):
        """Save the data object to the output."""
        return

class Rarpd(LogLineMatcher):
    
    def getInfo(self):
        audio = MP4(self.abspath)
        title = audio['\xa9nam'][0]  # track title
        self.title = unicodedata.normalize('NFKD', title).encode('ascii','ignore')
        self.time = -1                    # time
        artist = audio['\xa9ART'][0] # artist
        self.artist = unicodedata.normalize('NFKD', artist).encode('ascii','ignore')
        album = audio['\xa9alb'][0]  # album
        self.album = unicodedata.normalize('NFKD', album).encode('ascii','ignore')
        self.genre = audio['\xa9gen'][0]  # genre
    
    def save(self):
        print "save not implemented yet"
        return

class Newsyslog(LogLineMatcher):

    def save(self):
        print "save not implemented yet"
        return

if __name__ == '__main__':
    topdir = '/Volumes/PORTABRAIN/ken'
    count = 0
    for dirpath, dirnames, filenames in os.walk(topdir):
        for f in filenames:
            if f.lower().endswith('.ds_store'): continue
            count += 1
            print '%04d' % count,
            abspath = os.path.join(dirpath, f)
            ext = os.path.splitext(f)[1].lower().replace('.','')
            try:
                # dynamically dial up instance of the class determined by filename extension!
                log_line_matcher = getObject(ext, abspath, f)
                log_line_matcher.show()
            except KeyError:
                 # no function to process files with extension 'ext', ignore it
                 print 'XXX\tNONE\tNONE\tNONE\tNONE\t"%s"' % abspath
            #else:
            #    #function(abspath, f)
            #    print '---'