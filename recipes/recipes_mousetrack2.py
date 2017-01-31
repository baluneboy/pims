#!/usr/bin/env python

import sys
import wx
from pymouse import PyMouseEvent

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=(300, 300))
        self.align_to_bottom_right()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_title)
        self.timer.Start(40)  # in miliseconds

    def align_to_bottom_right(self):
        dw, dh = wx.DisplaySize()
        w, h = self.GetSize()
        x = dw - w
        y = dh - h
        self.SetPosition((x, y))

    def update_title(self, event):
        pos = wx.GetMousePosition()
        self.SetTitle("Your mouse is at (%s, %s)" % (pos.x, pos.y))

app = wx.App(redirect=False)
top = Frame()
top.Show()
app.MainLoop()

class MouseClickEvent(PyMouseEvent):
    def __init__(self):
        PyMouseEvent.__init__(self)

    def move(self, x, y):
        print "Mouse moved to", x, y
        self.pos = (x, y)

    def click(self, x, y, button, press):
        if button == 1:
            if press:
                print "Mouse pressed at", x, y, "with button", button
            else:
                print "Mouse released at", x, y, "with button", button
        else:  # Exit if any other mouse button used
            self.stop()

mouse_click_evt = MouseClickEvent()
mouse_click_evt.run()

######!/usr/bin/env python
#####
#####import wx
#####
#####class Frame(wx.Frame):
#####     def __init__(self):
#####        wx.Frame.__init__(self, None, size=(300, 300))
#####        myCursor= wx.StockCursor(wx.CURSOR_CROSS)
#####        self.SetCursor(myCursor)
#####        self.timer = wx.Timer(self)
#####        self.Bind(wx.EVT_TIMER, self.update_title)
#####        self.timer.Start(20)  # in milliseconds
#####
#####     def update_title(self, event):
#####        pos = wx.GetMousePosition()
#####        self.SetTitle("Your mouse is at (%s, %s)" % (pos.x, pos.y))
#####
#####app = wx.App(redirect=False)
#####top = Frame()
#####top.Show()
#####app.MainLoop()


###def mousy(win, sensor='121f03', delay=500):
###    w, h = win.GetSizeTuple()
###    x, y = win.GetPositionTuple()
###    win.SetTitle( "{0:+4f}, {1:+4f}, {2:+4f}, {3:+4f}, {4:s}, {5:d}".format(x, y, w, h, sensor, delay) )
###
###app = wx.PySimpleApp()
###frame = wx.Frame(None, title="A Bit Mousy!")
###frame.Show()
###frame.Bind(wx.EVT_LEFT_DOWN, lambda e:wx.CallAfter(mousy, frame))
###app.SetTopWindow(frame)
###app.MainLoop()
