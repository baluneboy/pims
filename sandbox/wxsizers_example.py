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
    def __init__(self, parent, text, color, pos=wx.DefaultPosition, size=wx.DefaultSize):
        
        wx.PyWindow.__init__(self, parent, -1,
                             #style=wx.RAISED_BORDER
                             #style=wx.SUNKEN_BORDER
                             style=wx.SIMPLE_BORDER
                             )
        
        self.color = color
        self.text = text
        if size != wx.DefaultSize:
            self.bestsize = size
        else:
            self.bestsize = (194, 33)
        self.SetSize(self.GetBestSize())

        self.SetBackgroundColour(self.color)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_UP, self.OnCloseParent)

    def ShouldInheritColours(self):
        return False

    def OLDOnPaint(self, evt):
        sz = self.GetSize()
        dc = wx.PaintDC(self)
        w,h = dc.GetTextExtent(self.text)
        dc.Clear()
        dc.DrawText(self.text, (sz.width-w)/2, (sz.height-h)/2)

    def OnPaint(self, evt):
        sz = self.GetSize()
        dc = wx.PaintDC(self)
        w,h = dc.GetTextExtent(self.text)
        
        # Initialize the wx.BufferedPaintDC, assigning a background
        # colour and a foreground colour (to draw the text)
        backColour = self.GetBackgroundColour()
        backBrush = wx.Brush(backColour, wx.SOLID)
        dc.SetBackground(backBrush)
        dc.Clear()
        dc.SetTextForeground(wx.BLACK)
        dc.DrawText(self.text, (sz.width-w)/2, (sz.height-h)/2)
        
        #dc.SetFont(self.GetFont())

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
    box.Add(SmallWindow(win, "one", wx.RED), 0, wx.EXPAND)
    box.Add(SmallWindow(win, "two", wx.GREEN), 0, wx.EXPAND)
    box.Add(SmallWindow(win, "es06 333/55:66:99", wx.RED), 1, wx.EXPAND)
    box.Add(SmallWindow(win, "four", wx.RED), 1, wx.EXPAND)
    box.Add(SmallWindow(win, "five", wx.RED), 1, wx.EXPAND)
    box.Add(SmallWindow(win, "six", wx.RED), 1, wx.EXPAND)
    box.Add(SmallWindow(win, "seven", wx.RED), 1, wx.EXPAND)
    box.Add(SmallWindow(win, "eight", wx.RED), 1, wx.EXPAND)

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
