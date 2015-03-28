#!/usr/bin/env python

# TODO header/title text with analysis_interval (not hard-coded)
# TODO a class to maintain plot type (IntervalStat/RMS) with its parameters & ripple to plot text, etc.
# TODO improved draw_plot code (robustness testing) for cushion at bottom tick of bottom subplot not interfere with wide-n-slide GMT
# TODO for vertical autoscale, do based on plot_span min-to-max time and not what's in plot.data (LOS issue, fewer pts?)
# TODO put processing or data details not already in header/title text to upperleft and/or upperright like off-line plot routines

# The Y axes allows "auto" or "manual" settings. For Y, auto
# mode sets the scaling of the graph to see all the data points.
# Note: have to press Enter in 'manual' text boxes to make new value affect plot.
#
# For X, manual mode does not apply to this graph.  In strip chart
# fashion, we want X to follow the data in near real-time.
#
#
# Most of the strip chart aspects of this are thanks to Eli, that is:
# Eli Bendersky (eliben@gmail.com)
# License: this code is in the public domain
# Last modified: 31.07.2008 (by Eli)

import os
import re
import logging
import random
import sys
import wx
import numpy as np
#from collections import deque
import datetime
from wx.lib.pubsub import Publisher

# The recommended way to use wx with mpl is with the WXAgg
# backend.
import pylab
import matplotlib
from matplotlib import dates
#matplotlib.use('WXAgg') # this throws a warning!?
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
      FigureCanvasWxAgg as FigCanvas, \
      NavigationToolbar2WxAgg as NavigationToolbar
#from matplotlib.ticker import AutoMinorLocator
from matplotlib.ticker import FormatStrFormatter

#from pims.realtime import rt_params as RTPARAMS
from pims.gui.iogrids import StripChartInputPanel
from pims.gui.tally_grid import StripChartInputGrid
from pims.pad.padstream import XyzPlotDataSortedList
from pims.files.log import SimpleLog
from pims.utils.benchmark import Benchmark
from pims.utils.pimsdateutil import unix2dtm
from pims.gui.plotutils import smart_ylims, round2multiple
from pims.gui.pimsticker import CushionedLinearLocator
from pims.gui import DUMMYDATA
from pims.database.samsquery import SimpleQueryAOS, get_samsops_db_params

from obspy.core.utcdatetime import UTCDateTime
from obspy.realtime import RtTrace
from obspy import read

# Status bar and other global vars
SB_LEFT = 0
SB_RIGHT = 1
REDRAW_MSEC = 5000               # redraw timer every 5 to 10 seconds or so
SB_MSEC = int( 3 * REDRAW_MSEC ) # lower-right time ~every several seconds
BENCH_STEP = Benchmark('step')   # datagen next method ("step") should avg about 3s

class DataGenRandom(object):
    """ A silly class that generates pseudo-random data for plot display."""
    def __init__(self, init=50):
        self.data = self.init = init
        
    def next(self):
        self._recalc_data()
        return self.data
    
    def _recalc_data(self):
        delta = random.uniform(-0.5, 0.5)
        r = random.random()

        if r > 0.9:
            self.data += delta * 15
        elif r > 0.8: 
            # attraction to the initial value
            delta += (0.5 if self.init > self.data else -0.5)
            self.data += delta
        else:
            self.data += delta

class DataGenExample(object):
    """Generator for RtTrace using trace split and rt scaling on example slist ascii file."""
    
    def __init__(self, scale_factor=0.1, num_splits=3):
        self.num = -1
        
        self.scale_factor = scale_factor
        self.num_splits = num_splits
        
        # read example trace (with demean stream first)
        self.data_trace = self.read_example_trace_demean()
        
        # split given trace into a list of three sub-traces:
        self.traces = self.split_trace()
        
        # assemble real time trace and register rt proc (scale by factor)
        self.rt_trace, i1 = self.assemble_rttrace_register1proc()
    
        # append and auto-process packet data into RtTrace:
        self.append_and_autoprocess_packet()
        self.header_string = 'example header string'
    
    def next(self, step_callback=None):
        if self.num < len(self.rt_trace) - 1:
            self.num += 1
            if step_callback:
                current_info_tuple = ('0000-00-00 00:00:00.000', '0000-00-00 00:00:00.000', '%6d' % self.num)
                cumulative_info_tuple = ('%6d' % len(self.rt_trace), '0000-00-00 00:00:00.000', '0000-00-00 00:00:00.000')
                step_callback(current_info_tuple, cumulative_info_tuple)
            return self.rt_trace[self.num]
        else:
            #raise StopIteration()
            self.num = -1
            return 0
    
    def read_example_trace_demean(self):
        """Read first trace of example data file"""
        st = read('/home/pims/dev/programs/python/pims/sandbox/data/slist_for_example.ascii')
        st.detrend('demean')
        data_trace = st[0]
        return data_trace

    def split_trace(self):
        """split given trace into a list of three sub-traces"""
        traces = self.data_trace / self.num_splits
        return traces

    def assemble_rttrace_register1proc(self):
        """assemble real time trace and register one process"""
        #rt_trace = RtTrace()
        rt_trace = PimsRtTrace()
        return rt_trace, rt_trace.registerRtProcess('scale', factor=self.scale_factor)

    def append_and_autoprocess_packet(self):
        """append and auto-process packet data into RtTrace"""
        for tr in self.traces:
            self.rt_trace.append(tr, gap_overlap_check=True)

