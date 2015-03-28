#!/usr/bin/env python

# Urwid example lazy directory browser / tree view
#    Copyright (C) 2004-2011  Ian Ward
#    Copyright (C) 2010  Kirk McDonald
#    Copyright (C) 2010  Rob Lanphier
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Urwid web site: http://excess.org/urwid/

"""
Urwid example lazy directory browser / tree view
Features:
- custom selectable widgets for files and directories
- custom message widgets to identify access errors and empty directories
- custom list walker for displaying widgets in a tree fashion
- outputs a quoted list of files and directories "selected" on exit
"""

import re
import os
import time
import fnmatch
import datetime
import itertools
import urwid

def find_files(top_dir, fname_pat):
    matches = []
    for root, dirnames, filenames in os.walk(top_dir):
      for filename in fnmatch.filter(filenames, fname_pat):
          matches.append(os.path.join(root, filename))
    return matches

class FlagFileWidget(urwid.TreeWidget):
    # apply an attribute to the expand/unexpand icons
    unexpanded_icon = urwid.AttrMap(urwid.TreeWidget.unexpanded_icon,
        'dirmark')
    expanded_icon = urwid.AttrMap(urwid.TreeWidget.expanded_icon,
        'dirmark')

    def __init__(self, node):
        self.__super.__init__(node)
        # insert an extra AttrWrap for our own use
        self._w = urwid.AttrWrap(self._w, None)
        self.flagged = False
        self.update_w()

    def selectable(self):
        return True

    def keypress(self, size, key):
        """allow subclasses to intercept keystrokes"""
        key = self.__super.keypress(size, key)
        if key:
            key = self.unhandled_keys(size, key)
        return key

    def unhandled_keys(self, size, key):
        """
        Override this method to intercept keystrokes in subclasses.
        Default behavior: Toggle flagged on space, ignore other keys.
        """
        if key == " ":
            self.flagged = not self.flagged
            self.update_w()
        else:
            return key

    def update_w(self):
        """Update the attributes of self.widget based on self.flagged.
        """
        if self.flagged:
            self._w.attr = 'flagged'
            self._w.focus_attr = 'flagged focus'
        else:
            self._w.attr = 'body'
            self._w.focus_attr = 'focus'

class FileTreeWidget(FlagFileWidget):
    """Widget for individual files."""
    def __init__(self, node):
        self.__super.__init__(node)
        path = node.get_value()
        add_widget(path, self)

    def get_display_text(self):
        return self.get_node().get_key()

    def unhandled_keys(self, size, key):
        """
        Overriding this method to intercept keystrokes in this subclasses.
        Default behavior WOULD HAVE BEEN: Toggle flagged on space, ignore other keys.
        """
        return key

class EmptyWidget(urwid.TreeWidget):
    """A marker for expanded directories with no contents."""
    def get_display_text(self):
        return ('flag', '(empty directory)')

class ErrorWidget(urwid.TreeWidget):
    """A marker for errors reading directories."""
    def get_display_text(self):
        return ('error', "(error/permission denied)")

class DirectoryWidget(FlagFileWidget):
    """Widget for a directory."""
    def __init__(self, node):
        self.__super.__init__(node)
        path = node.get_value()
        add_widget(path, self)
        self.expanded = starts_expanded(path)
        self.update_expanded_icon()

    def get_display_text(self):
        node = self.get_node()
        if node.get_depth() == 0:
            return "/"
        else:
            return node.get_key()
        
    def unhandled_keys(self, size, key):
        """
        Overriding this method to intercept keystrokes in this subclasses.
        Default behavior WOULD HAVE BEEN: Toggle flagged on space, ignore other keys.
        """
        node = self.get_node()
        if key == " ":
            self.flagged = not self.flagged
            self.update_w()
        else:
            return key
        
class FileNode(urwid.TreeNode):
    """Metadata storage for individual files"""

    def __init__(self, path, parent=None):
        depth = path.count(dir_sep())
        key = os.path.basename(path)
        urwid.TreeNode.__init__(self, path, key=key, parent=parent, depth=depth)

    def load_parent(self):
        parentname, myname = os.path.split(self.get_value())
        parent = DirectoryNode(parentname)
        parent.set_child_node(self.get_key(), self)
        return parent

    def load_widget(self):
        return FileTreeWidget(self)

class EmptyNode(urwid.TreeNode):
    def load_widget(self):
        return EmptyWidget(self)

