#!/usr/bin/env python

import os
import re
import time
import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from mutagen.mp3 import MP3

from pims.patterns.probepats import _ROADMAP_PDF_FILENAME_PATTERN, _QUASISTEADY_ESTIMATE_PDF_PATTERN
from pims.patterns.dailyproducts import _PADHEADERFILES_PATTERN
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop, otomat_fullfilestr_to_start_stop #, foscam_fullfilestr_to_datetime
from pims.utils.pimsdateutil import datetime_to_roadmap_fullstub, datetime_to_ymd_path
from pims.files.padgrep import get_hdr_dict_fs_fc_loc_ssa, get_hdr_dict_fs_fc_sensor


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
    
    def __init__(self, min_bytes=1024*1024):  # default min is 1 MB
        self.min_bytes = min_bytes
        
    def __call__(self, file_list):
        for f in file_list:
            file_bytes = os.path.getsize(f) 
            if file_bytes >= self.min_bytes:
                yield f

    def __str__(self):
        return 'is a file with at least %d bytes' % self.min_bytes

#---------------------------------------------------
# Operator is a too-small-file callable class
class TooSmallFile(object):
    
    def __init__(self, max_bytes=1024*500):
        self.max_bytes = max_bytes
        
    def __call__(self, file_list):
        for f in file_list:
            file_bytes = os.path.getsize(f) 
            if file_bytes <= self.max_bytes:
                yield f

    def __str__(self):
        return 'is a file with at most %d bytes' % self.max_bytes

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
        except Exception as e:
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
        except Exception as e:
            print('could not parse date from %s' % fullname)
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
        return 'is a roadmap file that matches sensor=%s, axis=%s and plot=%s' % (self.sensor, self.axis, self.plot)
    
    def match_pattern(self, bname):
        match = self.regex.match(bname)
        if match:
            m = match.group
            if (m('sensor') == self.sensor) and (m('axis') == self.axis) and (m('plot') == self.plot):
                return True
        else:
            return False

# for quasi-steady estimate gvt3 roadmap for ZBOT modeling
class MatchZbotQuasiSteadyEstimate(object):
    
    def __init__(self):
        self.regex = re.compile(_QUASISTEADY_ESTIMATE_PDF_PATTERN)
        
    def __call__(self, file_list):
        for f in file_list:
            if self.match_pattern(os.path.basename(f)):
                yield f
                
    def __str__(self):
        return 'is a quasi-steady estimate file for ZBOT modeling'
    
    def match_pattern(self, bname):
        match = self.regex.match(bname)
        if match:
            return True
        else:
            return False

# for PAD probe (matches sensor)
class MatchSensorPad(object):
    
    def __init__(self, sensor):
        self.sensor = sensor
        self.regex = re.compile(_PADHEADERFILES_PATTERN)
        
    def __call__(self, file_list):
        for f in file_list:
            if self.match_pattern(f):
                yield f
                
    def __str__(self):
        return 'is a PAD file that matches sensor=%s' % (self.sensor)
    
    def match_pattern(self, bname):
        match = self.regex.match(bname)
        if match:
            m = match.group
            if (m('sensor') == self.sensor):
                return True
        else:
            return False

