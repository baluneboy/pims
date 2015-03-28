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
from pims.files.utils import filter_filenames, parse_roadmap_filename
from pims.patterns.dailyproducts import _BATCHROADMAPS_PATTERN, _PADHEADERFILES_PATTERN
from pims.gui.tally_grid import RoadmapsInputGrid, CheapPadHoursInputGrid, RoadmapsOutputGrid, CheapPadHoursOutputGrid
from pims.gui.iogrids import MainFrame

class RoadmapsGridWorker(object):
    """A grid with days as rows, sensors as columns, & file count as cell values."""    

    def __init__(self, inputs):
        """Initialize with inputs dict."""
        for key, val in inputs.iteritems():
            setattr(self, key, val)
        self.title = self.__class__.__name__ + ' for "%s"' % self.pattern
        self.date_range = DateRange(start=self.start, stop=self.stop)

    def get_results(self):
        """Fill data frame, pivot, and set row_label, column_label, and row values."""
        self.data_frame = DataFrame()
        self.fill_data_frame()
        
        # use default pivot parameters
        pt = self.get_pivot_table(val='abbrev', rows=['date'], cols=['sensor'], aggregate='count')
        
        # turn pivot table into row_labels, column_labels, and rows to show
        self.row_labels = [ str(i[0][1]) for i in pt.rnames]     # days as row labels
        self.column_labels = [ str(i[0][1]) for i in pt.cnames]  # sensors as column labels
        self.rows = [ i for i in pt ]                            # count roadmap files for cell values
    
    def fill_data_frame(self):
        """Populate data frame day-by-day."""
        d = self.date_range.start
        while d <= self.date_range.stop:
            self.pivot_table_insert_day_entries(d)
            d += datetime.timedelta(days=1)

    def pivot_table_insert_day_entries(self, d):
        """Walk ymd path and insert regex matches of filename pattern into data frame."""
        dirpath = os.path.join( self.basepath, d.strftime('year%Y/month%m/day%d') )
        #fullfile_pattern = os.path.join(dirpath, self.pattern)
        fullfile_pattern = self.pattern
        bool_got_match = False
        for f in filter_filenames(dirpath, re.compile(fullfile_pattern).match):
            self.do_data_frame_insert(d, f)
            bool_got_match = True
        if not bool_got_match:
            # do not skip any days/rows, insert dummy dict for dfin
            self.do_data_frame_insert(d, None)
            
    def do_data_frame_insert(self, d, f):
        """Parse file basename to get dict and do data frame insert."""
        # handle degenerate case of no matching files
        if not f:
            self.data_frame.insert({'date':d.strftime('%Y-%m-%d'), 'hour':None, 'sensor':None, 'abbrev':None, 'bname':None, 'fname':None})
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
    
    def get_pivot_table(self, val='abbrev', rows=['date'], cols=['sensor'], aggregate='count'):
        """This is where we pivot."""
        return self.data_frame.pivot(val, rows, cols, aggregate)
    
    def attach(self, other):
        """Attach other DataFrame to this one (both must have the same columns)"""
        # do minimal checking
        if not isinstance(other, RoadmapsGridWorker):
            raise TypeError('second argument must be a RoadmapsGridWorker')
        # perform attachment
        self.data_frame.attach(other.data_frame)

    def __str__(self): return 'This is a %s for %s.\n' % (self.title, self.date_range)

    def __repr__(self): return self.__str__()

class CheapPadHoursGridWorker(RoadmapsGridWorker):
    """A grid with days as rows, sensors as columns, & "cheap" PAD hours as cell values."""    

    def do_data_frame_insert(self, d, f):
        """Parse file basename to get dict and do data frame insert."""
        # handle case of no matching files
        if not f:
            self.data_frame.insert({'date':d.strftime('%Y-%m-%d'), 'span_hours':0.0, 'sensor':None, 'bname':None, 'fname':None})
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

    def get_results(self):
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

def pads():
    # gather input info
    log = sys.stdout
    input_grid =  CheapPadHoursInputGrid #RoadmapsInputGrid
    grid_worker = CheapPadHoursGridWorker #RoadmapsGridWorker
    output_grid = CheapPadHoursOutputGrid #RoadmapsOutputGrid
    # launch app
    app = wx.App(False)
    frame = MainFrame(log, "PADS", input_grid, grid_worker, output_grid)
    frame.Show()
    app.MainLoop()

def roadmaps():
    # gather input info
    log = sys.stdout
    input_grid =  RoadmapsInputGrid
    grid_worker = RoadmapsGridWorker
    output_grid = RoadmapsOutputGrid
    # launch app
    app = wx.App(False)
    frame = MainFrame(log, "ROADMAPS", input_grid, grid_worker, output_grid)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":

    roadmaps()
    raise SystemExit

    #d1 = parser.parse('2013-10-18').date()
    #d2 = datetime.date.today()-datetime.timedelta(days=2)

#------------------------------------
    
    d1 = parser.parse('2013-01-01').date()
    d2 = parser.parse('2013-01-04').date()
    #d2 = datetime.date.today()-datetime.timedelta(days=2)
    date_range = DateRange(start=d1, stop=d2)
    pad_hours_grid = CheapPadHoursGridWorker(date_range, update_sec=4)
