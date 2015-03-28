#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------------
#An study of an paratemer-driven data-base component with wxPython
#By Jose Ney Meirelles Duarte -> jnduarte - at - microstart -dot- trix -dot- net
# Jan/2007

import  wx
import  wx.grid as  gridlib
import string

class DataBaseGrid(wx.grid.PyGridTableBase):
    #def mapel(self,e):
    #    return e
    def __init__(self, dataset, defaultsAppearance, coldefs):
        wx.grid.PyGridTableBase.__init__(self)

        self._data = dataset

        self.idgrid    = None
        self.CurrLine   = self.CurrCol = self.CurrVal = None

        #Establish a sef of default values:
        self.defAppear = defaultsAppearance
        self.defFont = None
        if self.defAppear.has_key("font"): self.defFont = self.defAppear["font"]
        self.defFontColor = None
        if self.defAppear.has_key("fontColor"): self.defFontColor = self.defAppear["fontColor"]
        self.DefaultHAlign = wx.ALIGN_LEFT
        if self.defAppear.has_key("DefaultHAlign"): self.DefaultHAlign = self.defAppear["DefaultHAlign"]
        self.DefaultVAlign = wx.ALIGN_CENTER
        if self.defAppear.has_key("DefaultVAlign"): self.DefaultVAlign = self.defAppear["DefaultVAlign"]
        self.DefaultRowSize = 25
        self.DefaultRowLabelSize = 0
        self.DefaultColSize = 50
        self.DefaultColLabelSize = 20
        self.DefaultEnableDragRowSize = False
        self.DefaultSelectionMode = 1
        self.DefaultEnableEditing = False
        self.OddBackgRowColour = "floral white"
        self.EvenBackgRowColour = "light grey"
        if self.defAppear is not None:
            if self.defAppear.has_key("DefaultRowSize"): self.DefaultRowSize = self.defAppear["DefaultRowSize"]
            if self.defAppear.has_key("RowLabelSize"): self.DefaultRowLabelSize = self.defAppear["RowLabelSize"]
            if self.defAppear.has_key("DefaultColSize"): self.DefaultColSize = self.defAppear["DefaultColSize"]
            if self.defAppear.has_key("ColLabelSize"): self.DefaultColLabelSize = self.defAppear["ColLabelSize"]
            if self.defAppear.has_key("EnableDragRowSize"): self.DefaultEnableDragRowSize = self.defAppear["EnableDragRowSize"]
            if self.defAppear.has_key("SelectionMode"): self.DefaultSelectionMode = self.defAppear["SelectionMode"]
            if self.defAppear.has_key("EnableEditing"): self.DefaultEnableEditing = self.defAppear["EnableEditing"]
            if self.defAppear.has_key("OddBackgRowColour"): self.OddBackgRowColour = self.defAppear[ "OddBackgRowColour" ]
            if self.defAppear.has_key("EvenBackgRowColour"): self.EvenBackgRowColour = self.defAppear[ "EvenBackgRowColour" ]

        #The Columns Individual Defs:
        self.cols     = coldefs
        self.ColsAttrs= self.CalcColsAttrs()

    #-----------------------------------------------------------------------------------------
    def CalcColsAttrs(self):
        """
        Calcs attrs for column cells, results in a list of tuples:
            colsAttrs = [ [even, odd], [even, odd], [even, odd], [even, odd] ]
        """
        self.calcAttrs = []
        for i in self.cols:
            self.oddAttr=gridlib.GridCellAttr()
            self.evenAttr=gridlib.GridCellAttr()
            flagA = False
            if i.has_key("colAlign"):
                if i["colAlign"][0] is not None and i["colAlign"][1] is not None:
                    self.oddAttr.SetAlignment(  i["colAlign"][0], i["colAlign"][1] )
                    self.evenAttr.SetAlignment( i["colAlign"][0], i["colAlign"][1] )
                    flagA = True
            if not flagA:
                self.oddAttr.SetAlignment(self.DefaultHAlign, self.DefaultVAlign )
                self.evenAttr.SetAlignment(self.DefaultHAlign, self.DefaultVAlign )
            flagA = flagB = flagC = False
            if i.has_key("defaulDefs"):
                if i["defaulDefs"]["Font"] is not None:
                    self.oddAttr.SetFont(  i["defaulDefs"]["Font"] )
                    self.evenAttr.SetFont( i["defaulDefs"]["Font"] )
                    flagA = True
                if i["defaulDefs"]["BkColour"] is not None:
                    self.oddAttr.SetBackgroundColour( i["defaulDefs"]["BkColour"] )
                    self.evenAttr.SetBackgroundColour(i["defaulDefs"]["BkColour"] )
                    flagB = True
                if i["defaulDefs"]["TxtColour"] is not None:
                    self.oddAttr.SetTextColour(  i["defaulDefs"]["TxtColour"] )
                    self.evenAttr.SetTextColour( i["defaulDefs"]["TxtColour"] )
                    flagC = True
            #Applies a global definitions, if column haveni't it:
            if (not flagA):
                self.oddAttr.SetFont(  self.defFont )
                self.evenAttr.SetFont( self.defFont )
            if (not flagB):
                self.oddAttr.SetBackgroundColour( self.OddBackgRowColour )
                self.evenAttr.SetBackgroundColour(self.EvenBackgRowColour )
            if (not flagC):
                self.oddAttr.SetTextColour(  self.defFontColor )
                self.evenAttr.SetTextColour( self.defFontColor )
            self.calcAttrs.append( (self.evenAttr, self.oddAttr) )
        return self.calcAttrs
    #-----------------------------------------------------------------------------------------

    def CalcCondicAttr(self, colattr, col, row, CurrVal):
        """A cell can have a conditional attributes, this is a great feature."""
        def evaluateCellCondition( condition, valor ):
            resultado = False
            if condition is not None:
                if condition.find("?") > -1 and valor is not None :
                    resultado = eval( condition.replace("?", valor) )
                else:
                    resultado = eval( condition )
            return resultado

        #locAttr = colattr # Robin Dunn said not to do this line, instead the next 2 lines
        locAttr = wx.grid.GridCellAttr() 
        locAttr.MergeWith(colattr)
        
        condition= self.cols[col]["condDefs"]["Condition"]
        if condition is not None:
            if evaluateCellCondition( condition, CurrVal ):
                if self.cols[col]["condDefs"]["Font"] is not None:
                    locAttr.SetFont(  self.cols[col]["condDefs"]["Font"] )
                if self.cols[col]["condDefs"]["BkColour"] is not None:
                    locAttr.SetBackgroundColour( self.cols[col]["condDefs"]["BkColour"][row % 2] )
                if self.cols[col]["condDefs"]["TxtColour"] is not None:
                    locAttr.SetTextColour(  self.cols[col]["condDefs"]["TxtColour"][row % 2] )
            else:
                #QUESTION: If the following line don't exists the conditional format is applied to all
                #subsequents cells of the column!
                #Have a more smart method to prevent is?
                self.ColsAttrs= self.CalcColsAttrs()
                return colattr
        return locAttr
        #-----------------------------------------------------------------------------------------

    def GetAttr(self, row, col, kind):
        self.CurrLine = row
        self.CurrCol  = col
        self.CurrVal  = self.GetValue(row, col)
        #OK, get a even/odd attrs for the column:
        attr = self.ColsAttrs[col][row % 2]
        #If the column has a conditional format, then evaluate it:
        if (self.cols[col].has_key("condDefs")):
            if self.cols[col]["condDefs"] is not None:
                attr = self.CalcCondicAttr( attr, col, row, self.CurrVal)
            else:
                #QUESTION: If the following line don't exists the conditional format is applied to all
                #subsequents cells of the column!
                #Have a more smart method to prevent is?
                attr = self.ColsAttrs[col][row % 2]
        attr.IncRef()
        return attr

    def clear(self):
        n = len(self._data)
        self._data = []
        if self.GetView() is not None:
            msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, 0, n)
            self.GetView().ProcessTableMessage(msg)

    def IsEmptyCell(self, row, col):
        lenval = 0
        val = self.GetValue(row,col)
        try:
            lenval = len(val.strip())
        except:
            val = `len(self.GetValue(row,col))`
            lenval = len(val.strip())
        if lenval == 0:
            return True
        else:
            return False

    def GetNumberRows(self):
        return len(self._data)

    def GetNumberCols(self):
        if len(self._data) > 0:
            return len( self._data[0] )
        else:
            return 0

    def GetValue(self, linha, coluna):
        return self._data[linha][coluna]

    def SetValue(self, linha, coluna, valor):
        self._data[linha][coluna] = valor

    def SetupColLabel(self, col):
        self.idgrid.SetColLabelValue( col, self.cols[col]["colLabel"] )
        if (self.cols[col]["colWidth"] is not None) and (self.cols[col]["colWidth"] > -1):
            self.idgrid.SetColSize( col, self.cols[col]["colWidth"] )
        if self.cols[col]["colAlign"] is None:
            self.idgrid.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
        else:
            self.idgrid.SetColLabelAlignment( self.cols[col]["colAlign"][0], self.cols[col]["colAlign"][1] )

    def GetColLabelValue(self, col):
        return self.cols[col]["colLabel"]

    def SetupGrid(self, grid):
        self.idgrid = grid
        grid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_CENTER )
        grid.SetDefaultColSize( self.DefaultColSize )
        grid.SetColLabelAlignment( wx.ALIGN_LEFT, wx.ALIGN_CENTER )
        grid.SetRowSize(      self.DefaultRowSize, False)
        grid.SetRowLabelSize(   self.DefaultRowLabelSize )
        grid.SetColSize(        self.DefaultColSize, False )
        grid.SetColLabelSize(   self.DefaultColLabelSize )
        grid.EnableDragRowSize( self.DefaultEnableDragRowSize)
        grid.EnableEditing(     self.DefaultEnableEditing )
        grid.SetSelectionMode(  self.DefaultSelectionMode )
        for i in range(len(self.cols)):
            self.SetupColLabel(i)

    def GetObject(self, row):
        return self._data[row]

    def AddObject(self, datarow):
        self._data.append(datarow)
        if self.GetView() is not None:
            msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, 1)
            self.GetView().ProcessTableMessage(msg)
        index = self.data.index(linhaDEdados)  #???
        self.GetView().SetGridCursor(index,0)