class ErrorNode(urwid.TreeNode):
    def load_widget(self):
        return ErrorWidget(self)

class DirectoryNode(urwid.ParentNode):
    """Metadata storage for directories"""

    def __init__(self, path, parent=None):
        if path == dir_sep():
            depth = 0
            key = None
        else:
            depth = path.count(dir_sep())
            key = os.path.basename(path)
        urwid.ParentNode.__init__(self, path, key=key, parent=parent,
                                  depth=depth)

    def load_parent(self):
        parentname, myname = os.path.split(self.get_value())
        parent = DirectoryNode(parentname)
        parent.set_child_node(self.get_key(), self)
        return parent

    def load_child_keys(self):
        dirs = []
        files = []
        try:
            path = self.get_value()
            # separate dirs and files
            for a in os.listdir(path):
                if os.path.isdir(os.path.join(path,a)):
                    dirs.append(a)
                else:
                    files.append(a)
        except OSError, e:
            depth = self.get_depth() + 1
            self._children[None] = ErrorNode(self, parent=self, key=None,
                                             depth=depth)
            return [None]

        # sort dirs and files
        dirs.sort(key=alphabetize)
        files.sort(key=alphabetize)
        # store where the first file starts
        self.dir_count = len(dirs)
        # collect dirs and files together again
        keys = dirs + files
        if len(keys) == 0:
            depth=self.get_depth() + 1
            self._children[None] = EmptyNode(self, parent=self, key=None,
                                             depth=depth)
            keys = [None]
        return keys

    def load_child_node(self, key):
        """Return either a FileNode or DirectoryNode"""
        index = self.get_child_index(key)
        if key is None:
            return EmptyNode(None)
        else:
            path = os.path.join(self.get_value(), key)
            if index < self.dir_count:
                return DirectoryNode(path, parent=self)
            else:
                path = os.path.join(self.get_value(), key)
                return FileNode(path, parent=self)

    def load_widget(self):
        return DirectoryWidget(self)

class DirectoryBrowser(object):
    palette = [
        ('body', 'black', 'light gray'),
        ('flagged', 'black', 'dark green', ('bold','underline')),
        ('focus', 'light gray', 'dark blue', 'standout'),
        ('flagged focus', 'yellow', 'dark cyan',
                ('bold','standout','underline')),
        ('head', 'yellow', 'black', 'standout'),
        ('foot', 'light gray', 'black'),
        ('key', 'light cyan', 'black','underline'),
        ('title', 'white', 'black', 'bold'),
        ('dirmark', 'black', 'dark cyan', 'bold'),
        ('flag', 'dark gray', 'light gray'),
        ('error', 'dark red', 'light gray'),
        ]

    footer_text = [
        ('title', "Directory Browser"), "    ",
        ('key', "UP"), ",", ('key', "DOWN"), ",",
        ('key', "PAGE UP"), ",", ('key', "PAGE DOWN"),
        "  ",
        ('key', "SPACE"), "  ",
        ('key', "+"), ",",
        ('key', "-"), "  ",
        ('key', "LEFT"), "  ",
        ('key', "HOME"), "  ",
        ('key', "END"), "  ",
        ('key', "Q"),
        ]

    def __init__(self, alarm_sec=3):
        cwd = os.getcwd()
        store_initial_cwd(cwd)
        self.alarm_sec = alarm_sec
        self.treewalker = urwid.TreeWalker(DirectoryNode(cwd))
        self.listbox = urwid.TreeListBox(self.treewalker)
        self.listbox.offset_rows = 3
        self.header = self._get_header()
        self.footer = urwid.AttrWrap(urwid.Text(self.footer_text), 'foot')
        self.view = urwid.Frame(
            urwid.AttrWrap(self.listbox, 'body'),
            header=urwid.AttrWrap(self.header, 'head'),
            footer=self.footer)

    def _get_header(self):
        t1 = time.clock()
        
        # get flagged dirs
        flagged_dirs = get_flagged_names(just_dirs=True)
        count = 0
        for d in flagged_dirs:
            count += len( find_files(d, '*.aiff') )
        time_str = datetime.datetime.now().strftime('%H:%M:%S')
        
        # simulate long-running file system checking
        for junk in range(6234567): pass
        
        elapsed_sec = (time.clock() - t1)        
        s = time_str + ' (every %ds) urwid browsing' % self.alarm_sec
        s += '\n%d flagged dirs, %d files, elapsed = %.1fs' % (len(flagged_dirs), count, elapsed_sec)
        return urwid.Text(s)

    def loop_callback(self, main_loop_obj, user_data):
        self.header = self._get_header()
        self.view.set_header( urwid.AttrWrap(self.header, 'head') )
        self.loop.set_alarm_in(self.alarm_sec, self.loop_callback, user_data=None)        

    def main(self):
        """Run the program."""
        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.unhandled_input)
        self.loop.set_alarm_in(self.alarm_sec, self.loop_callback, user_data=None)
        self.loop.run()

        # on exit, write the flagged filenames to the console
        names = [escape_filename_sh(x) for x in get_flagged_names()]
        print " ".join(names)

    def unhandled_input(self, k):
        # update display of focus directory
        if k in ('q','Q'):
            raise urwid.ExitMainLoop()
        
        if k in ('u', 'U'):
            # get flagged names
            flagged_names = get_flagged_names()
            # get node structure
            node_with_focus = self.listbox.get_focus()[0].get_node()
            depth = node_with_focus.get_depth()
            s = [ str(depth) ]
            n = [ os.path.basename( node_with_focus.get_value() ) ]
            while depth > 0:
                parent_node = node_with_focus.load_parent()
                #self.listbox.set_focus(parent_node)
                depth = parent_node.get_depth()
                s.append( str(depth) )
                if parent_node.get_value() in flagged_names:
                    n.append( 'F' + os.path.basename( parent_node.get_value() ) )
                else:
                    n.append( os.path.basename( parent_node.get_value() ) )
                node_with_focus = parent_node
            footstr = '>'.join(s)
            footstr = '&'.join(n)
            self.footer = urwid.AttrWrap(urwid.Text(footstr), 'foot')
            self.view.set_footer( self.footer )         

