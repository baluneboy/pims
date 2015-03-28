import sublime
import sublime_plugin
import hashlib

class ShasumrCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # We check for backslashes since we can do a better job of preserving
        # whitespace when backslashes are not present
        backslashes = False
        sels = self.view.sel()
        for sel in sels:
            if self.view.substr(sel).find('\\') != -1:
                backslashes = True

        # Expand selection to backslashes, unfortunately this can't use the
        # built in move_to brackets since that matches parentheses also
        if backslashes:
        	print 'friggin backslashes'
	        new_sels = []
	        for sel in sels:
	            new_sels.append(self.view.find('\}', sel.end()))
	        sels.clear()
	        for sel in new_sels:
	            sels.add(sel)
	        self.view.run_command("expand_selection", {"to": "brackets"})

        for sel in sels:
            string = self.view.substr(sel)
            print string

        # We clear all selection because we are going to manually set them
        self.view.sel().clear()
