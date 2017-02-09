#!/usr/bin/env python

import os
import re
import time
from mutagen.mp3 import MP3
from pims.patterns.probepats import _ROADMAP_PDF_FILENAME_PATTERN


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
            file_bytes = os.path.getsize(f) 
            if file_bytes >= self.min_bytes:
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

# this because some podcasts have long extensions that start with mp3
class ExtensionStartsWith(object):
    
    def __init__(self, begin='mp3'):
        self.begin = begin
        
    def __call__(self, file_list):
        for f in file_list:
            fname, ext = os.path.splitext(f)
            if ext.startswith('.' + self.begin):
                yield f
                
    def __str__(self):
        return 'is a file whose extension starts with %s' % self.begin

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

    def __init__(self, min_minutes=0.9, max_minutes=10.0):
        self.min_minutes = min_minutes
        self.max_minutes = max_minutes
        
    def __call__(self, file_list):
        for f in file_list:
            m = self.get_mp3_duration_minutes(f)
            if m >= self.min_minutes and m < self.max_minutes:
                yield f

    def __str__(self):
        return 'is mp3 file with %0.1f <= duration < %.1f minutes' % (self.min_minutes, self.max_minutes)

    def get_mp3_duration_minutes(self, fname):
        try:
            audio = MP3(fname)
            m = audio.info.length / 60.0
        except Exception, e:
            m = -1.0 # could not get dur minutes
        return m



# for roadmap probe (matches sensor and axis)
class MatchSensorAxRoadmap(object):
    
    def __init__(self, sensor, axis, plot='spg'):
        self.sensor = sensor
        self.axis = axis
        self.plot = plot
        self.regex = re.compile(_ROADMAP_PDF_FILENAME_PATTERN)
        
    def __call__(self, file_list):
        for f in file_list:
            if self.match_pattern(os.path.basename(f)):
                yield f
                
    def __str__(self):
        return 'is a file that matches sensor=%s, axis=%s and plot=%s' % (self.sensor, self.axis, self.plot)
    
    def match_pattern(self, bname):
        match = self.regex.match(bname)
        if match:
            m = match.group
            if (m('sensor') == self.sensor) and (m('axis') == self.axis) and (m('plot') == self.plot):
                return True
        else:
            return False
  
    
#---------------------------------------------------
# a file-missing function
def file_missing(file_list):
    for f in file_list:
        if not os.path.exists(f):
            yield f

def demo():
    
    # Initialize processing pipeline (no file list as input yet)
    #ffp = FileFilterPipeline(BigFile(min_bytes=33), EndsWith('mp3'))
    ffp = FileFilterPipeline(MinutesLongMp3File(min_minutes=0.9, max_minutes=10.1))
    print ffp
    
    # Apply processing pipeline input #1 (now ffp is callable)
    inp1 = ['/tmp/one.mp3', '/tmp/two.not', '/tmp/three.121f03.header', '/tmp/four.txt', '/tmp/five.not']
    for f in ffp(inp1):
        print f

def demo2():
    
    # Initialize processing pipeline (no file list as input yet)
    ffp = FileFilterPipeline(MatchSensorAxRoadmap('121f03', 'x'), BigFile(min_bytes=20))
    print ffp
    
    # Apply processing pipeline input #1 (now ffp is callable)
    fnames = [
        '2017_01_30_00_00_00.000_121f03_spgx_roadmaps500.pdf',
        '2017_01_30_00_00_00.000_121f03ten_spgy_roadmaps500.pdf',
        ]
    inp2 = [ os.path.join('/tmp/x/', f) for f in fnames ]
    for f in ffp(inp2):
        print f  
    
if __name__ == "__main__":
    demo2()