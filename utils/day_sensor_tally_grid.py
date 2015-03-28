#!/usr/bin/env python
"""
Populate wx grid structure with days as rows, sensors as columns, and tallies as cell values.
"""

import os
import re
import wx
import sys
import datetime
from dateutil import parser

# FIXME use pandas DataFrame instead
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from pyvttbl import DataFrame

from datetime_ranger import DateRange
from pims.utils.pimsdateutil import timestr_to_datetime
from pims.gui.tally_grid import TallyFrame, CheapPadHoursInputGrid, TallyOutputGrid, run_main_loop
from pims.files.utils import filter_filenames, parse_roadmap_filename
from pims.patterns.dailyproducts import _BATCHROADMAPS_PATTERN, _PADHEADERFILES_PATTERN

#class OLD_RoadmapGridWorker(object):
#    """A grid with days as rows, sensors as columns, & file count as cell values."""    
#
#    def __init__(self, date_range,
#                 pattern=_BATCHROADMAPS_PATTERN,
#                 basepath='/misc/yoda/www/plots/batch',
#                 update_sec=30):
#        self.date_range = date_range
#        self.pattern = pattern
#        self.basepath = basepath
#        self.update_sec = update_sec
#        self.title = self.__class__.__name__ + ' for "%s"' % self.pattern
#        
#    def do_data_frame_insert(self, d, f):
#        """Parse file basename to get dict and do data frame insert."""
#        # handle degenerate case of no matching files
#        if not f:
#            self.data_frame.insert({'date':d, 'hour':None, 'sensor':None, 'abbrev':None, 'bname':None, 'fname':None})
#            return
#        # otherwise, parse file basename via pattern and get dict to insert
#        m = re.match(self.pattern, f)
#        if m:
#            start = timestr_to_datetime(m.group('start'))
#            sensor = m.group('sensor')
#            abbrev = m.group('abbrev')
#        else:
#            start, sensor, abbrev = None, None, None
#        # now insert the dict TWSS
#        self.data_frame.insert({
#            'date':start.date(),
#            'hour':start.hour,
#            'sensor':sensor,
#            'abbrev':abbrev,
#            'bname':os.path.basename(f),
#            'fname':f
#            })
#
#    def get_grid(self):
#        """Fill data frame, pivot, and show grid."""
#        self.data_frame = DataFrame()
#        self.fill_data_frame()
#        
#        # use default pivot parameters
#        pt = self.get_pivot_table(val='abbrev', rows=['date'], cols=['sensor'], aggregate='count')
#        
#        # turn pivot table into row_labels, column_labels, and rows to show
#        self.row_labels = [ str(i[0][1]) for i in pt.rnames]     # days as row labels
#        self.column_labels = [ str(i[0][1]) for i in pt.cnames]  # sensors as column labels
#        self.rows = [ i for i in pt ]                            # count roadmap files for cell values
#
#    def pivot_table_insert_day_entries(self, d):
#        """Walk ymd path and insert regex matches of filename pattern into data frame."""
#        dirpath = os.path.join( self.basepath, d.strftime('year%Y/month%m/day%d') )
#        fullfile_pattern = os.path.join(dirpath, self.pattern)
#        bool_got_match = False
#        for f in filter_filenames(dirpath, re.compile(fullfile_pattern).match):
#            self.do_data_frame_insert(d, f)
#            bool_got_match = True
#        if not bool_got_match:
#            # do not skip any days/rows, insert dummy dict for dfin
#            self.do_data_frame_insert(d, None)
#    
#    def fill_data_frame(self):
#        """Populate data frame day-by-day."""
#        d = self.date_range.start
#        while d <= self.date_range.stop:
#            self.pivot_table_insert_day_entries(d)
#            d += datetime.timedelta(days=1)
#    
#    def get_pivot_table(self, val='abbrev', rows=['date'], cols=['sensor'], aggregate='count'):
#        """This is where we pivot."""
#        return self.data_frame.pivot(val, rows, cols, aggregate)
#    
#    def attach(self, other):
#        """Attach other DataFrame to this one (both must have the same columns)"""
#        # do minimal checking
#        if not isinstance(other, RoadmapGridWorker):
#            raise TypeError('second argument must be a RoadmapGridWorker')
#        # perform attachment
#        self.data_frame.attach(other.data_frame)
#
#    def __str__(self): return 'This is a %s for %s.\n' % (self.title, self.date_range)
#
#    def __repr__(self): return self.__str__()

