#!/usr/bin/env python

import wx
import datetime
from hypertreelist import HyperTreeListDemo


class ProbeHyperTreeList(HyperTreeListDemo):
    """add better title handling (with time) to AGW HyperTreeListDemo"""

    def __init__(self, *args, **kwargs):
        """Constructor for ProbeHyperTreeList"""
        title = kwargs.pop('title', 'untitled')
        super(ProbeHyperTreeList, self).__init__(*args, **kwargs)
        self.SetTitle(title)


def sys_time():
    utc = datetime.datetime.now()
    return utc


class Log(object):
    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        print text
    write = WriteText


def run_main():
    title = sys_time().strftime('%H:%M')
    app = wx.PySimpleApp()
    win = ProbeHyperTreeList(None, Log(), title=title)
    win.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    run_main()
