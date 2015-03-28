#!/usr/bin/env python

from numpy import arange, sin, pi, dot, array, sqrt, transpose, searchsorted
from scipy.io import wavfile

import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.pyplot import *

import wx

class Param:
    def __init__(self, name, min, max, default, step):
        #cbtn = wx.Button(self, label='Close', pos=(20, 30))
        #cbtn.Bind(wx.EVT_BUTTON, self.OnClose)
        self.name = name
        self.min = min
        self.max = max
        self.default = default
        self.step = step
        self.value = default
        
    def setValue(self, val):        
        print('%s = %f' % (self.name, val))
        self.value = val

class Data:
    def __init__(self, name, bin=1):
        self.name = name
        self.bin = bin
        self.data = []
        self.offset = []
        
    def add(self, offset, data):
        self.offset.append(offset)
        self.data.append(data)

class DataSet:
    def __init__(self, name, raw):
        self.data = {}
        self.name = name
        self.raw = raw
    
    def add(self, data):
        self.data[data.name] = data

class ParamPanel(wx.Panel):
    def __init__(self, parent, processor, listener):
        wx.Panel.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        
        btn3 = wx.Button(self, label='File', size=(70, 30))
        btn3.Bind(wx.EVT_BUTTON, self.OnFile)
        hbox5.Add(btn3, border=5)
        self.fname = wx.TextCtrl(self)
        hbox5.Add(self.fname, proportion=1, border=5)
        
        btn1 = wx.Button(self, label='Run', size=(70, 30))
        btn1.Bind(wx.EVT_BUTTON, self.OnRun)
        hbox5.Add(btn1, flag=wx.LEFT|wx.BOTTOM, border=5)  

        btn1 = wx.Button(self, label='Step', size=(70, 30))
        btn1.Bind(wx.EVT_BUTTON, self.OnStep)
        hbox5.Add(btn1, flag=wx.LEFT|wx.BOTTOM, border=5)    

        btn1 = wx.Button(self, label='RunTo', size=(70, 30))
        btn1.Bind(wx.EVT_BUTTON, self.OnRunTo)
        hbox5.Add(btn1, flag=wx.LEFT|wx.BOTTOM, border=5)

        vbox.Add(hbox5, flag=wx.EXPAND|wx.ALIGN_RIGHT|wx.RIGHT, border=10)

        vbox.Add((-1, 2))

        grid = wx.GridSizer(cols=3)

        self.paramList = processor.getParamList()
        self.paramField = []
        for param in self.paramList:
            hbox1 = wx.BoxSizer(wx.HORIZONTAL)
            st1 = wx.StaticText(self, label='%s (%.2f, %.2f, %.2f)' % (param.name, param.min, param.max, param.step))
            hbox1.Add(st1, flag=wx.RIGHT, border=8)
            tc = wx.TextCtrl(self)
            tc.SetValue('%.2f' % param.default)
            dict = {'param': param, 'field': tc}
            self.paramField.append(dict)
            hbox1.Add(tc, proportion=1)
            grid.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add(grid, flag=wx.EXPAND|wx.ALIGN_RIGHT|wx.RIGHT, border=10)

        self.SetSizer(vbox)        
        self.Fit()
        
        self.processor = processor
        self.listener = listener

    def save(self):
        import json

        data = [{'file':self.fname.Value}]
        for param in self.paramField:
            data.append({param['param'].name:param['field'].Value})

        data_string = json.dumps(data)

        print 'JSON:', data_string

        with open ('plotting.json', 'a') as f: f.write(data_string)

    def OnRun(self, e):
        
        for param in self.paramField:
            param['param'].setValue(float(param['field'].Value))
        
        dataSet = self.processor.run(self.fname.Value, self.paramList)
        self.listener.updateData(dataSet)

    def OnStep(self, e):
        
        for param in self.paramField:
            param['param'].setValue(float(param['field'].Value))
            
        if(self.processor.running == False):
            self.processor.start(self.fname.Value, self.paramList)
        
        dataSet = self.processor.step(self.paramList)
        self.listener.updateData(dataSet, True)

    def OnRunTo(self, e):

        for param in self.paramField:
            param['param'].setValue(float(param['field'].Value))

        dataSet = self.processor.run(self.fname.Value, self.paramList, self.listener.offset)
        self.listener.updateData(dataSet)

    def OnFile(self, e):        
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dialog = wx.FileDialog(None, 'Open', '*.wav', style=style)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
        else:
            path = None
        dialog.Destroy()
        self.fname.SetValue(path)
        self.save()

class CanvasPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.zoom = 5
        self.offset = 0
        self.resolution = 1000
        
        self.SetAutoLayout(1)

        self.sizer = wx.BoxSizer(wx.VERTICAL)       
 
        self.sld = wx.Slider(self, -1, self.offset, 0, 5000000 - self.zoom * self.resolution, wx.DefaultPosition, (-1, -1), wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.sld.SetLineSize(20)
        self.sld.Bind(wx.EVT_SCROLL, self.updateOffset)
      
        self.sizer.Add(self.sld, flag=wx.EXPAND, border=10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        sld = wx.Slider(self, -1, self.zoom, 1, 10, wx.DefaultPosition, (-1, -1), wx.SL_HORIZONTAL | wx.SL_LABELS)
        sld.SetLineSize(20)
        sld.Bind(wx.EVT_SCROLL, self.updateZoom)
        
        self.slice = wx.CheckBox(self, label='Slice')
        self.slice.SetValue(1)
        
        hbox.Add(self.slice, 1)
        hbox.Add(sld, 1)
        
        self.sizer.Add(hbox, flag=wx.EXPAND, border=10)

        self.figure = Figure()
        self.axes1 = self.figure.add_subplot(211)
        self.axes2 = self.figure.add_subplot(212)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()
        self.figure.tight_layout()
        self.canvas.mpl_connect('key_press_event', self.on_key)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)

        self.playline = self.axes1.plot([0, 0], [-1, 1], 'y.-')

    def draw(self):
        self.canvas.draw_idle()        
        
    def updateZoom(self, e):
        obj = e.GetEventObject()
        self.zoom = obj.GetValue()
        self.update()        

    def updateOffset(self, e):
        obj = e.GetEventObject()
        self.offset = obj.GetValue()
        self.update()

    def update(self):
        zoom = 2 << self.zoom
        x1 = self.offset - self.resolution/2
        x2 = self.offset + zoom * self.resolution - self.resolution/2
        self.axes1.axis([x1, x2, -1, 1])
        if(self.slice.Value == False):
            self.axes2.set_xlim([x1, x2])

        self.draw()

    def on_motion(self, event):
        if event.inaxes == self.axes1 and event.button is not None:
            xpos = event.xdata
            try:
                s = '%d' % xpos
                for data in self.dataSet.data.values() :
                    if data.bin == 1:
                        index = searchsorted(data.offset, xpos)
                        s = ('%s  %s=%.3f' % (s, data.name, data.data[index]))
                print(s)
            except:
                print(' %0.1f' % (xpos))

    def on_click(self, event):
        if event.inaxes == self.axes1:
            xpos = event.xdata
            try:
                s = 'clicked %d' % xpos
                print(s)
            except:
                print(' %0.1f' % (xpos))

    def on_key(self, event):
        if event.inaxes == self.axes1:
            xpos = event.xdata
            try:
                s = 'clicked %d' % xpos
                print(s)
            except:
                print(' %0.1f' % (xpos))

    def updateData(self, dataSet, stepping=False):
        self.axes1.cla()
        self.axes2.cla()
        self.sld.SetMax(dataSet.raw.size)
        
        colors = ['b', 'r', 'k', 'c']
        index1 = 0
        index2 = 0
        
        self.dataSet = dataSet
        
        t = range(0, dataSet.raw.size)
        self.axes1.plot(t, dataSet.raw, 'g', label='raw', alpha=0.5)

        self.playline = self.axes1.plot([self.offset, self.offset], [-1, 1], 'y.-')
        
        for data in dataSet.data.values():
            if data.bin == 1:
                s = array(data.data) * 1.0
                s = s / max(abs(s))
                self.axes1.plot(data.offset, s, colors[index1], label=data.name, ls='steps')
                index1 = index1 + 1
            else:
                y = range(0, data.bin)
                if(self.slice.Value == True or stepping == True):
                    self.axes2.plot(data.data[-1], colors[index2], label=data.name)
                    index2 = index2 + 1
                    self.axes2.autoscale()
                else:
                    self.axes2.pcolormesh(array(data.offset), array(y), transpose(data.data), cmap=cm.gray)                
        
        #self.curve1.set_ydata(s);
        self.axes1.grid(True, color = '0.7', linestyle='-', which='major', axis='both')
        self.axes1.grid(True, color = '0.9', linestyle='-', which='minor', axis='both')
        self.axes1.legend()
        self.axes1.set_title(dataSet.name)
        self.update()

class PlottingApp:
    def __init__(self, processor):        
        app = wx.PySimpleApp()
        fr = wx.Frame(None, -1, title='test', size=(640, 480))
        splitter = wx.SplitterWindow(fr, -1)
        panel1 = CanvasPanel(splitter)
        panel2 = ParamPanel(splitter, processor, panel1)
        splitter.SplitHorizontally(panel2, panel1, 10)  
        splitter.SetMinimumPaneSize(100)
        panel1.draw()
        fr.Show()
        app.MainLoop()

class Processor:
    def __init__(self):
        self.running = False
    
    def start(self, fname, paramList):
        sr, x = wavfile.read(fname)
        self.x = array(x) * 1.0 / max(x)

        self.t = int(paramList[0].value * sr / 1000)
        
        rms = Data('rms')
        self.offset = 0
        
        self.dataSet = DataSet('RMS', self.x)
        
        self.dataSet.add (Data('rms'))
        self.dataSet.add (Data('win', self.t))
        
        self.running = True
        
    def step(self, paramList, limit=-1):

        if(limit >= 0) :
            limit = min(limit, self.x.size)
        else:
            limit = self.x.size

        if (self.offset < limit - self.t):
            xnow = self.x[self.offset:(self.offset + self.t - 1)];
            x2 = dot(xnow, xnow)
            x2 = sqrt(x2 / self.t)
            self.dataSet.data['rms'].add(self.offset, x2)
            self.dataSet.data['win'].add(self.offset, xnow)
            self.offset = self.offset + self.t
            return self.dataSet
        else:
            return []
        
    def run(self, fname, paramList, limit=-1):
             
        if(self.running == False):   
            self.start(fname, paramList)
            
        while(self.step(paramList, limit) != []):
            paramList = paramList

        if(limit < 0) :
            self.running = False
        return self.dataSet 
    
    def getParamList(self):
        paramList = []
        paramList.append(Param('TIME', 1, 10, 10, 1))
        return paramList

if __name__ == "__main__":
    processor = Processor()
    plotting = PlottingApp(processor)