class RoadmapGridWorker(object):
    """A grid with days as rows, sensors as columns, & file count as cell values."""    

    def __init__(self, input_grid):
        input_grid = input_grid(-1)
        inputs = input_grid.get_inputs()
        self.date_range = inputs['date_range']
        self.pattern = inputs['pattern']
        self.basepath = inputs['basepath']
        self.update_sec = inputs['update_sec']
        self.title = self.__class__.__name__ + ' for "%s"' % self.pattern
        
    def do_data_frame_insert(self, d, f):
        """Parse file basename to get dict and do data frame insert."""
        # handle degenerate case of no matching files
        if not f:
            self.data_frame.insert({'date':d, 'hour':None, 'sensor':None, 'abbrev':None, 'bname':None, 'fname':None})
            return
        # otherwise, parse file basename via pattern and get dict to insert
        m = re.match(self.pattern, f)
        if m:
            start = timestr_to_datetime(m.group('start'))
            sensor = m.group('sensor')
            abbrev = m.group('abbrev')
        else:
            start, sensor, abbrev = None, None, None
        # now insert the dict TWSS
        self.data_frame.insert({
            'date':start.date(),
            'hour':start.hour,
            'sensor':sensor,
            'abbrev':abbrev,
            'bname':os.path.basename(f),
            'fname':f
            })

    def get_grid(self):
        """Fill data frame, pivot, and show grid."""
        self.data_frame = DataFrame()
        self.fill_data_frame()
        
        # use default pivot parameters
        pt = self.get_pivot_table(val='abbrev', rows=['date'], cols=['sensor'], aggregate='count')
        
        # turn pivot table into row_labels, column_labels, and rows to show
        self.row_labels = [ str(i[0][1]) for i in pt.rnames]     # days as row labels
        self.column_labels = [ str(i[0][1]) for i in pt.cnames]  # sensors as column labels
        self.rows = [ i for i in pt ]                            # count roadmap files for cell values

    def pivot_table_insert_day_entries(self, d):
        """Walk ymd path and insert regex matches of filename pattern into data frame."""
        dirpath = os.path.join( self.basepath, d.strftime('year%Y/month%m/day%d') )
        fullfile_pattern = os.path.join(dirpath, self.pattern)
        bool_got_match = False
        for f in filter_filenames(dirpath, re.compile(fullfile_pattern).match):
            self.do_data_frame_insert(d, f)
            bool_got_match = True
        if not bool_got_match:
            # do not skip any days/rows, insert dummy dict for dfin
            self.do_data_frame_insert(d, None)
    
    def fill_data_frame(self):
        """Populate data frame day-by-day."""
        d = self.date_range.start
        while d <= self.date_range.stop:
            self.pivot_table_insert_day_entries(d)
            d += datetime.timedelta(days=1)
    
    def get_pivot_table(self, val='abbrev', rows=['date'], cols=['sensor'], aggregate='count'):
        """This is where we pivot."""
        return self.data_frame.pivot(val, rows, cols, aggregate)
    
    def attach(self, other):
        """Attach other DataFrame to this one (both must have the same columns)"""
        # do minimal checking
        if not isinstance(other, RoadmapGridWorker):
            raise TypeError('second argument must be a RoadmapGridWorker')
        # perform attachment
        self.data_frame.attach(other.data_frame)

    def __str__(self): return 'This is a %s for %s.\n' % (self.title, self.date_range)

    def __repr__(self): return self.__str__()