class DataGenBetterExample(object):
    """Generator for X,Y,Z RtTraces using trace split and rt scaling on example slist ascii file."""
    
    def __init__(self, scale_factor=1000, num_splits=1):
        self.num = -1
        
        self.scale_factor = scale_factor
        self.num_splits = num_splits
        
        # read example trace (with demean stream first)
        self.data_trace = self.read_example_trace_demean()
        
        # split given trace into a list of sub-traces:
        self.traces = self.split_trace()
        
        # assemble real time traces and register rt proc (scale by factor)
        self.rt_trace = {}
        for ax in ['x', 'y', 'z']:
            self.rt_trace[ax], i1 = self.assemble_rttrace_register1proc()
    
        # append and auto-process packet data into RtTrace:
        self.append_and_autoprocess_packet()
        self.header_string = 'example header string'

        # initialize values for step routine
        self.starttime = self.rt_trace['x'].stats.starttime
        self.analysis_interval = 10.0
        self.analysis_samples = np.ceil( self.rt_trace['x'].stats.sampling_rate * self.analysis_interval )

    def next(self, step_callback=None):
        endtime = self.starttime + self.analysis_interval
        slice_range = {'starttime':self.starttime, 'endtime':endtime}
        traces = {}
        traces['x'] = self.rt_trace['x'].slice(**slice_range)
        slice_len = traces['x'].stats.npts
        cumulative_info_tuple = (str(self.starttime), str(endtime), '%d' % len(traces['x']))
        if  slice_len >= self.analysis_samples:
            self.num += 1
            # now get y and z
            for ax in ['y', 'z']:
                traces[ax] = self.rt_trace[ax].slice(**slice_range)
            t = traces['x'].absolute_times()
            traces['y'].filter('lowpass', freq=2.0, zerophase=True)
            traces['z'].filter('highpass', freq=2.0, zerophase=True)

            # get info and data to pass to step callback routine
            current_info_tuple = (str(slice_range['starttime']), str(slice_range['endtime']), '%d' % len(t))
            flash_msg = None
                
            # slide to right by analysis_interval
            self.starttime = endtime
        else:
            # not enough analysis_samples to work with, just squawk via flash message
            t = traces = []
            current_info_tuple = tuple()
            flash_msg = "slice_len = %d < %d needed for analysis_interval" % (slice_len, self.analysis_samples)

        if step_callback:
            step_data = (current_info_tuple, cumulative_info_tuple, t, traces, flash_msg)            
            step_callback(step_data)

    def read_example_trace_demean(self):
        """Read first trace of example data file"""
        st = read('/home/pims/dev/programs/python/pims/sandbox/data/slist_for_example_f05.ascii')
        st.detrend('demean')
        data_trace = st[0]
        return data_trace

    def split_trace(self):
        """split given trace into a list of three sub-traces"""
        traces = self.data_trace / self.num_splits
        return traces

    def assemble_rttrace_register1proc(self):
        """assemble real time trace and register one process"""
        rt_trace = PimsRtTrace()
        return rt_trace, rt_trace.registerRtProcess('scale', factor=self.scale_factor)

    def append_and_autoprocess_packet(self):
        """append and auto-process packet data into RtTrace"""
        for ax in ['x', 'y', 'z']:
            for tr in self.traces:
                # change Y and Z to look different than X for testing purposes
                if ax == 'y':
                    tr.data = -1.0 * tr.data
                if ax == 'z':
                    tr.data = 0.5 * tr.data
                self.rt_trace[ax].append(tr, gap_overlap_check=True)

class BoundControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a 
        manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)
        
        self.value = initval
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        self.radio_auto = wx.RadioButton(self, -1, 
            label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1,
            label="Manual")
        self.manual_text = wx.TextCtrl(self, -1, 
            size=(50,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)
        
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text) # FIXME bind change (not just ENTER)?

        ## set manual values during initialize here
        #self.radio_manual.SetValue(True)
        
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())
    
    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()
    
    def is_auto(self):
        return self.radio_auto.GetValue()
        
    def manual_value(self):
        return self.value

class BeginEndSamplesBox(wx.Panel):
    """ An info box with begin, end, and number of samples text."""
    def __init__(self, parent, ID, label):
        wx.Panel.__init__(self, parent, ID)
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.begin_time_text = wx.StaticText(self, -1, '0000-00-00 00:00:00.000')
        self.end_time_text = wx.StaticText(self, -1, '0000-00-00 00:00:00.000')
        self.samples_text = wx.StaticText(self, -1, '000000')
       
        sizer.Add(self.begin_time_text, 0, wx.ALL, 10)
        sizer.Add(self.end_time_text, 0, wx.ALL, 10)
        sizer.Add(self.samples_text, 0, wx.ALL, 10)
        
        self.SetSizer(sizer)
        #sizer.Fit(self)
    
    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())
    
    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()
    
    def is_auto(self):
        return self.radio_auto.GetValue()
        
    def manual_value(self):
        return self.value

