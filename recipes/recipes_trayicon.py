#! /usr/bin/python
# small script to put a logout icon in system tray
# by Tunafish, july 2011
#
# parts taken from:
# http://www.dangibbs.co.uk/journal/advanced-functionality-of-eggtrayicon

import gtk, commands,os
try:
    import egg.trayicon
except:
    print "You need to install the python-eggtrayicon package"
 
class EggTrayIcon:
    def __init__(self):
        self.tray = egg.trayicon.TrayIcon("TrayIcon")
 
        eventbox = gtk.EventBox()
        image = gtk.Image()
        # http://www.pygtk.org/docs/pygtk/gtk-stock-items.html
        image.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_SMALL_TOOLBAR) # gtk.STOCK_YES, STOCK_NO, STOCK_MEDIA_RECORD
 
        eventbox.connect("button-press-event", self.icon_clicked)
 
        eventbox.add(image)
        self.tray.add(eventbox)
        self.tray.show_all()
 
    def icon_clicked(self, widget, event):
        if event.button == 1:
            print 'do something'   
    
        if event.button == 3:
            menu = gtk.Menu()
            menuitem_exit = gtk.MenuItem("Exit")
            menu.append(menuitem_exit)
            menuitem_exit.connect("activate", lambda w: gtk.main_quit())
            menu.show_all()
            menu.popup(None, None, None, event.button, event.time, self.tray)
 
EggTrayIcon()
gtk.main()