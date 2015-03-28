#!/usr/bin/env python

import sys
import wx
import wx.grid as  gridlib
import numpy as np
from dateutil import parser
from datetime import timedelta
from pims.utils.pimsdateutil import dtm2unix, format_datetime_as_pad_underscores, _2DAYSAGO, _5DAYSAGO
from pims.utils.datetime_ranger import DateRange
from pims.patterns.dailyproducts import _BATCHROADMAPS_PATTERN, _PADHEADERFILES_PATTERN
#from pims.utils import pyperclip
from pims.utils.commands import timeLogRun
from pims.gui.pywxgrideditmixin import PyWXGridEditMixin
from pims.pad.newestpadheaderfile import newest_pad_header_file_endtime

# TODO add Pause button so that we can freeze state to do remedy or maybe "digging"
#      initially, remedy will just be a filtered look at data frame [or pivot table?]

# TODO add buttons to start and stop "selected/orange cells" for 2 types of threads:
#      monitor thread - disable grid interaction and just update cells every so often
#      remedy thread - how in the world do we get remedy specifics?

# FIXME we can fold 'basepath' into the PATTERNS and get rid of that attribute -- right?  TAG FIRST!!!

class CheapPadHoursRenderer(gridlib.PyGridCellRenderer):
    def __init__(self):
        gridlib.PyGridCellRenderer.__init__(self)

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        text = grid.GetCellValue(row, col)
        hours = float(text)
        hAlign, vAlign = attr.GetAlignment()
        dc.SetFont( attr.GetFont() )
        if isSelected:
            bg = grid.GetSelectionBackground()
            fg = grid.GetSelectionForeground()
        else:
            bg = 'white'
            fg = attr.GetTextColour()
            if hours == 0.0:
                bg = 'pink'
            elif hours < 8.0:
                bg = 'yellow'
            elif hours >= 8.0 and hours < 20.0:
                fg = 'red'
            
        dc.SetTextBackground(bg)
        dc.SetTextForeground(fg)
        dc.SetBrush(wx.Brush(bg, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)           
        grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)
  
    def Clone(self):
        return CheapPadHoursRenderer()

class RoadmapsRenderer(CheapPadHoursRenderer):

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        text = grid.GetCellValue(row, col)
        numfiles = int(text)
        hAlign, vAlign = attr.GetAlignment()
        dc.SetFont( attr.GetFont() )
        if isSelected:
            bg = grid.GetSelectionBackground()
            fg = grid.GetSelectionForeground()
        else:
            bg = 'yellow'
            if numfiles == 0:
                bg = 'pink'
            elif numfiles == 4 or numfiles == 13:
                bg = 'white'
            fg = attr.GetTextColour()

        dc.SetTextBackground(bg)
        dc.SetTextForeground(fg)
        dc.SetBrush(wx.Brush(bg, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)           
        grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)
  
    def Clone(self):
        return RoadmapsRenderer()

class CheapPadHoursInputGrid(gridlib.Grid, PyWXGridEditMixin):
    """Simple grid for inputs to a grid worker that gets results for tallying."""
    def __init__(self, parent, log, pattern=_PADHEADERFILES_PATTERN):
        gridlib.Grid.__init__(self, parent, -1)
        self.parent = parent
        self.log = log
        self.pattern = pattern
        self.get_default_values()
        self.set_default_attributes()
        # To add copy/paste ability for grids, use mixin; also you can set key handler, or add call to grid.Key() in your own handler
        self.__init_mixin__() # mixin for copy/paste
    
    def set_default_attributes(self):
        """Set default attributes of grid."""
        # FIXME make this dynamic, not hard-coded
        #self.SetDefaultRowSize(20)
        self.SetRowLabelSize(140)            
        self.SetColLabelSize(22)
        self.SetDefaultColSize(1280)
        #self.SetDefaultRenderer(gridlib.GridCellFloatRenderer(width=6, precision=1))
        self.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
        self.SetRowLabelAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
    
    def get_default_values(self):
        """Gather columns_labels, row_labels, and rows for input grid defaults."""
        self.column_labels = [ 'value']
        self.rows = [
        #    row_label          default_value1
        #--------------------------------------------------
            ('start',           _5DAYSAGO,           parser.parse),
            ('stop',            _2DAYSAGO,           parser.parse),
            ('pattern',         self.pattern,           str),
            ('basepath',        '/misc/yoda/pub/pad',   str),
            ('update_sec',      '600',                  int),
            ('exclude_columns', 'None',                 lambda x: x.split(',')),
        ]
        self.row_labels = [ t[0] for t in self.rows ]

    def set_row_labels(self):
        """Set the row labels."""
        for i,v in enumerate(self.row_labels):
            self.SetRowLabelValue(i, v) 

    def set_column_labels(self):
        """Set the column labels."""
        for i,v in enumerate(self.column_labels):
            self.SetColLabelValue(i, v)
            #self.SetColLabelAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE) 
            
    def set_default_cell_values(self):
        """Set default cell values using values in rows."""
        # loop over rows to set cell values
        for r, rowtup in enumerate(self.rows):
            self.SetCellValue( r, 0, str(rowtup[1]) )
    
    def get_inputs(self):
        """Get inputs from cells in the grid."""
        inputs = {}
        for i,v in enumerate(self.rows):
            label, val, conv = v[0], self.GetCellValue(i, 0), v[2]
            inputs[label] = conv(val)
        return inputs