# for PAD to match sample rate, cutoff freq and SSA coordinates
class HeaderMatchesRateCutoffLocSsaPad(object):
# <?xml version="1.0" encoding="US-ASCII"?>
# <sams2_accel>
# 	<SensorID>121f04</SensorID>
# 	<TimeZero>2018_06_13_23_56_43.640</TimeZero>
# 	<Gain>10.0</Gain>
# 	<SampleRate>500.0</SampleRate>
# 	<CutoffFreq>200.0</CutoffFreq>
# 	<GData format="binary 32 bit IEEE float little endian" file="2018_06_13_23_56_43.640+2018_06_14_00_01_37.643.121f04"/>
# 	<BiasCoeff x="1.23" y="4.46" z="7.89"/>
# 	<SensorCoordinateSystem name="121f04" r="180.0" p="0.0" w="-90.0" x="156.6" y="-46.08" z="207.32" comment="LAB1P2, ER7, Cold Atom Lab Front Panel" time="2018_05_31_00_00_00.000"/>
# 	<DataCoordinateSystem name="SSAnalysis" r="0.0" p="0.0" w="0.0" x="0.0" y="0.0" z="0.0" comment="S0, Geom. Ctr. ITA" time="2001_05_01_00_00_00.000"/>
# 	<DataQualityMeasure>temperature+gain+axial-mis-alignment, No temperature compensation</DataQualityMeasure>
# 	<ISSConfiguration>Increment:  28, Flight: ULF7</ISSConfiguration>
# 	<ScaleFactor x="1.0" y="1.0" z="1.0"/>
# </sams2_accel>
    
    def __init__(self, fs, fc, loc, coord_name='SSAnalysis'):
        self.template = {
            'DataCoordinateSystem_name': coord_name,
            'SensorCoordinateSystem_comment': loc,  # note that the 'comment' field contains location info
            'SampleRate': fs,
            'CutoffFreq': fc
            }
        
    def __call__(self, file_list):
        for f in file_list:
            if not f.endswith('.header'):
                hdr_file = f + '.header'
            else:
                hdr_file = f
            header_values = get_hdr_dict_fs_fc_loc_ssa(hdr_file)
            if header_values == self.template:
                    yield f
                
    def __str__(self):
        return 'is a PAD file with fs = %.3f, fc = %.3f, coord_sys = %s, loc = %s' % (self.template['SampleRate'],
                                                                                  self.template['CutoffFreq'],
                                                                                  self.template['DataCoordinateSystem_name'],
                                                                                  self.template['SensorCoordinateSystem_comment'],
                                                                                  )

# for PAD to match SensorID, SampleRate and CutoffFreq
class HeaderMatchesSensorRateCutoffPad(object):
# <?xml version="1.0" encoding="US-ASCII"?>
# <sams2_accel>
# 	<SensorID>121f04</SensorID>
# 	<TimeZero>2018_06_13_23_56_43.640</TimeZero>
# 	<Gain>10.0</Gain>
# 	<SampleRate>500.0</SampleRate>
# 	<CutoffFreq>200.0</CutoffFreq>
# 	<GData format="binary 32 bit IEEE float little endian" file="2018_06_13_23_56_43.640+2018_06_14_00_01_37.643.121f04"/>
# 	<BiasCoeff x="1.23" y="4.46" z="7.89"/>
# 	<SensorCoordinateSystem name="121f04" r="180.0" p="0.0" w="-90.0" x="156.6" y="-46.08" z="207.32" comment="LAB1P2, ER7, Cold Atom Lab Front Panel" time="2018_05_31_00_00_00.000"/>
# 	<DataCoordinateSystem name="SSAnalysis" r="0.0" p="0.0" w="0.0" x="0.0" y="0.0" z="0.0" comment="S0, Geom. Ctr. ITA" time="2001_05_01_00_00_00.000"/>
# 	<DataQualityMeasure>temperature+gain+axial-mis-alignment, No temperature compensation</DataQualityMeasure>
# 	<ISSConfiguration>Increment:  28, Flight: ULF7</ISSConfiguration>
# 	<ScaleFactor x="1.0" y="1.0" z="1.0"/>
# </sams2_accel>
    
    def __init__(self, sensor, fs, fc):
        self.template = {
            'SensorID': sensor,
            'SampleRate': fs,
            'CutoffFreq': fc
            }
        
    def __call__(self, file_list):
        for f in file_list:
            if not f.endswith('.header'):
                hdr_file = f + '.header'
            else:
                hdr_file = f
            header_values = get_hdr_dict_fs_fc_sensor(hdr_file)
            if header_values == self.template:
                    yield f
                
    def __str__(self):
        return 'is a PAD file with fs = %.3f, fc = %.3f, sensor = %s' % (self.template['SampleRate'],
                                                                                  self.template['CutoffFreq'],
                                                                                  self.template['SensorID'],
                                                                                  )

# FIXME this is sloppy way to get true file duration in minutes (crude but what we go with for now)
class MinDurMinutesPad(object):
    
    def __init__(self, min_minutes=5.0):
        self.min_minutes = min_minutes
        
    def __call__(self, file_list):
        for f in file_list:
            fstart, fstop = pad_fullfilestr_to_start_stop(f)
            num_minutes = (fstop - fstart).total_seconds() / 60.0
            if num_minutes >= self.min_minutes:
                # print 'ok', f, num_minutes
                yield f
            # else:
            #     print 'no', f, num_minutes
                
    def __str__(self):
        return 'is a PAD file longer in duration than %.f minutes' % (self.min_minutes)


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


