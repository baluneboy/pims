#!/usr/bin/env python
"""
PAD Headers.
"""

import os
import re
from datetime import timedelta
from interval import Interval
from pims.lib.tools import TransformedDict
from pims.pad.parsenames import match_header_filename
from pims.utils.pimsdateutil import timestr_to_datetime
from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.files.utils import listdir_filename_pattern
from pims.utils.iterabletools import pairwise
from create_header_dict import parse_header # FIXME old [but trusted] code

class PadHeaderDict(TransformedDict):
    """
    Given sensor designation and starting datetime, grab unique header (leader).
    
    Examples
    --------
    
    >>> print PadHeaderDict( '121f03006', datetime(2013, 1, 1))
    PadHeaderDict for 121f03006 at 2013-01-01 00:00:00
    
    >>> print PadHeaderDict( '121f03006', datetime(2012, 12, 31, 0, 5, 0) )._first_header_file
    /misc/yoda/pub/pad/year2012/month12/day31/sams2_accel_121f03006/2012_12_31_00_06_17.985-2012_12_31_01_23_13.189.121f03006.header
    
    >>> print PadHeaderDict( '121f03006', datetime(2012, 12, 31, 23, 57, 0) )._first_header_file
    /misc/yoda/pub/pad/year2012/month12/day31/sams2_accel_121f03006/2012_12_31_00_06_17.985-2012_12_31_01_23_13.189.121f03006.header

    >>> print PadHeaderDict( '121f03006', datetime(2012, 12, 31, 11, 59, 59, 999000) )._first_header_file
    /misc/yoda/pub/pad/year2012/month12/day31/sams2_accel_121f03006/2012_12_31_00_06_17.985-2012_12_31_01_23_13.189.121f03006.header
    
    """
    def __init__(self, sensor, desired_start, pad_dir='/misc/yoda/pub/pad'):
        super(PadHeaderDict, self).__init__()
        self['_sensor'] = sensor
        self['_desired_start'] = desired_start
        self['_pad_dir'] = pad_dir
        self['_header_file'] = self._find_the_right_header_file()
        self._add_hdr_file_fields()
        self._get_location()
        self._get_system()

    def __keytransform__(self, key): return key # FIXME for now, just a dict without key transform

    def _add_hdr_file_fields(self):
        hdr_file_dict = parse_header(self['_header_file'])
        for k,v in hdr_file_dict.iteritems():
            self[k] = v

    def _get_system(self):
        m = re.match( re.compile('(?P<system>sams|mams|mma)(2|es)*_accel'), self['DataType'] )
        if m:
            s = m.group('system')
        else:
            s = self['DataType'].split('_')[0]
        self['System'] = s.upper()
        
    def _get_location(self):
        self['Location'] = self['SensorCoordinateSystem']['comment']
    
    def _find_the_right_header_file(self):
        """
        Get list of header files from day before desired_start through day after, then
        use pairwise (ftw) to check through those header files.  The one we want is in
        the following time range:
         
               O-------------*
        |__1___|     |___2___|
          prev         THIS
           hdr          hdr!
         
        """
        # Get up to 3 days worth of header files
        hdr_files = []
        base_date = self['_desired_start'].date()
        for offset_days in range(-1,2):
            day = base_date + timedelta(days=offset_days)
            try:
                hdr_files += self._get_header_files_for_date(day)
            except:
                pass

        # Iterate pairwise to find the right one to use
        hdr_file = None
        for hdr1, hdr2 in pairwise(hdr_files):
            match1, match2 = [ match_header_filename(f) for f in [hdr1, hdr2] ]
            # Parse each of first/last header to get lower and upper bound of day interval
            stop1_str = match1.group('stop_str')
            stop2_str = match2.group('stop_str')
            # Convert time strings to datetime objects
            t1 = timestr_to_datetime(stop1_str)
            t2 = timestr_to_datetime(stop2_str)
            if self['_desired_start'] > t1 and self['_desired_start'] <= t2:
                #print "*", t1, "to", t2, "<<<", self.desired_start
                hdr_file = hdr2
                break
        return hdr_file

    def __str__(self):
        dots = '.' * len(self.__class__.__name__)
        s = dots
        s += '\n%s' % self.__class__.__name__
        for k,v in self.iteritems():
            if not k.startswith('_'):
                s += '\n%s: %s' % (k, v)
        s += '\n%s' % dots
        return s

    def __repr__(self): return self.__str__()
    
    def _get_header_files_for_date(self, d):
        """Get header files for given sensor on d day."""
        # Components of PAD path pattern
        ymd_subdir = os.path.join( self['_pad_dir'], datetime_to_ymd_path(d) )
        sys_sensor_pattern = '(?P<system>.*)_(accel|rad)_%s\Z' % self['_sensor']
        
        # Verify exactly one subdir matches pattern
        matching_dirs = listdir_filename_pattern(ymd_subdir, sys_sensor_pattern)
        if len(matching_dirs) != 1: return None
        sensor_dir = matching_dirs[0]
        
        # Get header files
        header_pattern = '.*\.%s\.header' % self['_sensor']
        return listdir_filename_pattern(sensor_dir, header_pattern)        

def demo():
    #dtm = datetime(2012, 12, 31, 11, 59, 59, 999000)
    #sensors = ['121f03006', 'hirap', '121f02']
    dtm = datetime(2013, 9, 28, 11, 59, 59, 999000)
    sensors = ['radgse']
    for sensor in sensors:
        print '-' * 15
        ph = PadHeaderDict( sensor, dtm )
        keys = ['System', 'CutoffFreq', 'SampleRate', 'Location']
        for key in keys:
            print key, ph[key]
   
if __name__ == "__main__":
    from datetime import datetime
    import doctest
    if False:
        doctest.testmod()
    else:
        demo()
    pass
    
