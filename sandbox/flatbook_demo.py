#!/usr/bin/env python

# TODO use this along with text in readme_ken.txt as upgrade to "pads" and "roadmaps" tally_grid.py
import wx
import os
import sys
import logging
from gridsimple_demo import SimpleGrid
import wx.lib.agw.flatnotebook as fnb

class MyFlatNotebook(fnb.FlatNotebook):

    def __init__(self, *args, **kwargs):
        self.log = kwargs.pop('log', sys.stdout)
        super(MyFlatNotebook, self).__init__(*args, **kwargs)

    def DeletePage(self, page):
        """not allowed in MyFlatNotebook"""
        self.log.debug( 'do not delete pages' )
    
class FlatNotebookDemo(wx.Frame):

    def __init__(self, parent, log):

        wx.Frame.__init__(self, parent, title="FlatNotebook Demo", size=(800,600))
        self.log = log

        self._bShowImages = False
        self._bVCStyle = False
        self._newPageCounter = 0

        self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        self.statusbar.SetStatusWidths([-2, -1])
        # statusbar fields
        statusbar_fields = [("FlatNotebook wxPython Demo, Andrea Gavana @ 02 Oct 2006"),
                            ("Welcome To wxPython!")]

        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)

        self.LayoutItems()

        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.OnPageClosing)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_DROPPED_FOREIGN, self.OnForeignDrop)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_DROPPED, self.OnDrop)


    def LayoutItems(self):

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(mainSizer)

        bookStyle = fnb.FNB_NODRAG

        self.book = MyFlatNotebook(self, wx.ID_ANY, agwStyle=bookStyle, log=self.log)
        
        # Add some pages to the first notebook
        self.Freeze()

        grid = SimpleGrid(self.book, self.log)
        self.book.AddPage(grid, "1st book Page 3 Grid FTW")
        
        text = wx.TextCtrl(self.book, -1, "First Book Page 2\n", style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.book.AddPage(text,  "Second Book Page 2")

        self.Thaw()         

        bookStyle &= ~(fnb.FNB_NODRAG)
        bookStyle |= fnb.FNB_ALLOW_FOREIGN_DND 
        self.secondBook = MyFlatNotebook(self, wx.ID_ANY, agwStyle=bookStyle, log=self.log)

        mainSizer.Add(self.book, 1, wx.EXPAND)

        # Add spacer between the books
        spacer = wx.Panel(self, -1)
        spacer.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))
        mainSizer.Add(spacer, 0, wx.ALL | wx.EXPAND)

        mainSizer.Add(self.secondBook, 1, wx.EXPAND)

        # Add some pages to the second notebook
        self.Freeze()

        grid = SimpleGrid(self.secondBook, self.log)
        self.secondBook.AddPage(grid, "2nd book Page 3 Grid FTW")
        
        text = wx.TextCtrl(self.secondBook, -1, "Second Book Page 1\n", style=wx.TE_MULTILINE|wx.TE_READONLY)  
        self.secondBook.AddPage(text, "Second Book Page 1")

        text = wx.TextCtrl(self.secondBook, -1, "Second Book Page 2\n", style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.secondBook.AddPage(text,  "Second Book Page 2")

        self.Thaw() 

        mainSizer.Layout()
        self.SendSizeEvent()


    def OnStyle(self, event):

        style = self.book.GetAGWWindowStyleFlag()
        eventid = event.GetId()

        if eventid == MENU_HIDE_NAV_BUTTONS:
            if event.IsChecked():            
                # Hide the navigation buttons
                style |= fnb.FNB_NO_NAV_BUTTONS
            else:
                style &= ~fnb.FNB_NO_NAV_BUTTONS
                style &= ~fnb.FNB_DROPDOWN_TABS_LIST

            self.book.SetAGWWindowStyleFlag(style)

        elif eventid == MENU_HIDE_ON_SINGLE_TAB:
            if event.IsChecked():
                # Hide the navigation buttons
                style |= fnb.FNB_HIDE_ON_SINGLE_TAB
            else:
                style &= ~(fnb.FNB_HIDE_ON_SINGLE_TAB)
                
            self.book.SetAGWWindowStyleFlag(style)
                
        elif eventid == MENU_HIDE_TABS:
            if event.IsChecked():
                # Hide the tabs
                style |= fnb.FNB_HIDE_TABS
            else:
                style &= ~(fnb.FNB_HIDE_TABS)

            self.book.SetAGWWindowStyleFlag(style)

        elif eventid == MENU_HIDE_X:
            if event.IsChecked():
                # Hide the X button
                style |= fnb.FNB_NO_X_BUTTON
            else:
                if style & fnb.FNB_NO_X_BUTTON:
                    style ^= fnb.FNB_NO_X_BUTTON

            self.book.SetAGWWindowStyleFlag(style)

        elif eventid == MENU_DRAW_BORDER:
            if event.IsChecked():
                style |= fnb.FNB_TABS_BORDER_SIMPLE
            else:
                if style & fnb.FNB_TABS_BORDER_SIMPLE:
                    style ^= fnb.FNB_TABS_BORDER_SIMPLE

            self.book.SetAGWWindowStyleFlag(style)

        elif eventid == MENU_USE_MOUSE_MIDDLE_BTN:
            if event.IsChecked():
                style |= fnb.FNB_MOUSE_MIDDLE_CLOSES_TABS            
            else:
                if style & fnb.FNB_MOUSE_MIDDLE_CLOSES_TABS:
                    style ^= fnb.FNB_MOUSE_MIDDLE_CLOSES_TABS

            self.book.SetAGWWindowStyleFlag(style)

        elif eventid == MENU_USE_BOTTOM_TABS:
            if event.IsChecked():
                style |= fnb.FNB_BOTTOM
            else:
                if style & fnb.FNB_BOTTOM:
                    style ^= fnb.FNB_BOTTOM

            self.book.SetAGWWindowStyleFlag(style)
            self.book.Refresh()

        elif eventid == MENU_NO_TABS_FOCUS:
            if event.IsChecked():
                # Hide the navigation buttons
                style |= fnb.FNB_NO_TAB_FOCUS
            else:
                style &= ~(fnb.FNB_NO_TAB_FOCUS)

            self.book.SetAGWWindowStyleFlag(style)


    def OnQuit(self, event):

        self.Destroy()


    def OnDeleteAll(self, event):

        #self.book.DeleteAllPages()
        self.log.debug('do not delete all pages')
        event.Skip()


    def OnShowImages(self, event):

        self._bShowImages = event.IsChecked()


    def OnForeignDrop(self, event):

        self.log.debug('Foreign drop received\n')
        self.log.debug('new NB: %s  ||  old NB: %s\n' % (event.GetNotebook(), event.GetOldNotebook()))
        self.log.debug('new tab: %s  ||  old tab: %s\n' % (event.GetSelection(), event.GetOldSelection()))
        

    def OnDrop(self, event):

        self.log.debug('Drop received - same notebook\n')
        self.log.debug('new: %s old: %s\n' % (event.GetSelection(), event.GetOldSelection()))


    def OnFF2Style(self, event):

        style = self.book.GetAGWWindowStyleFlag()

        # remove old tabs style
        mirror = ~(fnb.FNB_VC71 | fnb.FNB_VC8 | fnb.FNB_FANCY_TABS | fnb.FNB_FF2 | fnb.FNB_RIBBON_TABS)
        style &= mirror

        style |= fnb.FNB_FF2

        self.book.SetAGWWindowStyleFlag(style)


    def OnVC71Style(self, event):

        style = self.book.GetAGWWindowStyleFlag()

        # remove old tabs style
        mirror = ~(fnb.FNB_VC71 | fnb.FNB_VC8 | fnb.FNB_FANCY_TABS | fnb.FNB_FF2 | fnb.FNB_RIBBON_TABS)
        style &= mirror

        style |= fnb.FNB_VC71

        self.book.SetAGWWindowStyleFlag(style)


    def OnVC8Style(self, event):

        style = self.book.GetAGWWindowStyleFlag()

        # remove old tabs style
        mirror = ~(fnb.FNB_VC71 | fnb.FNB_VC8 | fnb.FNB_FANCY_TABS | fnb.FNB_FF2 | fnb.FNB_RIBBON_TABS)
        style &= mirror

        # set new style
        style |= fnb.FNB_VC8

        self.book.SetAGWWindowStyleFlag(style)
        
    def OnRibbonStyle(self, event):

        style = self.book.GetAGWWindowStyleFlag()

        # remove old tabs style
        mirror = ~(fnb.FNB_VC71 | fnb.FNB_VC8 | fnb.FNB_FANCY_TABS | fnb.FNB_FF2 | fnb.FNB_RIBBON_TABS)
        style &= mirror

        # set new style
        style |= fnb.FNB_RIBBON_TABS

        self.book.SetAGWWindowStyleFlag(style)


    def OnDefaultStyle(self, event):

        style = self.book.GetAGWWindowStyleFlag()

        # remove old tabs style
        mirror = ~(fnb.FNB_VC71 | fnb.FNB_VC8 | fnb.FNB_FANCY_TABS | fnb.FNB_FF2 | fnb.FNB_RIBBON_TABS)
        style &= mirror

        self.book.SetAGWWindowStyleFlag(style)


    def OnFancyStyle(self, event):

        style = self.book.GetAGWWindowStyleFlag()

        # remove old tabs style
        mirror = ~(fnb.FNB_VC71 | fnb.FNB_VC8 | fnb.FNB_FANCY_TABS | fnb.FNB_FF2 | fnb.FNB_RIBBON_TABS)
        style &= mirror

        style |= fnb.FNB_FANCY_TABS
        self.book.SetAGWWindowStyleFlag(style)
        

    def OnSelectColour(self, event):

        eventid = event.GetId()

        # Open a colour dialog
        data = wx.ColourData()

        dlg = wx.ColourDialog(self, data)

        if dlg.ShowModal() == wx.ID_OK:

            if eventid == MENU_SELECT_GRADIENT_COLOUR_BORDER:
                self.book.SetGradientColourBorder(dlg.GetColourData().GetColour())
            elif eventid == MENU_SELECT_GRADIENT_COLOUR_FROM:
                self.book.SetGradientColourFrom(dlg.GetColourData().GetColour())
            elif eventid == MENU_SELECT_GRADIENT_COLOUR_TO:
                self.book.SetGradientColourTo(dlg.GetColourData().GetColour())
            elif eventid == MENU_SET_ACTIVE_TEXT_COLOUR:
                self.book.SetActiveTabTextColour(dlg.GetColourData().GetColour())
            elif eventid == MENU_SELECT_NONACTIVE_TEXT_COLOUR:
                self.book.SetNonActiveTabTextColour(dlg.GetColourData().GetColour())
            elif eventid == MENU_SET_ACTIVE_TAB_COLOUR:
                self.book.SetActiveTabColour(dlg.GetColourData().GetColour())
            elif eventid == MENU_SET_TAB_AREA_COLOUR:
                self.book.SetTabAreaColour(dlg.GetColourData().GetColour())

            self.book.Refresh()


    def OnAddPage(self, event):

        caption = "New Page Added #" + str(self._newPageCounter)

        self.Freeze()

        image = -1
        if self._bShowImages:
            image = random.randint(0, self._ImageList.GetImageCount()-1)

        self.book.AddPage(self.CreatePage(caption), caption, True, image)
        self.Thaw()
        self._newPageCounter = self._newPageCounter + 1


    def CreatePage(self, caption):

        p = wx.Panel(self.book)
        wx.StaticText(p, -1, caption, (20,20))
        wx.TextCtrl(p, -1, "", (20,40), (150,-1))
        return p


    def OnDeletePage(self, event):
        #self.book.DeletePage(self.book.GetSelection())
        event.Skip()

    def OnSetSelection(self, event):

        dlg = wx.TextEntryDialog(self, "Enter Tab Number to select:", "Set Selection")

        if dlg.ShowModal() == wx.ID_OK:

            val = dlg.GetValue()
            self.book.SetSelection(int(val))


    def OnEnableTab(self, event):

        dlg = wx.TextEntryDialog(self, "Enter Tab Number to enable:", "Enable Tab")

        if dlg.ShowModal() == wx.ID_OK:

            val = dlg.GetValue()
            self.book.EnableTab(int(val))   


    def OnDisableTab(self, event):

        dlg = wx.TextEntryDialog(self, "Enter Tab Number to disable:", "Disable Tab")

        if dlg.ShowModal() == wx.ID_OK:

            val = dlg.GetValue()
            self.book.EnableTab(int(val), False)    


    def OnEnableDrag(self, event):

        style = self.book.GetAGWWindowStyleFlag()
        style2 = self.secondBook.GetAGWWindowStyleFlag()

        if event.IsChecked():        
            if style & fnb.FNB_NODRAG:
                style ^= fnb.FNB_NODRAG
            if style2 & fnb.FNB_NODRAG:
                style2 ^= fnb.FNB_NODRAG
        else:
            style |= fnb.FNB_NODRAG
            style2 |= fnb.FNB_NODRAG

        self.book.SetAGWWindowStyleFlag(style)
        self.secondBook.SetAGWWindowStyleFlag(style2)


    def OnAllowForeignDnd(self, event): 

        style = self.book.GetAGWWindowStyleFlag()
        if event.IsChecked():
            style |= fnb.FNB_ALLOW_FOREIGN_DND 
        else:
            style &= ~(fnb.FNB_ALLOW_FOREIGN_DND)

        self.book.SetAGWWindowStyleFlag(style)
        self.book.Refresh() 


    def OnSetAllPagesShapeAngle(self, event):


        dlg = wx.TextEntryDialog(self, "Enter an inclination of header borders (0-15):", "Set Angle")
        if dlg.ShowModal() == wx.ID_OK:

            val = dlg.GetValue()
            self.book.SetAllPagesShapeAngle(int(val))


    def OnSetPageImage(self, event):

        dlg = wx.TextEntryDialog(self, "Enter an image index (0-%i):"%(self.book.GetImageList().GetImageCount()-1), "Set Image Index")
        if dlg.ShowModal() == wx.ID_OK:
            val = dlg.GetValue()
            self.book.SetPageImage(self.book.GetSelection(), int(val))


    def OnAdvanceSelectionFwd(self, event):

        self.book.AdvanceSelection(True)


    def OnAdvanceSelectionBack(self, event):

        self.book.AdvanceSelection(False)


    def OnPageChanging(self, event):

        self.log.debug("Page Changing From %d To %d" % (event.GetOldSelection(), event.GetSelection()))
        event.Skip()


    def OnPageChanged(self, event):

        self.log.debug("Page Changed To %d" % event.GetSelection())
        event.Skip()


    def OnPageClosing(self, event):

        self.log.debug("Page NOT Closing, Selection: %d" % event.GetSelection())
        event.Skip()


    def OnDrawTabX(self, event):

        style = self.book.GetAGWWindowStyleFlag()
        if event.IsChecked():
            style |= fnb.FNB_X_ON_TAB
        else:
            if style & fnb.FNB_X_ON_TAB:
                style ^= fnb.FNB_X_ON_TAB       

        self.book.SetAGWWindowStyleFlag(style)


    def OnDClickCloseTab(self, event):

        style = self.book.GetAGWWindowStyleFlag()
        if event.IsChecked():       
            style |= fnb.FNB_DCLICK_CLOSES_TABS
        else:
            style &= ~(fnb.FNB_DCLICK_CLOSES_TABS)      

        self.book.SetAGWWindowStyleFlag(style)


    def OnGradientBack(self, event):

        style = self.book.GetAGWWindowStyleFlag()
        if event.IsChecked():
            style |= fnb.FNB_BACKGROUND_GRADIENT
        else:
            style &= ~(fnb.FNB_BACKGROUND_GRADIENT)

        self.book.SetAGWWindowStyleFlag(style)
        self.book.Refresh()


    def OnColourfulTabs(self, event):

        style = self.book.GetAGWWindowStyleFlag()
        if event.IsChecked():
            style |= fnb.FNB_COLOURFUL_TABS
        else:
            style &= ~(fnb.FNB_COLOURFUL_TABS)

        self.book.SetAGWWindowStyleFlag(style)
        self.book.Refresh()


    def OnSmartTabs(self, event):

        style = self.book.GetAGWWindowStyleFlag()
        if event.IsChecked():
            style |= fnb.FNB_SMART_TABS
        else:
            style &= ~fnb.FNB_SMART_TABS

        self.book.SetAGWWindowStyleFlag(style)
        self.book.Refresh()


    def OnDropDownArrow(self, event):

        style = self.book.GetAGWWindowStyleFlag()

        if event.IsChecked():

            style |= fnb.FNB_DROPDOWN_TABS_LIST
            style |= fnb.FNB_NO_NAV_BUTTONS

        else:

            style &= ~fnb.FNB_DROPDOWN_TABS_LIST
            style &= ~fnb.FNB_NO_NAV_BUTTONS

        self.book.SetAGWWindowStyleFlag(style)
        self.book.Refresh()


    def OnHideNavigationButtonsUI(self, event):

        style = self.book.GetAGWWindowStyleFlag()
        event.Check((style & fnb.FNB_NO_NAV_BUTTONS and [True] or [False])[0])


    def OnDropDownArrowUI(self, event):

        style = self.book.GetAGWWindowStyleFlag()
        event.Check((style & fnb.FNB_DROPDOWN_TABS_LIST and [True] or [False])[0])


    def OnAllowForeignDndUI(self, event): 

        style = self.book.GetAGWWindowStyleFlag()
        event.Enable((style & fnb.FNB_NODRAG and [False] or [True])[0])


    def OnAbout(self, event):

        msg = "This Is Not The About Dialog Of The FlatNotebook Demo.\n\n" + \
            "Author: Andrea Gavana @ 02 Oct 2006\n\n" + \
            "Please Report Any Bug/Requests Of Improvements\n" + \
            "To Me At The Following Adresses:\n\n" + \
            "andrea.gavana@gmail.com\n" + "gavana@kpo.kz\n\n" + \
            "Based On Eran C++ Implementation (wxWidgets Forum).\n\n" + \
            "Welcome To wxPython " + wx.VERSION_STRING + "!!"

        dlg = wx.MessageDialog(self, msg, "FlatNotebook wxPython Demo",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()        

class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent, -1)

        b = wx.Button(self, -1, " Test FlatNotebook ", (50,50))
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)


    def OnButton(self, evt):
        self.win = FlatNotebookDemo(self, self.log)
        self.win.Show(True)

def runTest(frame, nb, log):
    win = TestPanel(nb, log)
    return win

class MainFrame(wx.Frame):
    """main frame (window)"""
    def __init__(self, title):
        self.title = title
        wx.Frame.__init__(self, None, -1, self.title)

def get_log(level):
    logFormatter = logging.Formatter("%(asctime)s %(threadName)-12.12s %(levelname)-5.5s %(message)s")
    log = logging.getLogger('pims.sandbox.flatbook_demo')
    log.setLevel( getattr(logging, level.upper()) )
    fileHandler = logging.FileHandler("{0}/{1}.log".format('/tmp', 'pims_sandbox_flatbookdemo'))
    fileHandler.setFormatter(logFormatter)
    log.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    log.addHandler(consoleHandler)
    log.info('Logging started.')
    return log

def demo(level):
    log = get_log(level)
    app = wx.PySimpleApp()
    main_frame = MainFrame('title')
    app.frame = FlatNotebookDemo(main_frame, log)
    app.frame.Show()
    app.MainLoop()     

if __name__ == '__main__':
    demo('debug')