def main():
    DirectoryBrowser().main()

#######
# global cache of widgets
_widget_cache = {}

def add_widget(path, widget):
    """Add the widget for a given path"""

    _widget_cache[path] = widget

def get_flagged_names(just_dirs=False):
    """Return a list of all items (files and/or directories) marked as flagged."""

    l = []
    for w in _widget_cache.values():
        if w.flagged:
            if just_dirs:
                if isinstance(w.get_node(), DirectoryNode):
                    l.append(w.get_node().get_value())
            else:
                l.append(w.get_node().get_value())
    return l

######
# store path components of initial current working directory
_initial_cwd = []

def store_initial_cwd(name):
    """Store the initial current working directory path components."""

    global _initial_cwd
    _initial_cwd = name.split(dir_sep())

def starts_expanded(name):
    """Return True if directory is a parent of initial cwd."""

    if name is '/':
        return True

    l = name.split(dir_sep())
    if len(l) > len(_initial_cwd):
        return False

    if l != _initial_cwd[:len(l)]:
        return False

    return True

def escape_filename_sh(name):
    """Return a hopefully safe shell-escaped version of a filename."""

    # check whether we have unprintable characters
    for ch in name:
        if ord(ch) < 32:
            # found one so use the ansi-c escaping
            return escape_filename_sh_ansic(name)

    # all printable characters, so return a double-quoted version
    name.replace('\\','\\\\')
    name.replace('"','\\"')
    name.replace('`','\\`')
    name.replace('$','\\$')
    return '"'+name+'"'

def escape_filename_sh_ansic(name):
    """Return an ansi-c shell-escaped version of a filename."""

    out =[]
    # gather the escaped characters into a list
    for ch in name:
        if ord(ch) < 32:
            out.append("\\x%02x"% ord(ch))
        elif ch == '\\':
            out.append('\\\\')
        else:
            out.append(ch)

    # slap them back together in an ansi-c quote  $'...'
    return "$'" + "".join(out) + "'"

SPLIT_RE = re.compile(r'[a-zA-Z]+|\d+')
def alphabetize(s):
    L = []
    for isdigit, group in itertools.groupby(SPLIT_RE.findall(s), key=lambda x: x.isdigit()):
        if isdigit:
            for n in group:
                L.append(('', int(n)))
        else:
            L.append((''.join(group).lower(), 0))
    return L

def dir_sep():
    """Return the separator used in this os."""
    return getattr(os.path,'sep','/')

if __name__=="__main__":
    main()
    