#!/usr/bin/env python

import os
import sys
import datetime
from threading import *
import wx
import numpy as np
from plot_datetix import GraphFrame
from pylab import NaN

from pims.realtime.accelpacket import *
from pims.utils.pimsdateutil import unix2dtm
from pims.database.samsquery import SimpleQueryAOS, _HOST, _SCHEMA, _UNAME, _PASSWD

# input parameters
defaults = {
    'host':  'mr-hankey',   # host to query
    'table': '121f04',      # table name (i.e. sensor)
}
parameters = defaults.copy()

def parametersOK():
    """check for reasonableness of parameters"""
    parameters['aos_status'] = SimpleQueryAOS(_HOST, _SCHEMA, _UNAME, _PASSWD)

    return True # all OK, returned False (above) otherwise

# Status bar constants
SB_LEFT = 0
SB_RIGHT = 1
SB_MSEC = 2000

# Button definitions
START_ID = wx.NewId()
STOP_ID = wx.NewId()
SHOW_ID = wx.NewId()

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Result event"""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """A simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Initialize result event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class PacketIterator(object):
    """A packet iterator that maintains previous packet info (like contiguity)."""
    def __init__(self, packets, prevPacket=None):
        self.index = -1
        self.length = len(packets)
        self.packets = packets
        self.startTime = self.get_start_time()
        self.endTime = self.get_end_time()
        
        if self.length > 0:
            self.array = np.array(self.packets[0].xyz())
            # FIXME if there is a better way to build this array?
            for list_of_xyz_tuples in [p.xyz() for p in self.packets[1:]]:
                self.array = np.vstack([self.array, np.array(list_of_xyz_tuples)])
        
        #if not prevPacket:
        #    self.isContig = packets[0].contiguous(prevPacket)
        #else:
        #    self.isContig = True

    def __str__(self):
        s = '<%s> HAS %d PKTS w/ %d XYZ RECs (tuples).' % ( self.__class__.__name__, self.length, np.shape(self.array)[0] )
        return s

    def get_accel_stats(self):
        vecmag = np.sqrt(np.sum(self.array**2, axis=1))
        vecmag_max = np.max(vecmag)
        vecmag_avg = np.mean(vecmag)
        vecmag_std = np.std(vecmag)
        return vecmag_max, vecmag_avg, vecmag_std

    def get_start_time(self):
        """get start time for these packets"""
        if self.length == 0:
            return None
        return self.packets[0].time()

    def get_end_time(self):
        """get end time for these packets"""
        if self.length == 0:
            return None
        return self.packets[-1].endTime()
        
    def __iter__(self):
        return self

    def next(self):
        self.index += 1
        if self.index == self.length:
            raise StopIteration
        else:
            return self.packets[self.index]

class DatabaseTimeIterator(object):
    """A time-based database iterator."""    
    def __init__(self, displayHours=0.5, updateSeconds=5.0, host=None, table=None):
        self.host = host
        self.table = table        
        self.dispTime = datetime.timedelta(hours=displayHours)
        self.updateTime = datetime.timedelta(seconds=updateSeconds)
        self.updateTimeRange()
        self.startTime = self.dbMaxTime - self.dispTime - self.updateTime
        self.endTime = self.startTime + self.updateTime
        
    def __iter__(self):
        return self

    def next(self):
        self.startTime = self.endTime
        self.endTime = self.startTime + self.updateTime
        self.packets = self.dbFetchPackets()
        return self.startTime, self.endTime

    def updateTimeRange(self):
        self.dbMaxTime = self.getMaxTime()
        self.dbMinTime = self.getMinTime()
        
    def getMinTime(self):
        r = sqlConnect('select from_unixtime(min(time)) from %s' % self.table, self.host)
        return r[0][0]
    
    def getMaxTime(self):
        r = sqlConnect('select from_unixtime(max(time)) from %s' % self.table, self.host)
        return r[0][0]
    
    def dbFetchPackets(self):
        fmtDateTime = '%Y-%m-%d %H:%M:%S.%f'
        query = 'select * from %s where time>=unix_timestamp("%s") and time<unix_timestamp("%s") order by time asc' \
                % (self.table, self.startTime.strftime(fmtDateTime), self.endTime.strftime(fmtDateTime))
        results = sqlConnect(query, self.host) # NOTE: results[0] is time, results[1] is the blob, results[2] is the type
        packets = [guessPacket(i[1]) for i in results]
        self.updateTimeRange()
        return packets    

