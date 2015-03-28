#!/usr/bin/env python
import wx
import wx.grid as gridlib
 
########################################################################
class MyPanel(wx.Panel):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        self.number_of_grids = 0
        self.frame = parent
 
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        controlSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.widgetSizer = wx.BoxSizer(wx.VERTICAL)
 
        self.addButton = wx.Button(self, label="Add")
        self.addButton.Bind(wx.EVT_BUTTON, self.onAddWidget)
        controlSizer.Add(self.addButton, 0, wx.CENTER|wx.ALL, 5)
 
        self.removeButton = wx.Button(self, label="Remove")
        self.removeButton.Bind(wx.EVT_BUTTON, self.onRemoveWidget)
        controlSizer.Add(self.removeButton, 0, wx.CENTER|wx.ALL, 5)
 
        self.mainSizer.Add(controlSizer, 0, wx.CENTER)
        self.mainSizer.Add(self.widgetSizer, 0, wx.CENTER|wx.ALL, 10)
 
        self.SetSizer(self.mainSizer)
 
    #----------------------------------------------------------------------
    def onAddWidget(self, event):
        """Add widget."""
        self.number_of_grids += 1
        label = "Grid %s" %  self.number_of_grids
        name = "grid%s" % self.number_of_grids
        new_grid = gridlib.Grid(self, -1)
        new_grid.CreateGrid(self.number_of_grids, self.number_of_grids)
        new_grid.SetCellValue(0, 0, label)
        self.widgetSizer.Add(new_grid, 0, wx.ALL, 5)
        self.frame.fSizer.Layout()
        self.frame.Fit()
 
    #----------------------------------------------------------------------
    def onRemoveWidget(self, event):
        """Remove widget."""
        if self.widgetSizer.GetChildren():
            self.widgetSizer.Hide(self.number_of_grids-1)
            self.widgetSizer.Remove(self.number_of_grids-1)
            self.number_of_grids -= 1
            self.frame.fSizer.Layout()
            self.frame.Fit()
 
########################################################################
class MyFrame(wx.Frame):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, parent=None, title="Add / Remove Grids")
        self.fSizer = wx.BoxSizer(wx.VERTICAL)
        panel = MyPanel(self)
        self.fSizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(self.fSizer)
        self.Fit()
        self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()
