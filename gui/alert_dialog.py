#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import wxversion
wxversion.select('2.8')
import wx

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent

        # Vertical sizer:
        # Label above buttons
        # -----------------------------
        # Horizontal sizer for buttons
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Label above buttons
        label = wx.StaticText(self, -1, "This is a wx.Dialog")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        # Horizontal sizer for buttons
        box = wx.BoxSizer(wx.HORIZONTAL)

        # Add line to vertical sizer
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        #btnsizer = wx.StdDialogButtonSizer()
        
        btnsizer = wx.StdDialogButtonSizer()

        # The OK button.
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        self.Bind(wx.EVT_BUTTON, self.on_okay, btn)

        # The Show Log button.
        btn = wx.Button(self, -1, "Show Log")
        btnsizer.AddButton(btn)
        self.Bind(wx.EVT_BUTTON, self.on_show_log, btn)

        # Add box to sizer
        sizer.Add(btnsizer, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        self.SetSizer(sizer)
        sizer.Fit(self)

    def on_show_log(self, evt):
        self.Hide()
        #self.Destroy()
        wx.GetApp().ExitMainLoop()      
        
    def on_okay(self, evt):
        self.Hide()
        #self.Destroy()
        wx.GetApp().ExitMainLoop()        

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Alert Dialog", size=(240, 160))
        self.panel = Panel(self)
        self.CentreOnScreen()

class App(wx.App):
    def OnInit(self):
        frame = Frame()
        frame.Show(True)
        return True
    
    def OnExit(self):
        print 'bye'

def simple_gui():
    app = App(False)
    app.MainLoop()
    return 'simple_gui_output'

if __name__ == '__main__':
    simple_gui()
