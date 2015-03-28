#!/usr/bin/env python

import wx 
import os 

ID_ADD=100 
ID_BUTTON1 = 110 
ID_REM = 300 
ID_DES = 400 
ID_EXIT=200 

class MainWindow(wx.Frame): 
    def __init__(self,parent,id,title): 
        self.dirname='' 
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, style=wx.DEFAULT_FRAME_STYLE| 
                                        wx.NO_FULL_REPAINT_ON_RESIZE) 
        
        self.CreateStatusBar() # A Statusbar in the bottom of the window 
        
        # Setting up the menu. 
        filemenu= wx.Menu() 

        filemenu.Append(ID_ADD, "&Add buttons","") 
        filemenu.Append(ID_REM, "&Close buttons","") 
        filemenu.Append(ID_DES, "&Destroy buttons","") 
        filemenu.AppendSeparator() 
        filemenu.Append(ID_EXIT,"E&xit"," Terminate the program") 
        
        # Creating the menubar. 
        menuBar = wx.MenuBar() 
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar 
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content. 
        wx.EVT_MENU(self, ID_ADD, self.OnAdd) 
        wx.EVT_MENU(self, ID_EXIT, self.OnExit) 
        wx.EVT_MENU(self, ID_REM, self.OnRem) 
        wx.EVT_MENU(self, ID_DES, self.OnDes) 
        self.Show(1) 

    def OnExit(self,e): 
        self.Close(True)  # Close the frame. 


    def OnRem(self,e): 
        for i in range(0,6): 
            self.buttons[i].Close(True) 

    def OnAdd(self,e): 
        #add buttons 
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL) 
        self.buttons=[] 
        for i in range(0,6): 
            self.buttons.append(wx.Button(self, ID_BUTTON1+i, "Button &"+`i`)) 
            self.sizer2.Add(self.buttons[i],1,wx.EXPAND) 

        # Use some sizers to see layout options 
        self.sizer=wx.BoxSizer(wx.VERTICAL) 
        self.sizer.Add(self.sizer2,0,wx.EXPAND) 

        #Layout sizers 
        self.SetSizer(self.sizer) 
        self.SetAutoLayout(1) 
        self.sizer.Fit(self) 
    def OnDes(self,e): 
        for i in range(0,6): 
            self.buttons[i].Destroy() 


app = wx.PySimpleApp() 
frame = MainWindow(None, -1, "Sample editor") 
app.MainLoop() 