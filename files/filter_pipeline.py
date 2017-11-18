#!/usr/bin/env python

import os
import re
import time
import datetime
from dateutil.parser import parse
from mutagen.mp3 import MP3
from pims.patterns.probepats import _ROADMAP_PDF_FILENAME_PATTERN
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop, foscam_fullfilestr_to_datetime

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

class EeStatsFile(object):
    """an ee_stats file for plotting EE HS"""

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        
    def __call__(self, file_list):
        for f in file_list:
            if self.matches_regex(f):
                d = self.get_file_date(f)
                if d >= self.start_date and d <= self.end_date:
                    yield f

    def __str__(self):
        return 'is ee_stats file with %s <= date <= %s' % (self.start_date, self.end_date)

    def matches_regex(self, fullname):
        fullfile_pattern = r'.*%see_stats_.*\pkl' % os.path.sep
        if re.compile(fullfile_pattern).match(fullname):
            return True
        return False

    def get_file_date(self, fullname):
        try:
            # we are splitting for basenames like ee_stats_2017-01-02.pkl
            d = parse(os.path.basename(fullname).split('_')[-1].split('.')[0]).date()
        except Exception, e:
            print 'could not parse date from %s' % fullname
            d = 0

        return d

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

# for example, used to quarantine PAD files with filename's GMT stop time greater than start & GMT start time less than stop
class DateRangePadFile(object):
    
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop
        
    def __call__(self, file_list):
        for f in file_list:
            fstart, fstop = pad_fullfilestr_to_start_stop(f)
            if fstop > self.start and fstart < self.stop:
                yield f
                
    def __str__(self):
        return 'is a PAD file with fname stop > %s and fname start < %s' % (self.start, self.stop)

class DateRangeFoscamFile(object):
    
    def __init__(self, start, stop, morning=True):
        self.start = start
        self.stop = stop
        self.morning = morning
        
    def __call__(self, file_list):
        for f in file_list:
            dtm = foscam_fullfilestr_to_datetime(f)
            if dtm and dtm.date() >= self.start and dtm.date() <= self.stop:
                if dtm.hour < 12: 
                    yield f
                
    def __str__(self):
        return 'is a Foscam image file with %s < fname date < %s' % (self.start, self.stop)
    
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
    inp1 = ['/Users/ken/Music/iTunes/iTunes Media/Podcasts/The Math Dude Quick and Dirty Tips to Make Math Easier/227 227 TMD Polygon Puzzle_ How Many Degrees Are In a Polygon_.mp3',
            "/Users/ken/Music/iTunes/iTunes Media/Podcasts/Merriam-Webster's Word of the Day/peradventure.mp3",
            '/tmp/three.121f03.header',
            '/tmp/four.txt',
            '/tmp/five.not']
    for f in ffp(inp1):
        print f

def demo3():
    from datetime import datetime
    
    # Initialize processing pipeline (no file list as input yet)
    ffp = FileFilterPipeline(EeStatsFile(start_date=datetime(2017,1,31).date(), end_date=datetime(2017,2,1).date()))
    print ffp
    
    # Apply processing pipeline input #1 (now ffp is callable)
    inp1 = ['/misc/yoda/www/plots/user/sheep/ee_stats_2017-01-29.pkl',
            '/misc/yoda/www/plots/user/sheep/ee_stats_2017-01-30.pkl',
            '/misc/yoda/www/plots/user/sheep/ee_stats_2017-01-31.pkl',
            '/misc/yoda/www/plots/user/sheep/ee_stats_2017-02-01.pkl']
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
    demo3()