class OtoDaySensorHours(object):
    """return generator for OTO mat files whose names match given sensor, start/stop hour range(s)"""

    def __init__(self, day, sensor, hours):
        self.sensor = sensor
        self.day = parse(day)
        self.hours = hours
        
    def __call__(self, file_list):
        for f in file_list:
            sensor = f.split('.')[-2]
            if not self.sensor == sensor:
                return
            fstart, fstop = otomat_fullfilestr_to_start_stop(f)
            for h1, h2 in self.hours:
                start = self.day + relativedelta(hours=h1)
                stop = self.day + relativedelta(hours=h2)
                if fstart > start and fstop < stop:
                    yield f
                
    def __str__(self):
        return 'is an OTO file for sensor with fname start/stop hour in given list of hour ranges'


class PadDaySensorHours(object):
    """return generator for PAD files whose names match given sensor, start/stop hour range(s)"""

    def __init__(self, day, sensor, hours):  # e.g. hours = [(0,4), (22,23)]
        self.sensor = sensor
        self.day = parse(day)
        self.hours = hours

    def __call__(self, file_list):
        for f in file_list:
            sensor = f.split('.')[-1]
            if not self.sensor == sensor:
                return
            fstart, fstop = pad_fullfilestr_to_start_stop(f)
            for h1, h2 in self.hours:
                start = self.day + relativedelta(hours=h1)
                stop = self.day + relativedelta(hours=h2)
                if fstart > start and fstop < stop:
                    yield f

    def __str__(self):
        return 'is PAD file for sensor with fname start/stop hour in given list of hour ranges'


#class DateRangeStateFoscamFile(object):
#    
#    def __init__(self, start, stop, morning=True, state=None):
#        self.start = start
#        self.stop = stop
#        self.morning = morning
#        self.state = state
#        
#    def __call__(self, file_list):
#        for f in file_list:
#            fdtm, fstate = parse_foscam_fullfilestr(f)
#            keep = False
#            state_matches = False
#            if self.state:
#                state_matches = self.state == fstate
#            else:
#                state_matches = True
#            if fdtm:  # not None
#                if state_matches:
#                    if fdtm.date() >= self.start and fdtm.date() <= self.stop:
#                        if self.morning:
#                            if fdtm.hour < 12:
#                                keep = True
#                        else:
#                            keep = True
#            if keep:
#                yield f
#                
#    def __str__(self):
#        return 'is a Foscam image file with %s < fname date < %s' % (self.start, self.stop)
    
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
    print(ffp)
    
    # Apply processing pipeline input #1 (now ffp is callable)
    inp1 = ['/Users/ken/Music/iTunes/iTunes Media/Podcasts/The Math Dude Quick and Dirty Tips to Make Math Easier/227 227 TMD Polygon Puzzle_ How Many Degrees Are In a Polygon_.mp3',
            "/Users/ken/Music/iTunes/iTunes Media/Podcasts/Merriam-Webster's Word of the Day/peradventure.mp3",
            '/tmp/three.121f03.header',
            '/tmp/four.txt',
            '/tmp/five.not']
    for f in ffp(inp1):
        print(f)

def demo3():
    from datetime import datetime
    
    # Initialize processing pipeline (no file list as input yet)
    ffp = FileFilterPipeline(EeStatsFile(start_date=datetime(2017,1,31).date(), end_date=datetime(2017,2,1).date()))
    print(ffp)
    
    # Apply processing pipeline input #1 (now ffp is callable)
    inp1 = ['/misc/yoda/www/plots/user/sheep/ee_stats_2017-01-29.pkl',
            '/misc/yoda/www/plots/user/sheep/ee_stats_2017-01-30.pkl',
            '/misc/yoda/www/plots/user/sheep/ee_stats_2017-01-31.pkl',
            '/misc/yoda/www/plots/user/sheep/ee_stats_2017-02-01.pkl']
    for f in ffp(inp1):
        print(f)

    
