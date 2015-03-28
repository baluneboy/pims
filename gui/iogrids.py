#!/usr/bin/env python

import sys
import wx
import wx.grid as gridlib
from wx.lib.pubsub import Publisher
import datetime

class InputPanel(wx.Panel):
    """The input panel."""
    
    def __init__(self, frame, log, input_grid, grid_worker):
        """Constructor"""
        wx.Panel.__init__(self, frame)
        self.frame = frame

        self.grid = input_grid(self, log)
        self.grid.CreateGrid( len(self.grid.row_labels), len(self.grid.column_labels) )
        
        self.grid.set_row_labels()
        self.grid.set_column_labels()
        self.grid.set_default_cell_values()  
        
        self.grid_worker = grid_worker
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.switch_btn = wx.Button(self, label="Show Outputs")
        self.switch_btn.Bind(wx.EVT_BUTTON, self.switchback)
        
        self.run_btn = wx.Button(self, label="Run")
        self.run_btn.Bind(wx.EVT_BUTTON, self.on_run)
        
        self.close_btn = wx.Button(self, label="Close")
        self.close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        
        self.btn_sizer.Add(self.switch_btn, 0, wx.ALL|wx.LEFT, 5)
        self.btn_sizer.Add(self.run_btn, 0, wx.ALL|wx.LEFT, 4)
        self.btn_sizer.Add(self.close_btn,0, wx.ALL|wx.LEFT, 4)
        self.main_sizer.Add(self.btn_sizer)
        self.main_sizer.Add(self.grid, 0, wx.EXPAND)
        self.SetSizer(self.main_sizer)
        
    def switchback(self, event):
        """Callback for panel switch button."""
        ## get inputs from input grid
        #inputs = self.grid.get_inputs()

        # now switch to outputs
        Publisher.sendMessage("switch", "message")

    def run(self):
        """Get inputs, then results, and update output grid."""
        # get inputs from input grid
        inputs = self.grid.get_inputs()
        
        # instantiate grid_worker with inputs
        gw = self.grid_worker(inputs)
        gw.get_results() # gets row_labels, column_labels, and rows
        
        # add more to inputs, which makes our outputs
        inputs['row_labels'] = gw.row_labels
        inputs['column_labels'] = gw.column_labels
        inputs['rows'] = gw.rows
        
        # update output grid with new results
        self.frame.output_panel.refresh_grid(results=inputs)

    def on_run(self, event):
        """Callback for run button."""
        self.run() # get results via input grid and grid_worker
        Publisher.sendMessage("switch", "message")
        
    def on_close(self, event):
        """Callback for close button."""
        #self.frame.statusbar.Destroy()
        self.frame.Destroy()
        sys.exit(0)

class StripChartInputPanel(InputPanel):
       
    def __init__(self, frame, log, input_grid, rt_params):
        """Constructor"""
        wx.Panel.__init__(self, frame)
        self.frame = frame
        self.rt_params = rt_params

        self.grid = input_grid(self, log, self.rt_params)
        self.grid.CreateGrid( len(self.grid.row_labels), len(self.grid.column_labels) )
        
        self.grid.set_row_labels()
        self.grid.set_column_labels()
        self.grid.set_default_cell_values()  
        
        #self.grid_worker = grid_worker
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.switch_btn = wx.Button(self, label="Show Outputs")
        self.switch_btn.Bind(wx.EVT_BUTTON, self.switchback)
        
        self.run_btn = wx.Button(self, label="Run")
        self.run_btn.Bind(wx.EVT_BUTTON, self.on_run)
        
        self.close_btn = wx.Button(self, label="Close")
        self.close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        
        self.btn_sizer.Add(self.switch_btn, 0, wx.ALL|wx.LEFT, 5)
        self.btn_sizer.Add(self.run_btn, 0, wx.ALL|wx.LEFT, 4)
        self.btn_sizer.Add(self.close_btn,0, wx.ALL|wx.LEFT, 4)
        self.main_sizer.Add(self.btn_sizer)
        self.main_sizer.Add(self.grid, 0, wx.EXPAND)
        self.SetSizer(self.main_sizer)    