class CheapPadHoursGridWorker(RoadmapGridWorker):
    """A grid with days as rows, sensors as columns, & "cheap" PAD hours as cell values."""    

    def __init__(self, date_range,
                 pattern=_PADHEADERFILES_PATTERN,
                 basepath='/misc/yoda/pub/pad',
                 update_sec=30):        
        super(CheapPadHoursGridWorker, self).__init__(
            date_range,
            pattern=pattern,
            basepath=basepath,
            update_sec=update_sec)

    def do_data_frame_insert(self, d, f):
        """Parse file basename to get dict and do data frame insert."""
        # handle degenerate case of no matching files
        if not f:
            self.data_frame.insert({'date':d, 'span_hours':0.0, 'sensor':None, 'bname':None, 'fname':None})
            return
        # otherwise, parse file basename via pattern and get dict to insert
        m = re.match(self.pattern, f)
        if m:
            # a different pattern emerges here relative to base class
            start = timestr_to_datetime(m.group('start'))
            stop = timestr_to_datetime(m.group('stop'))
            span_hours = (stop - start).seconds / 3600.0
            sensor = m.group('sensor')
        else:
            start, stop, span_hours, sensor = None, None, None, None
        # now insert the dict TWSS
        self.data_frame.insert({
            'date':start.date(),
            'span_hours':span_hours,
            'sensor':sensor,
            'bname':os.path.basename(f),
            'fname':f
            })

    def get_grid(self):
        """Fill data frame, pivot, and show grid."""
        self.data_frame = DataFrame()
        self.fill_data_frame()
        
        # use default pivot parameters
        pt = self.get_pivot_table(val='span_hours', rows=['date'], cols=['sensor'], aggregate='sum')
        
        # turn pivot table into row_labels, column_labels, and rows to show
        self.row_labels = [ str(i[0][1]) for i in pt.rnames]     # days as row labels
        self.column_labels = [ str(i[0][1]) for i in pt.cnames]  # sensors as column labels
        rows = [ i for i in pt ]                                 # approx. pad hours for cell values
        
        # replace None's with zero's in the rows
        self.rows = [ [0 if not x else x for x in r] for r in rows ]        

if __name__ == "__main__":
    #import doctest
    #doctest.testmod(verbose=True)

    ## get range of days (dates)
    #d1 = parser.parse('2013-09-28').date()
    #d2 = parser.parse('2013-10-02').date()
    #date_range = DateRange(start=d1, stop=d2)
    #
    ## use special pattern
    #pth_field = "(?P<ymdpath>.*)"
    #date_field = "(?P<start>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})"
    #sensor_field = "_(?P<sensor>.*one)" # sensor field ends with "one"
    #abbrev_field = "_(?P<abbrev>.*)"
    #suffix_field = "_roadmaps(?P<rate>.*)\.pdf\Z"
    #pattern = pth_field + date_field + sensor_field + abbrev_field + suffix_field
    #
    #basepath = '/misc/yoda/www/plots/batch'
    #update_sec = 5

    #roadmaps_count_grid = RoadmapGridWorker(date_range,
    #                                        pattern=pattern,
    #                                        basepath=basepath,
    #                                        update_sec=update_sec)
    
    input_grid = CheapPadHoursInputGrid
    grid_worker = RoadmapGridWorker
    run_main_loop(input_grid, grid_worker)
    
    raise SystemExit

#------------------------------------

    #d1 = parser.parse('2013-10-18').date()
    #d2 = datetime.date.today()-datetime.timedelta(days=2)

#------------------------------------
    
    d1 = parser.parse('2013-01-01').date()
    d2 = parser.parse('2013-01-04').date()
    #d2 = datetime.date.today()-datetime.timedelta(days=2)
    date_range = DateRange(start=d1, stop=d2)
    pad_hours_grid = CheapPadHoursGridWorker(date_range, update_sec=4)
    run_main_loop(pad_hours_grid, exclude_columns=['None'])
