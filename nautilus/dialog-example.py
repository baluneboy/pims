#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import os

def alert(msg):
    """Show a dialog with a simple message."""

    dialog = gtk.MessageDialog()
    dialog.set_markup(msg)
    dialog.run()

def main():
    selected = os.environ.get('NAUTILUS_SCRIPT_SELECTED_URIS', '')
    curdir = os.environ.get('NAUTILUS_SCRIPT_CURRENT_URI', os.curdir)
    
    if selected:
        targets = selected.splitlines()
    else:
        targets = [curdir]
    
    files = []
    directories = []
    
    for target in targets:
        if target.startswith('file:///'):
            target = target[7:]
        for dirname, dirnames, filenames in os.walk(target):
            for dirname in dirnames:
                directories.append(dirname)
            for filename in filenames:
                files.append(filename)

    alert('%s directories and %s files' %
          (len(directories),len(files)))

if __name__ == "__main__":
    main()