class GraphFrame(wx.Frame):
    """ The main frame (window) of the strip chart application.
    
    datagen is data generator (let's use its next method)
    title string
    log to keep track of things
    
    """
    def __init__(self, datagen, title, log, rt_params):
        
        self.datagen = datagen
        self.apply_interval_func = datagen.process_chain.apply_interval_func
        self.title = '%s using %s' % (title, self.datagen.__class__.__name__)
        self.log = log
        self.rt_params = rt_params

        # FIXME rt_params should be enough to completely define snap_file
        self.snap_file = os.path.join( rt_params['paths.snap_path'], 'intrms_10sec_5hz.png' ) 
        
        ## FIXME better container for "plot type"
        #self.plot_type = IntervalRMS(self.rt_params['time.analysis_interval'],
        #                             self.rt_params['time.plot_span'],
        #                             self.rt_params['data.scale_factor'])
        
        wx.Frame.__init__(self, None, -1, self.title)
        
        #self.create_menu() # on close, this causes LIBDBUSMENU-GLIB-WARNING Trying to remove a child that doesn't believe we're it's parent.
        
        _HOST, _SCHEMA, _UNAME, _PASSWD = get_samsops_db_params('samsquery')
        self.aos_tiss_time_callback = SimpleQueryAOS(_HOST, _SCHEMA, _UNAME, _PASSWD).get_aos_tisstime
        #self.aos_tiss_time_callback = self.false_aos_tiss_time_callback
        #foo, bar = self.aos_tiss_time_callback(); print foo, bar; raise SystemExit
        
        self.create_status_bar()
        self.create_panels()

        ## get initial values for plot_span, analysis_interval, extra_intervals, maxlen, etc.
        #self.get_inputs()

        # we must limit size of otherwise ever-growing data object
        # use a list of tuples sorted by first element
        self.data = XyzPlotDataSortedList( maxlen=self.rt_params['data.maxlen'] )
        
        # this is first call to "prime the pump" of data generator via next method
        self.paused = False
        #self.data.append( self.datagen.next(self.step_callback) )
        self.datagen.next(self.step_callback) # this appends first several values to self.data's deque
        self.paused = True
       
        # after our first "next" call above, set plot title using datagen's header_string
        # FIXME this should use input args and objects to modify parentheses to show LPF info
        newstr = re.sub(r'(.*)\((.*)\)(.*)', r'\1(5 Hz LPF)\3', self.datagen.header_string)
        self.set_plot_title(newstr)
       
        # Set up a timer to update the date/time (every few seconds)
        self.timer = wx.PyTimer(self.notify)
        self.timer.Start(SB_MSEC)
        self.notify() # call it once right away
        
        # Set up redraw timer
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
        self.redraw_timer.Start(REDRAW_MSEC) # milliseconds
        
        # Do initial redraw
        self.draw_plot()
        self.Maximize()
        
        self.log.debug('GraphFrame was initialized.')

    def get_inputs(self):
        """get values from input panel grid"""
        # get inputs in dict form from input grid
        inputs = self.input_panel.grid.get_inputs()
        
        # set attributes of this graph frame using inputs dict
        for k, v in inputs.iteritems():
            key = k.replace('.', '_')
            setattr(self, key, v)
            #print key, getattr(self, key)
        self.sensor = self.pw_tables # FIXME rename legacy pw tables to sensor early on?

    def update_info(self, info_control, info_tuple):
        info_control.begin_time_text.SetLabel(info_tuple[0])
        info_control.end_time_text.SetLabel(info_tuple[1])
        info_control.samples_text.SetLabel(info_tuple[2])

    # update plot info and data
    def step_callback(self, step_data):
        """update plot info and data"""
        
        # incoming data from (presumably) PadGenerator
        current_info_tuple, cumulative_info_tuple, t, substream, flash_msg = step_data
        
        #substream.write('/tmp/example.slist','SLIST')
        
        if len(t) != 0:
            txyz = tuple()
            meantime = np.mean( [ substream[0].stats.starttime.timestamp, substream[-1].stats.endtime.timestamp] )
            txyz = txyz + ( meantime, )
            
            # apply interval function on per-axis basis (like IntervalRMS)
            rms = self.apply_interval_func(substream)
            
            # kludge to get rid of pesky inf values
            if np.any(np.isinf(rms)):
                # FIXME does merge, detrend, filter, or std cause this inf value issue?
                #fname = '/tmp/substream_' + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + ".SLIST"
                #substream.write(fname, format="SLIST")
                #self.log.debug('WROTE SUBSTREAM FILE %s' % fname)            
                # replace inf values with nan
                rms[np.where(np.isinf(rms))] = np.nan
                # FIXME can we trace back to before detrend & filtering to see what happened?
                self.log.warning( 'INF2NAN had to set inf value to nan for time %s' % unix2dtm(meantime) )
                
            txyz = txyz + tuple(rms)
            self.data.append(txyz)
            
        L = list(txyz); L.insert(0, unix2dtm(txyz[0])); L.insert(0, len(self.data)); self.log.debug( "CSV {:d},{:},{:f},{:f},{:f},{:f}".format(*L) )
        
        if flash_msg:
            self.flash_status_message(flash_msg, flash_len_ms=500)
            
        self.update_info(self.current_info, current_info_tuple)
        self.update_info(self.cumulative_info, cumulative_info_tuple)

    def create_menu(self):
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
                
        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)

    def create_panels(self):
        """layout panels"""
        self.input_panel = StripChartInputPanel(self, self.log, StripChartInputGrid, self.rt_params)
        self.input_panel.grid
        self.input_panel.run_btn.Hide()
        
        self.output_panel = wx.Panel(self)
        self.output_panel.Hide()
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.input_panel, 1, wx.EXPAND)
        self.sizer.Add(self.output_panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)        

        Publisher().subscribe(self.switch_panels, "switch")
        
        self.init_plot()
        self.canvas = FigCanvas(self.output_panel, -1, self.fig)

        self.get_inputs()
        self.xmin_control = BoundControlBox(self.output_panel, -1, "X min", 0)
        self.xmax_control = BoundControlBox(self.output_panel, -1, "X max", 120)
        self.ymin_control = BoundControlBox(self.output_panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.output_panel, -1, "Y max", 0.1)
        self.current_info = BeginEndSamplesBox(self.output_panel, -1, "Current")
        self.cumulative_info = BeginEndSamplesBox(self.output_panel, -1, "Cumulative")        

        self.step_button = wx.Button(self.output_panel, -1, "Step")
        self.Bind(wx.EVT_BUTTON, self.on_step_button, self.step_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_step_button, self.step_button)
        
        self.pause_button = wx.Button(self.output_panel, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
        
        self.cb_grid = wx.CheckBox(self.output_panel, -1, "Show Grid", style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)
        
        self.cb_xlab = wx.CheckBox(self.output_panel, -1, "Show X labels", style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)        
        self.cb_xlab.SetValue(False)

        self.switch_btn = wx.Button(self.output_panel, -1, "Show Inputs")
        self.switch_btn.Bind(wx.EVT_BUTTON, self.switchback)        
        
        # hbox1 for buttons and checkbox controls    
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.switch_btn, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.step_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)        
        self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        # hbox2 for xy min/max controls, and current/cumulative info
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(30)
        self.hbox2.Add(self.current_info, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.cumulative_info, border=5, flag=wx.ALL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.hbox1,  0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2,  0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.canvas, 5, flag=wx.LEFT | wx.TOP | wx.GROW)        
        
        self.output_panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
    
    def switchback(self, event):
        """Callback for panel switch button."""
        Publisher.sendMessage("switch", "message")
    
    def on_switch_panels(self, event):
        """"""
        id = event.GetId()
        self.switch_panels(id)
        
    def switch_panels(self, msg=None):
        """switch panels"""
        if self.input_panel.IsShown():
            self.get_inputs()
            self.SetTitle("Output Panel") # FIXME with better, succinct convention title
            self.input_panel.Hide()
            self.output_panel.Show()
            self.sizer.Layout()
        else:
            self.SetTitle("Input Panel") # FIXME with better, succinct convention title
            self.input_panel.Show()
            self.output_panel.Hide()
        self.Fit()
        self.Layout()

    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar(2, 0)        
        self.statusbar.SetStatusWidths([-1, 320])
        self.statusbar.SetStatusText("Ready", SB_LEFT)

    def getTimeString(self):
        return datetime.datetime.now().strftime('%d-%b-%Y,  %j/%H:%M:%S ')

    def notify(self):
        """ Timer event """
        # FIXME the path and plot name should come for free with inputs/objects
        #self.fig.savefig('/misc/yoda/www/plots/sams/121f05/intrms_10sec_5hz.png', facecolor=self.fig.get_facecolor(), edgecolor='none')
        self.fig.savefig(self.snap_file, facecolor=self.fig.get_facecolor(), edgecolor='none')
        t = self.getTimeString() + ' (update every ' + str(int(SB_MSEC/1000.0)) + 's)'
        self.SetStatusText(t, SB_RIGHT)
        
        # check for new plot parameter file (paths.csvpost_path + sensor_plotstr.csv)
        #fname = self.sensor + '_' + self.datagen.process_chain.interval_func.plotstr() + '.csv'
        #csvfile = os.path.join( self.paths_params_path, fname )
        #if os.path.exists(csvfile):
        #    # handle JAXA posted plot parameter CSV file here (pending, deployed, problem)
        #    msg = '%s BEING HANDLED' % csvfile
        #print msg

    def set_plot_title(self, title):
        """use datagen header_string to set plot title"""
        # FIXME this "plot type" title info should come with input arg yet-to-be generalized object
        self.axes['x'].set_title('10-Second Interval RMS\n' + title, size=16)

    # A generator for *fake* AOS/LOS updates 
    def false_aos_tiss_time_callback(self):
        #aos_tiss = True, datetime.datetime.now()
        #while 1:
        #    aos_tiss = aos_tiss[0], datetime.datetime.now()
        #    yield aos_tiss
        return False, datetime.datetime.now()

    def init_plot(self):
        """initialize the plot"""
        self.axes_labels = ['x', 'y', 'z']
        self.dpi = self.rt_params['figure.dpi']
        self.fig = Figure(self.rt_params['figure.figsize'], dpi=self.dpi)

        rect = self.fig.patch
        rect.set_facecolor('white') # works with plt.show(), but not plt.savefig

        self.axes = {}
        self.axes['x'] = self.fig.add_subplot(3,1,1)
        for i, ax in enumerate(self.axes_labels[1:]):
            self.axes[ax] = self.fig.add_subplot(3, 1, i+2, sharex=self.axes['x'], sharey=self.axes['x'])
            self.axes[ax].set_axis_bgcolor('white')
        self.set_plot_title('init_plot (no first header yet)')
        
        #pylab.setp(self.axes.get_xticklabels(), fontsize=14)
        #pylab.setp(self.axes.get_yticklabels(), fontsize=14)

        # plot the data as a line series, and save the reference 
        # to the plotted line series
        x = DUMMYDATA['x']
        y = DUMMYDATA['y']

        # TODO move these to rt_params via rtsetup.py or where?
        #      and bundle via dict with ax_labels (or maybe a class?)
        self.line_colors = {'x': 'Red', 'y': 'Green', 'z': 'Blue'}
        
        # TODO encapsulate these with step_callback object
        self.units = 'g _{RMS}'
        if self.rt_params['data.scale_factor'] == 1e3:
            self.units_prefix = 'm'
        elif self.rt_params['data.scale_factor'] == 1e6:
            self.units_prefix = '\mu'
        elif self.rt_params['data.scale_factor'] == 1:
            self.units_prefix = ''
        else:
            raise Exception('unhandled data.scale_factor = %g' % rt_params['data.scale_factor'])
        ylabel_suffix = r' ($%s %s$)' % (self.units_prefix, self.units)
        
        # Plotting goes here ...
        self.plot_data = {}
        for ax in self.axes_labels:
            self.plot_data[ax] = self.axes[ax].plot_date(x, y, '.-', color=self.line_colors[ax])[0]
            self.axes[ax].set_ylabel( r'%s-Axis %s' % (ax.upper(), ylabel_suffix) )
            # the pad for GMT in next line was replaced in draw_plot by CushionedLinearLocator
            # to pad a bit to allow wide-n-glide GMT to fit with ymin tick value (zero for RMS)
            #self.axes[ax].tick_params(axis='y', pad=10)        

        # Set major x ticks every 2 minutes, minor every 1 minute (x and y subplots get shared)
        self.axes['z'].xaxis.set_major_locator( matplotlib.dates.MinuteLocator(interval=2) )
        self.axes['z'].xaxis.set_minor_locator( matplotlib.dates.MinuteLocator(interval=1) )
        self.axes['z'].xaxis.set_major_formatter( matplotlib.dates.DateFormatter('%H:%M:%S\n%d-%b-%Y') )
        self.axes['z'].xaxis.set_minor_formatter( matplotlib.dates.DateFormatter('%H:%M:%S') )
        
        # Make tick_params more suitable to our liking...
        plt.tick_params(axis='x', which='both', width=2)
        
        # tick_params for x-axis
        plt.tick_params(axis='x', which='major', labelsize=12, length=8)
        plt.tick_params(axis='x', which='minor', labelsize=9)
        plt.tick_params(axis='x', which='major', length=8)
        plt.tick_params(axis='x', which='minor', length=6, colors='gray')
        
        # tick_params for y-axis
        plt.tick_params(axis='y', which='both', labelsize=12)
        plt.tick_params(right=True, labelright=True)

        # fancy way of making top 2 subplot x-labels vanish (zero labelsize)
        self.axes['x'].tick_params(axis='x', which='minor', labelsize=0, direction='out', length=6)
        self.axes['y'].tick_params(axis='x', which='minor', labelsize=0, direction='out', length=6)

        # only apply GMT xlabel to z-axis
        self.axes['z'].set_xlabel('GMT')
        
        # attach AOS/LOS GMT to "last" axes
        ax = self.fig.axes[-1]
        self.text_aos_gmt = ax.text(1.08, -0.25, '???\n00:00:00\ndd-Mon-yyyy',
                                                horizontalalignment='center',
                                                verticalalignment='center',
                                                transform = ax.transAxes,
                                                bbox=dict(facecolor='LightBlue', alpha=0.3))        
        
        # to save fig with same facecolor as rt plot, use:
        #fig.savefig('whatever.png', facecolor=fig.get_facecolor(), edgecolor='none')

        self.log.debug('GraphFrame.init_plot() is complete.')

    def draw_plot(self):
        """ Redraws the plot"""
        
        # TODO see if you can find better way to pull values from self.data for plot
        t = [ unix2dtm(tup[0]) for tup in list(self.data) ]
        x = [ tup[1] for tup in list(self.data) ]
        y = [ tup[2] for tup in list(self.data) ]
        z = [ tup[3] for tup in list(self.data) ]

        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        secpad = self.rt_params['time.analysis_interval']
        if self.xmax_control.is_auto():
            xmax = t[-1] + datetime.timedelta(seconds=secpad)
        else:
            xmax = float(self.xmax_control.manual_value())
            
        if self.xmin_control.is_auto():
            secdelta = self.rt_params['time.plot_span'] + (2.0 * secpad)
            xmin = xmax - datetime.timedelta(seconds=secdelta)
        else:
            xmin = float(self.xmin_control.manual_value())

        # FIXME check whether something like ax.margins(0.05)
        #       or "just y" version gives cushion better than
        #       CushionedLinearLocator

        # for ymin and ymax, find the min and max values
        # in the data displayed and add some cushion for
        # wide-n-glide GMT on xaxis
        minxyz = min([min(x), min(y), min(z)])
        maxxyz = max([max(x), max(y), max(z)])
        ylims = smart_ylims(minxyz, maxxyz)
        if self.ymin_control.is_auto():
            # this is where cushion happens for positive RMS data
            ycushion = np.diff(ylims) / 20.0
            ymin = -ycushion
            plt.ylim( (0, round2multiple(10, np.abs(ylims[1]))) )
            ytick_locator = CushionedLinearLocator()
            ytick_formatter = FormatStrFormatter('%g')
            self.axes['z'].yaxis.set_major_locator( ytick_locator )
            self.axes['z'].yaxis.set_major_formatter( ytick_formatter )
            plt.ylim( (-ycushion, round2multiple(10, np.abs(ylims[1]))) )
        else:
            ymin = float(self.ymin_control.manual_value())
            
        if self.ymax_control.is_auto():
            ymax = round2multiple(10, ylims[1])
            # for better kludge here, how about min( [ 1001 round2multiple(10, ylims[1]) ] ) ?
        else:
            ymax = float(self.ymax_control.manual_value())

        # only need to set xlims and ylims for x-axis
        # the y-, and z-axis will share both sets of lims
        self.axes['x'].set_xbound(lower=xmin, upper=xmax)
        self.axes['x'].set_ybound(lower=ymin, upper=ymax)
        
        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        if self.cb_grid.IsChecked():
            self.axes['x'].grid(True, color='gray')
            self.axes['y'].grid(True, color='gray')
            self.axes['z'].grid(True, color='gray')
            self.axes['x'].xaxis.grid(True, 'minor')
            self.axes['y'].xaxis.grid(True, 'minor')
            self.axes['z'].xaxis.grid(True, 'minor')
            
        else:
            self.axes['x'].grid(False)
            self.axes['y'].grid(False)
            self.axes['z'].grid(False)
            self.axes['x'].xaxis.grid(False, 'minor')
            self.axes['y'].xaxis.grid(False, 'minor')
            self.axes['z'].xaxis.grid(False, 'minor')
                                
        self.plot_data['x'].set_xdata( t )
        self.plot_data['x'].set_ydata( x )
        
        self.plot_data['y'].set_xdata( t )
        self.plot_data['y'].set_ydata( y )
        
        self.plot_data['z'].set_xdata( t )
        self.plot_data['z'].set_ydata( z )

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #
        #pylab.setp(self.axes['x'].get_xticklabels(), visible=self.cb_xlab.IsChecked())
        plt.setp(self.axes['x'].get_xticklabels(), visible=self.cb_xlab.IsChecked())
        plt.setp(self.axes['y'].get_xticklabels(), visible=self.cb_xlab.IsChecked())

        # update AOS/LOS and current GMT
        self.aos, self.gmt = self.aos_tiss_time_callback()
        #self.aos, self.gmt = self.false_aos_tiss_time_callback()
        if self.aos == 'AOS':
            self.text_aos_gmt.set_backgroundcolor('LightGreen')
        elif self.aos == 'LOS':
            self.text_aos_gmt.set_backgroundcolor('LightPink')
        else:
            self.text_aos_gmt.set_backgroundcolor('LightBlue')
        self.text_aos_gmt.set_text('%s\n%s' % (self.aos, self.gmt.strftime('%H:%M:%S\n%d-%h-%Y')) )

        self.canvas.draw()

        ## it takes bout 50ms to redraw plot
        #self.log.debug('done redrawing plot')

        #MINDLEN, MAXDLEN = 50, 90
        #self.save_screenshot('/tmp/whatever%04d.png' % len(self.data))
        #self.fig.savefig('/tmp/example_%06d.png' % len(self.data), facecolor=self.fig.get_facecolor(), edgecolor='none')
    
    def on_step_button(self, event):
        if self.paused:
            self.datagen.next(self.step_callback) # this appends to self.data
            self.draw_plot()
    
    def on_update_step_button(self, event):
        if self.paused:
            self.step_button.Enable()
        else:
            self.step_button.Disable()
    
    def on_pause_button(self, event):
        self.paused = not self.paused
    
    def on_update_pause_button(self, event):
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)
    
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_cb_xlab(self, event):
        self.draw_plot()
    
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
    
    def on_redraw_timer(self, event):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        if not self.paused:
            BENCH_STEP.start()
            #self.data.append( self.datagen.next(self.step_callback) )
            self.datagen.next(self.step_callback) # appends RMS values to self.data's deque
            self.flash_status_message(str(BENCH_STEP), 2000)
        self.draw_plot()
    
    def on_exit(self, event):
        self.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

    def save_screenshot(self, fileName):
        """ Takes a screenshot of the screen at give pos & size (rect). """
        print 'Taking screenshot...'
        rect = self.GetRect()
        # see http://aspn.activestate.com/ASPN/Mail/Message/wxpython-users/3575899
        # created by Andrea Gavana
 
        # adjust widths for Linux (figured out by John Torres 
        # http://article.gmane.org/gmane.comp.python.wxpython/67327)
        if sys.platform == 'linux2':
            client_x, client_y = self.ClientToScreen((0, 0))
            border_width = client_x - rect.x
            title_bar_height = client_y - rect.y
            rect.width += (border_width * 2)
            rect.height += title_bar_height + border_width
 
        #Create a DC for the whole screen area
        dcScreen = wx.ScreenDC()
 
        #Create a Bitmap that will hold the screenshot image later on
        #Note that the Bitmap must have a size big enough to hold the screenshot
        #-1 means using the current default colour depth
        bmp = wx.EmptyBitmap(rect.width, rect.height)
 
        #Create a memory DC that will be used for actually taking the screenshot
        memDC = wx.MemoryDC()
 
        #Tell the memory DC to use our Bitmap
        #all drawing action on the memory DC will go to the Bitmap now
        memDC.SelectObject(bmp)
 
        #Blit (in this case copy) the actual screen on the memory DC
        #and thus the Bitmap
        memDC.Blit( 0, #Copy to this X coordinate
                    0, #Copy to this Y coordinate
                    rect.width, #Copy this width
                    rect.height, #Copy this height
                    dcScreen, #From where do we copy?
                    rect.x, #What's the X offset in the original DC?
                    rect.y  #What's the Y offset in the original DC?
                    )
 
        #Select the Bitmap out of the memory DC by selecting a new
        #uninitialized Bitmap
        memDC.SelectObject(wx.NullBitmap)
 
        img = bmp.ConvertToImage()
        #fileName = "/tmp/myImage.png"
        img.SaveFile(fileName, wx.BITMAP_TYPE_PNG)
        #print '...saving as png!'

