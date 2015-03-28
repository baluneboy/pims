#!/usr/bin/env python

#import wx
#from wx.lib.analogclock import *
#class MyFrame(wx.Dialog):
#    """use simple dialog box as frame"""
#    def __init__(self, parent, id, title):
#        wx.Dialog.__init__(self, parent, -4, title, size=(300,320))
#        self.SetBackgroundColour("blue")
#        clock = AnalogClockWindow(self)
#        clock.SetBackgroundColour("yellow")
#        
#        box = wx.BoxSizer(wx.VERTICAL)
#        box.Add(clock, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL|wx.SHAPED, 10)
#        self.SetAutoLayout(True)
#        self.SetSizer(box)
#        self.Layout()
#        
#        self.ShowModal()
#        self.Destroy()
#app = wx.PySimpleApp()
#frame = MyFrame(None, -1, "wx Analog Clock")
## show the frame
#frame.Show(True)
## start the event loop
#app.MainLoop()

import wx
import time
 
class MyForm(wx.Frame):
 
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Timer Tutorial 1", size=(500,500))
 
        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self, wx.ID_ANY)
 
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
 
        self.toggleBtn = wx.Button(panel, wx.ID_ANY, "Start")
        self.toggleBtn.Bind(wx.EVT_BUTTON, self.onToggle)
 
    def onToggle(self, event):        
        if self.timer.IsRunning():
            self.timer.Stop()
            self.toggleBtn.SetLabel("Start")
            print "timer stopped!"
        else:
            print "starting timer..."
            self.timer.Start(1000)
            self.toggleBtn.SetLabel("Stop")
 
    def update(self, event):
        print "\nupdated: ",
        print time.ctime()
 
# Run the program
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = MyForm().Show()
    app.MainLoop()