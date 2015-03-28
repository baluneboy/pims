#!/usr/bin/env python

import wx
import thread

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

class MainFrame(wx.Frame):

    def __init__(self, parent, worker):
        wx.Frame.__init__(self, parent)

        self.worker = worker
        self.label = wx.StaticText(self, label="Ready")
        self.btn = wx.Button(self, label="Start")
        self.gauge = wx.Gauge(self)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.label, proportion=1, flag=wx.EXPAND)
        self.sizer.Add(self.btn, proportion=0, flag=wx.EXPAND)
        self.sizer.Add(self.gauge, proportion=0, flag=wx.EXPAND)

        self.SetSizerAndFit(self.sizer)

        self.Bind(wx.EVT_BUTTON, self.on_button)

    def on_button(self, evt):
        self.btn.Enable(False)
        self.gauge.SetValue(0)
        self.label.SetLabel("Running")
        thread.start_new_thread( self.worker, (self.gauge.SetValue, self.on_long_run_done) )

    def on_long_run_done(self):
        self.gauge.SetValue(100)
        self.label.SetLabel("Done")
        self.btn.Enable(True)

def demo(worker):
    app = wx.PySimpleApp()
    app.TopWindow = MainFrame(None, worker)
    app.TopWindow.Show()
    app.MainLoop()

if __name__ == "__main__":
    demo(sample_external_long_running)