def demo2():
    
    # Initialize processing pipeline (no file list as input yet)
    ffp = FileFilterPipeline(MatchSensorAxRoadmap('121f03', 'x'), BigFile(min_bytes=20))
    print(ffp)
    
    # Apply processing pipeline input #1 (now ffp is callable)
    fnames = [
        '2017_01_30_00_00_00.000_121f03_spgx_roadmaps500.pdf',
        '2017_01_30_00_00_00.000_121f03ten_spgy_roadmaps500.pdf',
        ]
    inp2 = [ os.path.join('/tmp/x/', f) for f in fnames ]
    for f in ffp(inp2):
        print(f)
    
    
def demo_gateway2():
    
    import glob
    
    # Initialize processing pipeline (no file list as input yet)
    day = datetime.datetime(2016,1,22)
    hours = [(0,4), (22,23)]
    ffp = FileFilterPipeline(OtoDaySensorHours(day, hours))
    print(ffp)
    
    # Apply processing pipeline input #1 (now ffp is callable)
    wild_path = '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/day22/sams2_accel_121f03/*mat'
    filenames = glob.glob(wild_path)
    for f in ffp(filenames):
        print(f) 
   
   
def demo_gateway():
    
    import glob
    
    # Initialize processing pipeline (no file list as input yet)
    ffp = FileFilterPipeline(HeaderMatchesSensorRateCutoffPad('121f03', 500, 200), MinDurMinutesPad(min_minutes=5.0))
    print(ffp)
    
    # Apply processing pipeline input #1 (now ffp is callable)
    #wild_path = '/misc/yoda/pub/pad/year2018/month01/day02/sams2_accel_121f03/*header'
    wild_path = '/tmp/trashpad/year2018/month01/day02/sams2_accel_121f03/*header'
    filenames = glob.glob(wild_path)
    for f in ffp(filenames):
        print(f)    
    

def show_missing_roadmaps(end, start=None, sensor='121f03', axis='s', base_path='/misc/yoda/www/plots/batch'):
    import glob
    import pandas as pd
    
    if start is None:
        start = parse(end) - datetime.timedelta(days=7)
    for d in pd.date_range(start, end):
        print(d.date(), sensor, 'spg' + axis, " > ", end=' ')
        day_dir = os.path.dirname(datetime_to_roadmap_fullstub(d))
    
        # initialize processing pipeline (no file list as input yet)
        ffp = FileFilterPipeline(MatchSensorAxRoadmap(sensor, axis))
        
        # apply processing pipeline (now ffp is callable)
        # /misc/yoda/www/plots/batch/year2018/month01/day25/2018_01_25_00_00_00.000_121f04ten_pcss_roadmaps500.pdf
        day_files = glob.glob(os.path.join(day_dir, '*_%s_*roadmaps*.pdf' % sensor))
        if len(day_files) == 0:
            print('MISSING---', end=' ')
        else:
            for f in ffp(day_files):
                hh = f.split('_')[3]
                print(hh, end=' ')
        print('')


def demo_fetch_big_pad_files(start, end, sensor, fs, fc, hours):
    import glob
    import pandas as pd

    print(start, end)
    print(sensor, fs, fc)
    print(hours)

    for d in pd.date_range(start, end):
        print(d.date(), sensor, " > ", end=' ')
        day_dir = datetime_to_ymd_path(d, base_dir='d:/pad')

        # initialize processing pipeline (no file list as input yet)
        ffp = FileFilterPipeline(HeaderMatchesSensorRateCutoffPad(sensor, fs, fc),
                                 PadDaySensorHours(d.strftime('%Y-%m-%d'), sensor, hours),
                                 BigFile(min_bytes=2*1024*1024))

        # apply processing pipeline (now ffp is callable)
        glob_pat = os.path.join(day_dir, '*_*_%s/*.%s' % (sensor, sensor))
        day_files = glob.glob(glob_pat)
        if len(day_files) == 0:
            print('MISSING---', end=' ')
        else:
            # for f in ffp(day_files):
            #     hh = f.split('_')[3]
            #     print hh,
            keep_files = list(ffp(day_files))
            print(len(keep_files), 'files', keep_files, end=' ')
        print('')


if __name__ == "__main__":

    #sensors = [ '121f0%s' % str(s) for s in [2, 3, 4, 5, 8]]
    #for sensor in sensors:
    #    show_missing_roadmaps('2018-01-25', start='2018-01-20', sensor=sensor)

    # demo_gateway2()

    # SLEEP FILES ONLY
    demo_fetch_big_pad_files('2020-04-01', '2020-04-07', '121f03006', 142.0, 6.0, [(0, 4)])
