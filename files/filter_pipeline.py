#!/usr/bin/env python

import os
import re
import time
from mutagen.mp3 import MP3

class FileFilterPipeline(object):

    def __init__(self, *functions, **kwargs):
        self.functions = functions
        self.data = kwargs.get('data') # makes this callable

    def __call__(self, data):
        return FileFilterPipeline(*self.functions, data=data)

    def __iter__(self):
        data = self.data
        for func in self.functions:
            data = func(data)
        return data
    
    def __str__(self):
        s = self.__class__.__name__
        for f in self.functions:
            s += '\n' + str(f)
        s += '\n-----------------------'
        return s

##############################
# SOME FUNDAMENTAL OPERATORS #
##############################

#---------------------------------------------------
# old Operator #1 is a file-exists function (old, func way...)
def old_file_exists(file_list):
    for f in file_list:
        if os.path.exists(f):
            yield f

# ...better Operator #1 alternative (for consistency) is a callable class
class FileExists(object):
        
    def __call__(self, file_list):
        for f in file_list:
            if os.path.exists(f):
                yield f
                
    def __str__(self):
        return 'is an existing file'

#---------------------------------------------------
# Operator #2 is a big-file callable class
class BigFile(object):
    
    def __init__(self, min_bytes=1024*1024):
        self.min_bytes = min_bytes
        
    def __call__(self, file_list):
        for f in file_list:
            if os.path.getsize(f) >= self.min_bytes:
                yield f

    def __str__(self):
        return 'is a file with at least %d bytes' % self.min_bytes

#---------------------------------------------------    
# old Operator #3 is an extension-checking function
def old_has_ext(file_list, ext='pdf'):
    for f in file_list:
        if f.endswith(ext):
            yield f

# ...better Operator #3 alternative (for consistency) is a callable class
class EndsWith(object):
    
    def __init__(self, ending='mp3'):
        self.ending = ending
        
    def __call__(self, file_list):
        for f in file_list:
            if f.endswith(self.ending):
                yield f
                
    def __str__(self):
        return 'is a file that ends with %s' % self.ending

#---------------------------------------------------
# Operator #5 is a young age callable class
class YoungFile(object):
    
    def __init__(self, max_age_minutes=5):
        self.max_age_minutes = max_age_minutes
        
    def __call__(self, file_list):
        for f in file_list:
            epoch_sec = os.path.getmtime(f)
            file_age_minutes = ( time.time() - epoch_sec ) / 60.0
            if file_age_minutes <= self.max_age_minutes:
                yield f

    def __str__(self):
        return 'is a file that is at most %d minutes old' % self.max_age_minutes

#---------------------------------------------------
# for filter pipeline, an mp3 file callable class
class MinutesLongMp3File(object):

    def __init__(self, min_minutes=0.9):
        self.min_minutes = min_minutes
        
    def __call__(self, file_list):
        for f in file_list:
            if self.get_mp3_duration_minutes(f) >= self.min_minutes:
                yield f

    def __str__(self):
        return 'is a mp3 file with duration of at least %0.1f minutes' % self.min_minutes    

    def get_mp3_duration_minutes(self, fname):
        audio = MP3(fname)
        return audio.info.length / 60.0

#---------------------------------------------------
# a file-missing function
def file_missing(file_list):
    for f in file_list:
        if not os.path.exists(f):
            yield f

def demo():
    
    # Initialize processing pipeline (no file list as input yet)
    ffp = FileFilterPipeline(FileExists(), BigFile(min_bytes=33), EndsWith('mp3'))
    print ffp
    
    # Apply processing pipeline input #1 (now ffp is callable)
    inp1 = ['/tmp/one.mp3', '/tmp/two.not', '/tmp/three.121f03.header', '/tmp/four.txt', '/tmp/five.not']
    for f in ffp(inp1):
        print f
    
if __name__ == "__main__":
    demo()