class RoadmapsInputGrid(CheapPadHoursInputGrid):
    """Simple grid for inputs to a grid worker that gets roadmap results for tallying."""
    def __init__(self, parent, log, pattern=_BATCHROADMAPS_PATTERN):
        super(RoadmapsInputGrid, self).__init__(parent, log, pattern=pattern)
        
    def get_default_values(self):
        """Gather columns_labels, row_labels, and rows for input grid defaults."""
        self.column_labels = [ 'value']
        self.rows = [
        #    row_label          default_value1
        #--------------------------------------------------
            ('start',           _5DAYSAGO,           parser.parse),
            ('stop',            _2DAYSAGO,           parser.parse),
            ('pattern',         self.pattern,                   str),
            ('basepath',        '/misc/yoda/www/plots/batch',   str),
            ('update_sec',      '600',                          int),
            ('exclude_columns', 'None',                         lambda x: x.split(',')),
        ]
        self.row_labels = [ t[0] for t in self.rows ]   

class TallyOutputGrid(gridlib.Grid, PyWXGridEditMixin):
    """Simple grid for output of tally."""
    
    def __init__(self, panel, log, results):
        gridlib.Grid.__init__(self, panel, -1)
        self.panel = panel
        self.log = log
        # To add copy/paste ability for grids, use mixin; also you can set key handler, or add call to grid.Key() in your own handler
        self.__init_mixin__() # mixin for copy/paste
        
        # get properties from results dictionary 
        self.row_labels = results['row_labels']
        self.column_labels = results['column_labels']
        self.rows = results['rows']
        self.exclude_columns = results['exclude_columns']
        self.update_sec = results['update_sec']
        
        self.set_default_attributes()
        self.bind_events()
        self.update_grid()

    # FIXME can we work around what seems like bug in GetSelectedCells?
    #       for now, just go with a la carte selection style results
    def process_selected_cells(self, evt):
        """Get/process selected cells."""
        selected_cells = self.GetSelectedCells()
        #if not cells:
        #    if self.GetSelectionBlockTopLeft():
        #        top_left = self.GetSelectionBlockTopLeft()[0]
        #        bottom_right = self.GetSelectionBlockBottomRight()[0]
        #        print "top-left, bottom-right:", top_left, bottom_right
        #    else:
        #        print "cells ", cells
        #else:
        #    print "cells ", cells
        if selected_cells:
            self.log.write( '%d selected cells are: %s' % ( len(selected_cells), str(selected_cells) ) )

    def set_default_attributes(self):
        """Set default attributes of grid."""
        # FIXME make this dynamic, not hard-coded
        self.SetDefaultRowSize(20)
        self.SetRowLabelSize(99)            
        self.SetColLabelSize(22)
        #self.SetDefaultColSize(1280)
        #self.SetDefaultRenderer(gridlib.GridCellFloatRenderer(width=6, precision=1))
        self.SetDefaultCellAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.SetColLabelAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.SetRowLabelAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)

    def bind_events(self):        
        self.moveTo = None
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.EnableEditing(False)
        
        # for now, just simple callbacks on all the events
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_DCLICK, self.OnCellRightDClick)

        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLeftDClick)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_DCLICK, self.OnLabelRightDClick)

        self.Bind(gridlib.EVT_GRID_ROW_SIZE, self.OnRowSize)
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnColSize)

        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.OnSelectCell)

        self.Bind(gridlib.EVT_GRID_EDITOR_SHOWN, self.OnEditorShown)
        self.Bind(gridlib.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)
        self.Bind(gridlib.EVT_GRID_EDITOR_CREATED, self.OnEditorCreated)

    def update_grid(self):
        """Write labels and values to grid."""
        # if needed, then exclude some columns
        idx_toss = []
        for xcol in self.exclude_columns:
            idx_toss += [i for i,x in enumerate(self.column_labels) if x == xcol]
        arr = np.array(self.rows)
        arr = np.delete(arr, idx_toss, axis=1)
            
        # get rid of labels for exclude columns too
        column_labels = [i for i in self.column_labels if i not in self.exclude_columns]

        # now we have enough info to create grid
        self.CreateGrid(arr.shape[0], arr.shape[1])

        # loop over array to set cell values
        for r in range(arr.shape[0]):
            self.SetRowLabelValue(r, self.row_labels[r])
            #self.SetRowAttr(r, attr)
            for c in range(arr.shape[1]):
                self.SetCellValue(r, c, str(arr[r][c]))
                #self.SetCellTextColour(r, c, wx.BLUE)

        # set column labels
        for idx, clabel in enumerate(column_labels):
            self.SetColLabelValue(idx, clabel)
        self.SetColLabelAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)        

    def OnCellLeftClick(self, evt):
        self.log.write("OnCellLeftClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnCellRightClick(self, evt):
        self.log.write("OnCellRightClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnCellLeftDClick(self, evt):
        self.log.write("OnCellLeftDClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnCellRightDClick(self, evt):
        self.log.write("OnCellRightDClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnLabelLeftClick(self, evt):
        if evt.GetRow() == -1:
            if evt.GetCol() == -1:
                wise = 'BOTH'
                label = 'both'
            else:
                wise = 'COLUMN'
                label = self.GetColLabelValue(evt.GetCol())
        elif evt.GetCol() == -1:
            wise = 'ROW'
            label = self.GetRowLabelValue(evt.GetRow())
        else:
            wise = 'NEITHER'
            label = 'neither'
            
        self.log.write("OnLabelLeftClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        msg = "%s-WISE: %s" % (wise, label)
        self.log.write(msg + '\n')

        evt.Skip()

    def OnLabelRightClick(self, evt):
        self.log.write("OnLabelRightClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnLabelLeftDClick(self, evt):
        self.log.write("OnLabelLeftDClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnLabelRightDClick(self, evt):
        self.log.write("OnLabelRightDClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnRowSize(self, evt):
        self.log.write("OnRowSize: row %d, %s\n" %
                       (evt.GetRowOrCol(), evt.GetPosition()))
        evt.Skip()

    def OnColSize(self, evt):
        self.log.write("OnColSize: col %d, %s\n" %
                       (evt.GetRowOrCol(), evt.GetPosition()))
        evt.Skip()

    def OnRangeSelect(self, evt):
        if evt.Selecting():
            msg = 'Selected'
        else:
            msg = 'Deselected'
        self.log.write("OnRangeSelect: %s  top-left %s, bottom-right %s\n" %
                           (msg, evt.GetTopLeftCoords(), evt.GetBottomRightCoords()))
        evt.Skip()

    def OnCellChange(self, evt):
        self.log.write("OnCellChange: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))

        # Show how to stay in a cell that has bad data.  We can't just
        # call SetGridCursor here since we are nested inside one so it
        # won't have any effect.  Instead, set coordinates to move to in
        # idle time.
        value = self.GetCellValue(evt.GetRow(), evt.GetCol())

        if value == 'no good':
            self.moveTo = evt.GetRow(), evt.GetCol()

    def OnIdle(self, evt):
        if self.moveTo != None:
            self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo = None
        evt.Skip()

    def OnSelectCell(self, evt):
        if evt.Selecting():
            msg = 'Selected'
        else:
            msg = 'Deselected'
        self.log.write("OnSelectCell: %s (%d,%d) %s\n" %
                       (msg, evt.GetRow(), evt.GetCol(), evt.GetPosition()))

        # Another way to stay in a cell that has a bad value...
        row = self.GetGridCursorRow()
        col = self.GetGridCursorCol()

        if self.IsCellEditControlEnabled():
            self.HideCellEditControl()
            self.DisableCellEditControl()

        value = self.GetCellValue(row, col)

        if value == 'no good 2':
            return  # cancels the cell selection

        evt.Skip()

    def OnEditorShown(self, evt):
        if evt.GetRow() == 6 and evt.GetCol() == 3 and \
           wx.MessageBox("Are you sure you wish to edit this cell?",
                        "Checking", wx.YES_NO) == wx.NO:
            evt.Veto()
            return

        self.log.write("OnEditorShown: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnEditorHidden(self, evt):
        if evt.GetRow() == 6 and evt.GetCol() == 3 and \
           wx.MessageBox("Are you sure you wish to  finish editing this cell?",
                        "Checking", wx.YES_NO) == wx.NO:
            evt.Veto()
            return

        self.log.write("OnEditorHidden: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnEditorCreated(self, evt):
        self.log.write("OnEditorCreated: (%d, %d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetControl()))

class CheapPadHoursOutputGrid(TallyOutputGrid):

    def update_grid(self):
        """Write labels and values to grid."""
        # if needed, then exclude some columns
        idx_toss = []
        for xcol in self.exclude_columns:
            idx_toss += [i for i,x in enumerate(self.column_labels) if x == xcol]
        arr = np.array(self.rows)
        arr = np.delete(arr, idx_toss, axis=1)
            
        # get rid of labels for exclude columns too
        column_labels = [i for i in self.column_labels if i not in self.exclude_columns]

        # now we have enough info to create grid
        self.CreateGrid(arr.shape[0], arr.shape[1])

        # set custom renderer, just for row 4
        attr = gridlib.GridCellAttr()
        attr.SetRenderer(CheapPadHoursRenderer())

        # loop over array to set cell values
        for r in range(arr.shape[0]):
            self.SetRowLabelValue(r, self.row_labels[r])
            self.SetRowAttr(r, attr)
            for c in range(arr.shape[1]):
                #self.SetCellValue(r, c, str(arr[r][c]))
                self.SetCellValue(r, c, str( np.round( arr[r][c], 1 )))
                #self.SetCellTextColour(r, c, wx.BLUE)

        # set column labels
        for idx, clabel in enumerate(column_labels):
            self.SetColLabelValue(idx, clabel)
        self.SetColLabelAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE) 

    # FIXME only allow this for "006" columns [ OR should it be the "unfiltered" sensor column?]
    # FIXME see base class for bug in selected cells
    def process_selected_cells(self, evt):
        """Do resample for selected cells."""
        selected_cells = self.GetSelectedCells()
        if selected_cells:
            self.log.write( '%d jobs to do:\n' % len(selected_cells) )
            prefix_cmd = 'export OCTAVEPATH=/home/pims/dev/programs/octave;'
            for cell in selected_cells:
                dtm = parser.parse( self.GetRowLabelValue(cell[0]) )
                sensor = self.GetColLabelValue(cell[1])
                #u1 = dtm2unix(dtm)
                #u2 = dtm2unix(dtm+timedelta(days=1))
                #print "rm packetWriterState; python /usr/local/bin/pims/packetWriter.py tables=%s ancillaryHost=kyle cutoffDelay=0 delete=0 startTime=%.1f endTime=%.1f" %( sensor, u1, u2)
                s1 = format_datetime_as_pad_underscores(dtm)
                s2 = format_datetime_as_pad_underscores(dtm + timedelta(days=1))
                hours_tally = float(self.GetCellValue(cell[0], cell[1]))
                if hours_tally == 0.0:
                    # if selected cell value is zero (hours), then do cmdstr for whole day
                    cmdstr = prefix_cmd + "python /home/pims/dev/programs/python/packet/resample.py fcNew=6 sensor=%s dateStart=%s dateStop=%s" %( sensor.strip('006'), s1, s2)
                else:
                    # otherwise, do some form of remedy_resample instead                     
                    endtime = newest_pad_header_file_endtime(dtm, sensor), self.GetCellValue(cell[0], cell[1])
                    s1 = format_datetime_as_pad_underscores(endtime[0] + timedelta(seconds=1))
                    cmdstr = prefix_cmd + "python /home/pims/dev/programs/python/packet/resample.py fcNew=6 sensor=%s dateStart=%s dateStop=%s" %( sensor.strip('006'), s1, s2)
                timeLogRun(cmdstr, 2700, None) # timeout of 2700 seconds for 45 minutes

class RoadmapsOutputGrid(TallyOutputGrid):

    def update_grid(self):
        """Write labels and values to grid."""
        # if needed, then exclude some columns
        idx_toss = []
        for xcol in self.exclude_columns:
            idx_toss += [i for i,x in enumerate(self.column_labels) if x == xcol]
        arr = np.array(self.rows)
        arr = np.delete(arr, idx_toss, axis=1)
            
        # get rid of labels for exclude columns too
        column_labels = [i for i in self.column_labels if i not in self.exclude_columns]

        # now we have enough info to create grid
        self.CreateGrid(arr.shape[0], arr.shape[1])

        # set custom renderer, just for row 4
        attr = gridlib.GridCellAttr()
        attr.SetRenderer(RoadmapsRenderer())

        # loop over array to set cell values
        for r in range(arr.shape[0]):
            self.SetRowLabelValue(r, self.row_labels[r])
            self.SetRowAttr(r, attr)
            for c in range(arr.shape[1]):
                self.SetCellValue(r, c, str(arr[r][c]))
                #self.SetCellTextColour(r, c, wx.BLUE)

        # set column labels
        for idx, clabel in enumerate(column_labels):
            self.SetColLabelValue(idx, clabel)
        self.SetColLabelAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE) 

    def runMatlabSuperfine(self, sensor, d, logProcess=None):
        """run generate_vibratory_roadmap_superfine on ike for this day/sensor"""
        cmdstr = 'ssh ike /home/pims/dev/programs/bash/backfillsuperfine.bash %s %s "*_accel_*%s"' % (d.strftime('%Y-%m-%d'), d.strftime('%Y-%m-%d'), sensor)
        #print cmdstr
        timeLogRun(cmdstr, 3600, logProcess) # timeout of 3600 seconds for 60 minutes

    def runMatlabRoadmap(self, sensor, d, mfile, abbrev, logProcess=None):
        """run cutoff or 10 Hz version of generate_vibratory_roadmap on ike for this day/sensor"""
        cmdstr = 'ssh ike /home/pims/dev/programs/bash/backfill_roadmap.bash %s "*_accel_*%s" %s %s' % (d.strftime('%Y-%m-%d'), sensor, mfile, abbrev)
        #print cmdstr        
        timeLogRun(cmdstr, 3600, logProcess) # timeout of 3600 seconds for 60 minutes
    
    def runIkeRepairRoadmap(self, d, logProcess=None):
        """run processRoadmap.py on ike to get new PDFs into the mix"""
        repairYear = d.strftime('%Y')
        cmdstr = "ssh ike 'cd /home/pims/roadmap && python /home/pims/roadmap/processRoadmap.py logLevel=3 mode=repair repairModTime=4 repairYear=%s | grep nserted'" % repairYear
        #print cmdstr        
        timeLogRun(cmdstr, 900, logProcess) # timeout of 900 seconds for 15 minutes

    # TODO loop over zero cells, ONLY f0[23458] NOT 006 (and desc by date):
    #      1. kill prev PID
    #      2. run next cmd (including rm at start)
    # FIXME see base class for bug in selected cells
    def process_selected_cells(self, evt):
        """Do roadmaps for selected cells."""
        selected_cells = self.GetSelectedCells()
        if selected_cells:
            self.log.write( '%d jobs to do:\n' % len(selected_cells) )
            prefix_cmd = 'export OCTAVEPATH=/home/pims/dev/programs/octave;'
            for cell in selected_cells:
                dtm = parser.parse( self.GetRowLabelValue(cell[0]) )
                sensor = self.GetColLabelValue(cell[1])
                if sensor.endswith('one'):
                    self.runMatlabSuperfine(sensor.strip('one'), dtm)
                elif sensor.endswith('ten'):
                    self.runMatlabRoadmap(sensor.strip('ten'), dtm, 'configure_roadmap_spectrogram_10hz', "ten")
                else:
                    self.runMatlabRoadmap(sensor, dtm, 'configure_roadmap_spectrogram', "''")
                self.runIkeRepairRoadmap(dtm)

class StripChartInputGrid(CheapPadHoursInputGrid):
    """2-columns: (1) PARAMETERS (like packetWriter.py), and (2) rt_params (plot_span, etc.)"""
    
    #from pims.realtime import rt_params
    
    def __init__(self, parent, log, rt_params):
        self.rt_params = rt_params
        super(StripChartInputGrid, self).__init__(parent, log, pattern=None)
        #for k, v in zip(rt_params.keys(), rt_params.values()):
        #    print k, "%s" % v
        #raise SystemExit
        self.SetDefaultRowSize(20)
        self.SetRowLabelSize(200)
        self.SetRowLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        self.EnableEditing(False)
        
    def get_default_values(self):
        """Gather columns_labels, row_labels, and rows for input grid defaults."""
        self.column_labels = [ 'value']
        self.rows = []
        self.row_labels = []
        for label, value in zip(self.rt_params.keys(), self.rt_params.values()):
            self.rows.append( (label, value, str))
            self.row_labels.append(label)

if __name__ == '__main__':
    # SEE ROADMAPS TALLY GRID FOR F02, F04, AND HIRAP FOR 15-OCT-2013 THRU 18-NOV-2013
    from pims.utils.gridworkers import roadmaps, pads
    eval( sys.argv[1] + '()' )
