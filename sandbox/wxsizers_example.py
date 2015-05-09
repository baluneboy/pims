#!/usr/bin/env python

import wx
import time

from pims.bigtime.timemachine import TimeGetter
from pims.utils.pimsdateutil import unix2dtm

class MainFrame(wx.Frame):

    def __init__(self, parent, title, sizer_func, tables, worker):
        
        wx.Frame.__init__(self, parent, -1, title)

        p = wx.Panel(self, -1)

        self.sizer = sizer_func(p, tables)
        #self.CreateStatusBar()
        #self.SetStatusText("Resize this frame to see how the sizers respond...")

        p.SetSizer(self.sizer)
        self.sizer.Fit(p)
        self.Bind(wx.EVT_CLOSE, self.on_close_window)
        self.Fit()

    def on_close_window(self, event):
        self.MakeModal(False)
        self.Destroy()

class SmallWindow(wx.PyWindow):
    """
    A small window that is used to show SAMS rt db table timestamp.
    """
    def __init__(self, parent, text, fgcolor=wx.BLACK, bgcolor=wx.WHITE, pos=wx.DefaultPosition, size=wx.DefaultSize):
        
        wx.PyWindow.__init__(self, parent, -1, style=wx.SIMPLE_BORDER)

        self.text = text        
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor

        if size != wx.DefaultSize:
            self.bestsize = size
        else:
            self.bestsize = (194, 33)
        self.SetSize(self.GetBestSize())

        self.SetBackgroundColour(self.bgcolor)
        self.SetForegroundColour(self.fgcolor)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_UP, self.OnCloseParent)

    def ShouldInheritColours(self):
        return False

    def OnPaint(self, evt):
        sz = self.GetSize()
        dc = wx.PaintDC(self)
        w,h = dc.GetTextExtent(self.text)
        
        # Initialize the wx.BufferedPaintDC, assigning a background
        # colour and a foreground colour (to draw the text)
        backColour = self.GetBackgroundColour()
        backBrush = wx.Brush(self.bgcolor, wx.SOLID)
        dc.SetBackground(backBrush)
        dc.Clear()
        dc.SetTextForeground(self.fgcolor)
        dc.DrawText(self.text, (sz.width-w)/2, (sz.height-h)/2)

    def OnSize(self, evt):
        self.Refresh()

    def OnCloseParent(self, evt):
        p = wx.GetTopLevelParent(self)
        if p:
            p.Close()            

    def DoGetBestSize(self):
        return self.bestsize

def make_box_of_small_windows(win, tables):
    box = wx.BoxSizer(wx.HORIZONTAL)
    for txt in tables:
        box.Add(SmallWindow(win, txt), 0, wx.EXPAND)
    return box

def align_upper_right(win):
    dw, dh = wx.DisplaySize()
    w, h = win.GetSize()
    x = dw - w + 55
    win.SetPosition((x, 0))

def say_hi():
    print 'hi'
    
def say_bye():
    print 'bye'

def sample_external_long_running(func, func_when_done, val=30):
    from time import sleep
    sleep(2)
    wx.CallAfter(func, val)
    sleep(2)
    wx.CallAfter(func, 2*val)
    sleep(1)
    wx.CallAfter(func, 3*val)
    sleep(3)
    wx.CallAfter(func_when_done)

def run(tables, worker):
    app = wx.PySimpleApp()
    app.TopWindow = MainFrame(None, 'most recent db rt table timestamps', make_box_of_small_windows, tables, worker)
    align_upper_right(app.TopWindow)
    app.TopWindow.Show()
    app.MainLoop()

if __name__ == "__main__":
    #tables = ['121f02rt', '121f03rt', '121f04rt', '121f05rt', '121f08rt', 'es03rt', 'es05rt', 'es06rt']
    #run(tables, sample_external_long_running)
    #
    rt_tables = [
        #    table   db host
        # -------------------------
        ('121f02rt', 'manbearpig'),
        ('121f03rt', 'manbearpig'),
        ('121f04rt', 'manbearpig'),
        ('121f05rt', 'manbearpig'),        
        ('121f08rt', 'manbearpig'),
        ('es03rt',   'manbearpig'),
        ('es05rt',   'manbearpig'),
        ('es06rt',   'manbearpig'),
    ]

    time_getters = []
    for table, dbhost in rt_tables:
        tg = TimeGetter(table, host=dbhost)
        time_getters.append(tg)
        
    for i in range(3):
        time.sleep(1)
        for tg in time_getters:
            ut = tg.get_time()
            if ut:
                print unix2dtm(tg.get_time()), tg.table
            #else:
            #    print None, tg.table
        print '-' * 22