def demo_pad_gen():
    from pims.pad.packetfeeder import PadGenerator
    from pims.realtime import rt_params
    
    app = wx.PySimpleApp()
    log = SimpleLog('pims.gui.stripchart.demo_pad_gen', log_level='DEBUG').log
    log.info('Logging started.')
    #app.frame = GraphFrame(DataGenExample(), 'title', log, rt_params)
    app.frame = GraphFrame(DataGenBetterExample(), 'title', log, rt_params)
    #app.frame = GraphFrame(PadGenerator(), 'title', log, rt_params)
    app.frame.Show()
    app.MainLoop()        

def demo_callback(curr_info, cum_info):
    print curr_info, cum_info
    
def demo_datagen_with_time_arr():
    dg = DataGenBetterExample(scale_factor=0.1, num_splits=4)
    for i in range(1000):
        if i < 3 or i > 746:
            cb = demo_callback
        else:
            cb = None
        t, a = dg.next(step_callback=cb)

if __name__ == '__main__':
    
    #demo_datagen_with_time_arr()
    demo_pad_gen()
    

#-----------------------------------
#FIRST PACKET
#-----------------------------------
#SAMS2, 121f05, X-axis
#JPM1F5, ER4, Drawer 2
#sample_rate 500 (Hz > sps)
#
#-----------------------------------
#THIS PACKET 0279
#-----------------------------------
#BEGINS: 2013-09-09T15:20:15.672885Z
#ENDS:   2013-09-09T15:20:15.818885Z
#74 samples
#packetGap: 0.1480000019
#sampleGap: 0.0020000935
#
#-----------------------------------
#CUMULATIVE REAL-TIME TRACE
#-----------------------------------
#BEGINS: 2013-09-09T15:20:15.672885Z
#ENDS:   2013-09-09T15:20:15.818885Z
#74 samples
#
#-----------------------------------
#MISC
#-----------------------------------
#TOTAL_PACKETS_FED
#NEXT_COUNT
