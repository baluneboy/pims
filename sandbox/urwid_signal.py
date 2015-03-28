#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import time
import urwid
import random
 
class ItemWidget (urwid.WidgetWrap):
 
    def __init__ (self, id, description):
        self.id = id
        self.content = 'item %s: %s...' % (str(id), description[:25])
        self.item = [
            ('fixed', 15, urwid.Padding(urwid.AttrWrap(
                urwid.Text('item %s' % str(id)), 'body', 'focus'), left=2)),
            urwid.AttrWrap(urwid.Text('%s' % description), 'body', 'focus'),
        ]
        w = urwid.Columns(self.item)
        self.__super.__init__(w)
 
    def selectable (self):
        return True
 
    def keypress(self, size, key):
        return key
 
def main ():
 
    palette = [
        ('body','dark blue', '', 'standout'),
        ('focus','light red', '', 'standout'),
        ('head','white', 'black'),
        ]
 
    lorem = [
        'Line one was a very good line.',
        'Two for the show.',
        'The third line.',
    ]
    
    def key_stroke (input):
        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()
 
        if input is 'enter':
            focus = listbox.get_focus()[0].content
            view.set_header(urwid.AttrWrap(urwid.Text('selected: %s' % str(focus)), 'head'))
 
    items = []
    for i in range(100):
        item = ItemWidget(i, random.choice(lorem))
        items.append(item)
 
    header = urwid.AttrMap(urwid.Text('selected:'), 'head')
    walker = urwid.SimpleListWalker(items)
    listbox = urwid.ListBox(walker)
    view = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header)
 
    def update():
        focus = listbox.get_focus()[0].content
        view.set_header(urwid.AttrWrap(urwid.Text('selected: %s' % str(focus)), 'head'))
 
    loop = urwid.MainLoop(view, palette, unhandled_input=key_stroke)
    urwid.connect_signal(walker, 'modified', update)
    loop.run()

if __name__ == '__main__':
    main()