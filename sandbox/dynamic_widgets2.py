#!/usr/bin/env python
import wx
import wx.grid as gridlib
from wx.lib.pubsub import Publisher
import datetime
from pims.gui.iogrids import InputPanel, OutputPanel

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

class MainFrame(wx.Frame):
    """The parent frame for the i/o panels."""
    
    # Status bar constants
    SB_LEFT = 0
    SB_RIGHT = 1
    
    def __init__(self, log, input_grid, grid_worker, output_grid):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY, title='Add / Remove Grids')
 
        self.SetPosition( (1850, 22) )
        self.SetSize( (1533, 955) )
 
        self.grid_worker = grid_worker
 
        self.input_panel = InputPanel(self, log, input_grid, grid_worker)
        self.output_panel = OutputPanel(self, log, output_grid)
        self.output_panel.Hide()
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.input_panel, 1, wx.EXPAND)
        self.sizer.Add(self.output_panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        
        Publisher().subscribe(self.switch_panels, "switch")
        
        # menu bar
        menubar = wx.MenuBar()
        panelMenu = wx.Menu()
        self.panelMenu = panelMenu
        switch_panels_menu_item = panelMenu.Append(wx.ID_ANY, 
                                                  "Switch Panels", 
                                                  "Some text")
        self.Bind(wx.EVT_MENU, self.on_switch_panels, 
                  switch_panels_menu_item)
        
        menubar.Append(panelMenu, '&Panel')
        self.SetMenuBar(menubar)
        
        # Status bar
        self.statusbar = self.CreateStatusBar(2, 0)        
        self.statusbar.SetStatusWidths([-1, 320])
        self.statusbar.SetStatusText("Ready", self.SB_LEFT)
        
        # Set up a timer to update the date/time (every few seconds)
        self.update_sec = 5
        self.timer = wx.PyTimer(self.notify)
        self.timer.Start( int(self.update_sec * 1000) )
        self.notify() # call it once right away        
        
    def on_switch_panels(self, event):
        """"""
        id = event.GetId()
        self.switch_panels(id)
        
    def switch_panels(self, msg=None):
        """"""
        item = self.panelMenu.FindItemById(self.panelMenu.FindItem("Switch Panels"))
        if item:
            item.SetItemLabel("Go Input Panel")
        
        if self.input_panel.IsShown():
            self.SetTitle("Output Panel")
            self.input_panel.Hide()
            self.output_panel.Show()
            self.sizer.Layout()
            
            try:
                item = self.panelMenu.FindItemById(self.panelMenu.FindItem("Go Output Panel"))
                item.SetItemLabel("Go Input Panel")
            except:
                pass
            
        else:
            self.SetTitle("Input Panel")
            self.input_panel.Show()
            self.output_panel.Hide()
            
            item = self.panelMenu.FindItemById(self.panelMenu.FindItem("Go Input Panel"))
            item.SetItemLabel("Go Output Panel")
            
        #self.Fit()
        self.Layout()

    def get_time_str(self):
        return datetime.datetime.now().strftime('%d-%b-%Y,%j/%H:%M:%S ')

    def notify(self):
        """Timer event updated every so often."""
        #self.update_grid()
        t = self.get_time_str() + ' (update every ' + str(int(self.update_sec)) + 's)'
        self.statusbar.SetStatusText(t, self.SB_RIGHT)

#== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== 
def demo():
    import sys
    from pims.gui.tally_grid import CheapPadHoursInputGrid, TallyOutputGrid
    from pims.utils.gridworkers import CheapPadHoursGridWorker
    
    log = sys.stdout
    input_grid = CheapPadHoursInputGrid
    grid_worker = CheapPadHoursGridWorker
    output_grid = TallyOutputGrid

    app = wx.App(False)
    frame = MainFrame(log, input_grid, grid_worker, output_grid)
    frame.Show()
    app.MainLoop()

#== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== #== 
def easy_demo():
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()
    
#----------------------------------------------------------------------
if __name__ == "__main__":
    #easy_demo()
    demo()