class ProcessThread(Thread):
    """Worker thread to get database query results and processing."""
    def __init__(self, notify_window, graph_window):
        """initialize"""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._graph_window = graph_window
        self._want_abort = 0
        
        # FIXME this should have more info (location, name)
        axes_title = 'SAMS Sensor ' +  self._notify_window.table
        wx.CallAfter(self._graph_window.axes.set_title, axes_title)
        
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def update_AOS(self):
        """update LED for AOS/LOS"""
        # use CallAfter for thread-safe access to wx main window gui
        wx.CallAfter(self._notify_window.update_AOS)
        # FIXME for display window, get rid of TISS time part (but make it so I can get at it when I want to)
        wx.CallAfter( self._graph_window.update_AOS, str( parameters['aos_status'] ) )
        
    def change_status(self, txt):
        """change LEFT status in main window"""
        # use CallAfter for thread-safe access to wx main window gui
        wx.CallAfter(self._notify_window.SetStatusText, txt, SB_LEFT)
        
    def appendText(self, txt):
        """append text to main window textcontrol"""
        # use CallAfter for thread-safe access to wx main window gui
        wx.CallAfter(self._notify_window.text.WriteText, txt)

    def dbTimeRangeUpdate(self, t1, t2):
        """update static texts in main window for db min/max times"""
        # use CallAfter for thread-safe access to wx main window gui
        trange = " db from " + " to ".join( (t1, t2) )
        # FIXME copy table and host attributes from _notify_window to _graph_window
        new_title = " ".join( (self._notify_window.table, self._notify_window.host, trange) )
        wx.CallAfter(self._notify_window.SetTitle, new_title)
        wx.CallAfter(self._graph_window.SetTitle, new_title)
        
    def vecmag(self, p):
        xyz = np.array(p.xyz())
        return np.sqrt(np.sum(xyz**2, axis=1)) # along rows, with xyz in each row

    def vecmag_max(self, p):
        vecmag = self.vecmag(p)
        return np.max(vecmag)

    def processPackets(self, packets):
        """Process latest db fetch of packets based on time."""
        pkts = PacketIterator(packets)
        if pkts.length == 0:
            #self.appendText('\nNo packets to process at %s' % datetime.datetime.now())
            self.change_status( 'No packets to process now %s' % datetime.datetime.now().strftime('%d-%b-%Y,%j/%H:%M:%S') )
            gmt, vecmag_avg = datetime.datetime.now(), NaN
        else:
            self.change_status( '%d packets to process now %s' % (pkts.length, datetime.datetime.now().strftime('%d-%b-%Y,%j/%H:%M:%S')))
            vecmag_max, vecmag_avg, vecmag_std = pkts.get_accel_stats()
            seconds_packets_span = pkts.endTime - pkts.startTime
            gmtStart = unix2dtm(pkts.startTime)
            gmt = gmtStart + datetime.timedelta(seconds=seconds_packets_span/2.0)
            self.appendText('\nGMT %s; vecmag(max,mean,std) = (%.1f, %.1f, %.1f) ug; %.4fs seconds; %d records; %d packets' % (
                gmt,                            # GMT at "midpoint" of packets
                float(str(vecmag_max/1e-6)),    # vecmag's max value; numpy version bug requires float(str())
                float(str(vecmag_avg/1e-6)),    # vecmag's avg value; numpy version bug requires float(str())
                float(str(vecmag_std/1e-6)),    # vecmag's std value; numpy version bug requires float(str())
                seconds_packets_span,           # seconds spanned by packets
                np.shape(pkts.array)[0],        # number of records in packets
                pkts.length,                    # number of packets
                ))
            self.appendText('.')
            
        wx.CallAfter(self._graph_window.update_plot, gmt, vecmag_avg/1e-6)

    def run(self):
        """Run the worker thread."""
        displayHours =  0.5  # 0.1 is 6 minutes
        updateSeconds = 5
        dbti = DatabaseTimeIterator(displayHours=displayHours, updateSeconds=updateSeconds, host=self._notify_window.host, table=self._notify_window.table)
        self.appendText('\nSTART RUN: dispTime = %s, updateTime = %s' % (dbti.dispTime, dbti.updateTime))
        #####################################################################################
        # This is where our "data stream" begins in the form of database time iterator, which
        # would continue indefinitely unless user hits the stop button
        #####################################################################################
        for startTime, endTime in dbti:
            self.dbTimeRangeUpdate( dbti.dbMinTime.strftime('%d-%b-%Y,%j/%H:%M:%S'), dbti.dbMaxTime.strftime('%d-%b-%Y,%j/%H:%M:%S') )
            self.update_AOS()
            while ( endTime > datetime.datetime.now() ):
                if self._want_abort:
                    wx.PostEvent( self._notify_window, ResultEvent(None) ) # use a result of None to acknowledge the abort
                    return
                sleep(1)
            #wx.PostEvent( self._notify_window, ResultEvent( (startTime, endTime) ) )
            #print startTime, endTime
            self.processPackets(dbti.packets)

    def abort(self):
        """abort worker thread"""
        # Method for use by main thread to signal an abort
        self._want_abort = 1

