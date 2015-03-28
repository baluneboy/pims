#!/usr/bin/env python

import wx
import os
import re

# A simple multi-choice dialog
class MultiChoiceDialog(object):
    """ A simple multi-choice dialog. """
    
    def __init__(self, title, prompt, choices):
        
        # inputs
        self.title = title
        self.prompt = prompt
        self.choices = choices
        
        # format or otherwise prettify the choices
        self.pretty_choices = self.prettify_choices()
        
        # for wx, we need to create app before constructing dialog
        self.app = wx.PySimpleApp()
        
        # construct wx multichoice dialog
        self.dialog = wx.MultiChoiceDialog( None, self.prompt, self.title, self.pretty_choices )       
    
        # preselect items
        self.preselect()
    
    def prettify_choices(self):
        # nothing pretty for simple base class
        return self.choices
    
    def preselect(self):
        """This is where a subclass might, for example, filter for pre-selects."""
        # we just select all items for simple base class
        idx = range(len(self.choices))
        self.dialog.SetSelections(idx)
    
    def show_dialog(self):
        
        # interact with user
        if self.dialog.ShowModal() == wx.ID_OK:
            selections = self.dialog.GetSelections()
            user_selections = [self.choices[x] for x in selections]
        else:
            return None
            
        self.dialog.Destroy()
        self.app.MainLoop()
        
        # return items the user selected
        return user_selections
    
# A multi-choice dialog for files (with paths).
class MultiChoiceFileDialog(MultiChoiceDialog):
    """ A multi-choice dialog for files (with paths). """

    def prettify_choices(self):
        # to make file choices pretty, we strip dirnames
        return [os.path.basename(f) for f in self.choices]

# A multi-choice dialog for files with a filter for preselects.
class MultiChoiceFilterFileDialog(MultiChoiceFileDialog):
    """ A multi-choice dialog for files with a filter for preselects. """

    def __init__(self, title, prompt, choices, predicate):
        # we will use predicate for preselect method
        self.predicate = predicate
        super(MultiChoiceFilterFileDialog, self).__init__(title, prompt, choices)

    def preselect(self):
        """Apply filtering via predicate to do preselection."""
        idx = [ i for i, f in enumerate(self.choices) if self.predicate(f) ]
        self.dialog.SetSelections(idx)

if __name__ == '__main__':
    
    #title = "Demo wx.MultiChoiceDialog"
    #prompt = "Pick from\nthis list:"
    #choices = [ 'apple', 'pear', 'banana', 'coconut', 'orange', 'grape', 'pineapple',
    #        'blueberry', 'raspberry', 'blackberry', 'snozzleberry',
    #        'etc' ]    
    #
    #mcd = MultiChoiceDialog(title, prompt, choices)
    #user_selections = mcd.show_dialog()
    #
    #print user_selections
    #raise SystemExit

    # example predicates
    is_csv = lambda fname : bool(re.match('.*\.csv', fname))
    is_txt = lambda fname : bool(re.match('.*\.txt', fname))
    is_csv_or_txt = lambda fname : bool(re.match('.*\.csv|.*\.txt', fname))
       
    title = "Demo Class MultiChoiceFileDialog"
    prompt = "Pick from\nthis file list:"
    choices = [ '/tmp/one.txt', '/path/two.csv' ]    
    
    mcd = MultiChoiceFilterFileDialog(title, prompt, choices, is_csv)
    user_selections = mcd.show_dialog()    
    
    if user_selections is None:
        print 'you pressed cancel'        
    elif len(user_selections) == 0:
        print 'you chose nothing'
    else:
        print user_selections