#===============================================================================================================
class Application(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        theWindow = wx.Frame(parent=None, id=-1, title='Data Grid from a List...')
        theWindow.SetSize((470, 400))
        theGrid = wx.grid.Grid(parent=theWindow, id=-1)

        defaultsAppearance={
                            "font": wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""),
                            "fontColor": "NAVY",
                            "DefaultHAlign": wx.ALIGN_LEFT,
                            "DefaultVAlign": wx.ALIGN_CENTER,
                            "DefaultRowSize": 30,
                            "RowLabelSize": 0,
                            "DefaultColSize": 50,
                            "ColLabelSize": 25,
                            "EnableDragRowSize": False,
                            "EnableEditing": True,
                            "SelectionMode": 1,
                            "OddBackgRowColour": "floral white",
                            "EvenBackgRowColour": "light grey"
                        }
        coldefs= [
                    {
                        "colLabel": u'Column One',
                        "colWidth": 350,
                        "colAlign": (wx.ALIGN_LEFT, wx.ALIGN_CENTER),
                        "defaultDefs": None,
                        "condDefs": None,
                    },
                    {
                        "colLabel": u'Other Column',
                        "colWidth": 100,
                        "colAlign": (wx.ALIGN_RIGHT, wx.ALIGN_BOTTOM),
                        "defaultDefs": None,
                        "condDefs": {"Condition": "('col2, 3'=='?') or ('col2, 7'=='?')",
                                    "Font": None,
                                    "BkColour": None,
                                    "TxtColour": ("RED","RED") },
                    }
                ]
        dataset = []
        for i in range(20):
            lind = [ "column-One" + `i` , "col2, " + `i` ]
            dataset.append(lind)
        dados = DataBaseGrid(dataset, defaultsAppearance, coldefs )
        theGrid.SetTable(dados)
        dados.SetupGrid(theGrid)
        theWindow.Show(True)
        self.SetTopWindow(theWindow)
    def OnInit(self):
        return True

app = Application()
app.MainLoop()