class MainFrame(wx.Frame):
    """GUI Frame class that spins off the worker thread."""
    def __init__(self, *args, **kwargs):
        """Create the MainFrame."""
        parent, id, self.graphWindow = args[0], args[1], args[2]
        self.host = kwargs['host']
        self.table = kwargs['table']
        #title = os.path.basename(__file__)
        title = " ".join( (self.table, self.host) )
        wx.Frame.__init__(self, parent, id, title, size=(1200,1200))

        self.AOStext = wx.StaticText(self, -1, 'unknown')
        #self.AOStext.SetBackgroundColour(wx.BLACK)
        self.AOStext.SetForegroundColour(wx.BLACK)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add( self.AOStext )
        
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add( wx.Button(self, START_ID, 'Start') )
        btnSizer.Add( wx.Button(self, STOP_ID, 'Stop') )
        btnSizer.Add( wx.Button(self, SHOW_ID, 'TEST') )
        mainSizer.Add(btnSizer)

        self.text = wx.TextCtrl(self, -1, '', pos=(15,100), size=(1100,800), style=wx.TE_MULTILINE)
        self.text.WriteText('Ready.')        
        mainSizer.Add(self.text)

        self.Bind(wx.EVT_BUTTON, self.onStart, id=START_ID)
        self.Bind(wx.EVT_BUTTON, self.onStop, id=STOP_ID)
        self.Bind(wx.EVT_BUTTON, self.onTest, id=SHOW_ID)

        # Set up event handler for any worker thread results
        EVT_RESULT(self,self.onResult)

        # And indicate we don't have a worker thread yet
        self.worker = None

        # Status bar
        self.statusbar = self.CreateStatusBar(2, 0)        
        self.statusbar.SetStatusWidths([-1, 300])
        self.statusbar.SetStatusText("Ready", SB_LEFT)
        
        # Set up a timer to update the date/time (every few seconds)
        self.timer = wx.PyTimer(self.notify)
        self.timer.Start(SB_MSEC)
        self.notify() # - call it once right away

        # set main sizer
        self.SetSizer(mainSizer)
        mainSizer.Fit(self)

    def getTimeString(self):
        # FIXME this was lifted from Ted (accelPacket) -- this can be better
        t = localtime(time())
        return strftime('%d-%b-%Y,%j/%H:%M:%S ', t)

    def notify(self):
        """ Timer event """
        t = self.getTimeString() + ' (update every ' + str(int(SB_MSEC/1000.0)) + 's)'
        self.SetStatusText(t, SB_RIGHT)

    def update_AOS(self):
        c = str( parameters['aos_status'] )
        self.AOStext.SetLabel( c )
        if c.endswith('AOS'):
            self.AOStext.SetForegroundColour('dark green')
        else:
            self.AOStext.SetForegroundColour(wx.RED)

    def onTest(self, event):
        """test"""
        #print self.text.GetValue()
        #from random import choice
        #c = choice( ['AOS','LOS','WHAT'] )
        self.update_AOS()

    def auto_start(self):
        """Start Processing."""
        # Trigger the worker thread unless it's already busy        
        if not self.worker:
            self.SetStatusText('Starting worker thread computation.', SB_LEFT)
            self.worker = ProcessThread(self, self.graphWindow)

    def onStart(self, event):
        self.auto_start()

    def onStop(self, event):
        """Stop Processing."""
        # Flag the worker thread to stop if running
        if self.worker:
            self.SetStatusText('Trying to abort processing.', SB_LEFT)
            self.worker.abort()

    def onResult(self, event):
        """Show Result status."""
        if event.data is None:
            # Thread aborted (using our convention of None return)
            self.SetStatusText('Processing aborted.', SB_LEFT)
            self.text.WriteText('\nPROCESSING ABORTED AT %s' % datetime.datetime.now() )
        else:
            # Process results here
            self.SetStatusText( '%s %s' % event.data, SB_LEFT)
        # In either event, the worker is done
        self.worker = None

class MainApp(wx.App):
    """Class Main App."""
    def __init__(self, *args, **kwargs):
        self.host = kwargs['host']
        self.table = kwargs['table']
        wx.App.__init__(self, *args)
    
    def OnInit(self, *args, **kwargs):
        """Init Main App."""
        self.graphFrame = GraphFrame()
        self.frame = MainFrame(None, -1, self.graphFrame, host=self.host, table=self.table)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        self.graphFrame.Show()
        self.frame.auto_start()
        return True

def printUsage():
    """print short description of how to run the program"""
    print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def run_main_app(host, table):
    app = MainApp(0, host=host, table=table)
    app.MainLoop()
    
def main(argv):
    """describe what this routine does here"""
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parametersOK():
            run_main_app(parameters['host'], parameters['table'])
            return 0
    printUsage()  

if __name__ == '__main__':
    main(sys.argv)
