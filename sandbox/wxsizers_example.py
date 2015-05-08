#!/usr/bin/env python

import wx

class MainFrame(wx.Frame):

    def __init__(self, parent, title, sizer_func, worker):
        
        wx.Frame.__init__(self, parent, -1, title)

        p = wx.Panel(self, -1)

        self.sizer = sizer_func(p)
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
    def __init__(self, parent, text, pos=wx.DefaultPosition, size=wx.DefaultSize):
        
        wx.PyWindow.__init__(self, parent, -1,
                             #style=wx.RAISED_BORDER
                             #style=wx.SUNKEN_BORDER
                             style=wx.SIMPLE_BORDER
                             )
        
        self.text = text
        if size != wx.DefaultSize:
            self.bestsize = size
        else:
            self.bestsize = (194, 33)
        self.SetSize(self.GetBestSize())
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_UP, self.OnCloseParent)

    def OnPaint(self, evt):
        sz = self.GetSize()
        dc = wx.PaintDC(self)
        w,h = dc.GetTextExtent(self.text)
        dc.Clear()
        dc.DrawText(self.text, (sz.width-w)/2, (sz.height-h)/2)

    def OnSize(self, evt):
        self.Refresh()

    def OnCloseParent(self, evt):
        p = wx.GetTopLevelParent(self)
        if p:
            p.Close()            

    def DoGetBestSize(self):
        return self.bestsize
    
def make_box_of_small_windows(win):
    box = wx.BoxSizer(wx.HORIZONTAL)
    box.Add(SmallWindow(win, "one"), 0, wx.EXPAND)
    box.Add(SmallWindow(win, "two"), 0, wx.EXPAND)
    box.Add(SmallWindow(win, "es06 333/55:66:99"), 1, wx.EXPAND)
    box.Add(SmallWindow(win, "four"), 1, wx.EXPAND)
    box.Add(SmallWindow(win, "five"), 1, wx.EXPAND)
    box.Add(SmallWindow(win, "six"), 1, wx.EXPAND)
    box.Add(SmallWindow(win, "seven"), 1, wx.EXPAND)
    box.Add(SmallWindow(win, "eight"), 1, wx.EXPAND)

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

def demo(worker):
    app = wx.PySimpleApp()
    app.TopWindow = MainFrame(None, 'most recent db rt table timestamps', make_box_of_small_windows, worker)
    align_upper_right(app.TopWindow)
    app.TopWindow.Show()
    app.MainLoop()

if __name__ == "__main__":
    demo(sample_external_long_running)