class OutputPanel(wx.Panel):
    """The output panel."""
 
    def __init__(self, frame, log, output_grid):
        """Constructor"""
        wx.Panel.__init__(self, frame)
        self.frame = frame
        self.log = log        
        self.output_grid = output_grid
        self.output_grid.set_status_text = self.frame.set_status_text
        
        self.number_of_grids = 0
        self.frame = frame
 
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.widget_sizer = wx.BoxSizer(wx.VERTICAL)
 
        self.switch_btn = wx.Button(self, label="Show Inputs")
        self.switch_btn.Bind(wx.EVT_BUTTON, self.switchback)
        self.control_sizer.Add(self.switch_btn, 0, wx.LEFT|wx.ALL, 5)
 
        self.pause_btn = wx.Button(self, label="Pause")
        self.pause_btn.Bind(wx.EVT_BUTTON, self.on_pause)
        #self.pause_btn = wx.Button(self, label="Continue")
        #self.pause_btn.Bind(wx.EVT_BUTTON, self.on_continue)
        
        self.control_sizer.Add(self.pause_btn, 0, wx.LEFT|wx.ALL, 5)
 
        self.process_btn = wx.Button(self, label="Process Selected Cells")
        # we cannot bind the process button until the "add_grid" method happens
        self.control_sizer.Add(self.process_btn, 0, wx.LEFT|wx.ALL, 5)
        self.process_btn.Disable()
 
        self.main_sizer.Add(self.control_sizer, 0, wx.LEFT)
        self.main_sizer.Add(self.widget_sizer, 0, wx.LEFT|wx.ALL, 10)
 
        self.SetSizer(self.main_sizer)
 
    def switchback(self, event):
        """Callback for panel switch button."""
        Publisher.sendMessage("switch", "message")
 
    def refresh_grid(self, results=None):
        """Refresh grid with results."""
        self.remove_grid()
        self.add_grid(results=results)
 
    def add_grid(self, results=None):
        """Add grid."""
        if results:
            new_grid = self.output_grid(self, self.log, results)
            self.process_btn.Bind(wx.EVT_BUTTON, new_grid.process_selected_cells)
        else:
            # create a dummy grid if results is None
            new_grid = gridlib.Grid(self, -1)
            new_grid.CreateGrid(3, 3)
            new_grid.SetCellValue(0, 0, 'no results yet')
        self.widget_sizer.Add(new_grid, 0, wx.ALL, 5)
        self.frame.sizer.Layout()
        self.frame.Fit()        
 
    def remove_grid(self):
        """Remove grid."""
        if self.widget_sizer.GetChildren():
           self.widget_sizer.Hide(0)
           self.widget_sizer.Remove(0)
           self.frame.sizer.Layout()
           self.frame.Fit()
 
    def on_continue(self, event):
        """Continue."""
        self.frame.timer.Start()
        self.pause_btn.SetLabel('Pause')
        self.pause_btn.Bind(wx.EVT_BUTTON, self.on_pause)
        self.process_btn.Disable()
        self.frame.notify()
 
    def on_pause(self, event):
        """Pause."""
        self.frame.timer.Stop()
        self.frame.statusbar.SetStatusText('PAUSED', self.frame.SB_RIGHT)
        self.pause_btn.SetLabel('Continue')
        self.pause_btn.Bind(wx.EVT_BUTTON, self.on_continue)
        self.process_btn.Enable()

class MainFrame(wx.Frame):
    """The parent frame for the i/o panels."""
    
    # Status bar constants
    SB_LEFT = 0
    SB_RIGHT = 1
    
    def __init__(self, log, main_title, input_grid, grid_worker, output_grid):
        self.main_title = main_title
        wx.Frame.__init__(self, None, wx.ID_ANY, main_title + " Input Panel")
 
        self.SetPosition( (1850, 22) )
        self.SetSize( (1558, 955) )
 
        self.grid_worker = grid_worker
 
        self.input_panel = InputPanel(self, log, input_grid, grid_worker)
        self.output_panel = OutputPanel(self, log, output_grid)
        self.output_panel.Hide()
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.input_panel, 1, wx.EXPAND)
        self.sizer.Add(self.output_panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.output_panel.add_grid()
        
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
        self.set_status_text("Ready")
        
        # FIXME this does not change update_sec with input_grid value's changes
        # Set up a timer to update the date/time (every few seconds)
        self.update_sec = 10 #self.input_panel.grid.get_inputs()['update_sec']
        self.timer = wx.PyTimer(self.notify)
        self.timer.Start( int(self.update_sec * 1000) )
        self.notify() # call it once right away
        
        self.Maximize(True)
        
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
            self.SetTitle(self.main_title + " Output Panel")
            self.input_panel.Hide()
            self.output_panel.Show()
            self.sizer.Layout()
            
            try:
                item = self.panelMenu.FindItemById(self.panelMenu.FindItem("Go Output Panel"))
                item.SetItemLabel("Go Input Panel")
            except:
                pass
        else:
            self.SetTitle(self.main_title + " Input Panel")
            self.input_panel.Show()
            self.output_panel.Hide()
            
            item = self.panelMenu.FindItemById(self.panelMenu.FindItem("Go Input Panel"))
            item.SetItemLabel("Go Output Panel")
            
        self.Fit()
        self.Layout()

    def get_time_str(self):
        return datetime.datetime.now().strftime('%d-%b-%Y,%j/%H:%M:%S ')

    def notify(self):
        """Timer event updated every so often."""
        self.input_panel.run()
        t = self.get_time_str() + ' (update every ' + str(int(self.update_sec)) + 's)'
        self.statusbar.SetStatusText(t, self.SB_RIGHT)
    
    def set_status_text(self, s):
        """Set LEFT status text."""
        self.statusbar.SetStatusText(s, self.SB_LEFT)
    
if __name__ == "__main__":
    from pims.utils.gridworkers import demo1
    demo1()
