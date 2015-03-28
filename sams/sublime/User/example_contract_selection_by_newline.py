import sublime, sublime_plugin

# Test cases:
#
# With cursor at X, the command should select the string:
# "Here is the X cursor
# "
#
# With cursor at X, the command should select
# the single quoted string:
# "Here is 'the X cursor' now"
#
# With cursor at X, the command should select
# the double quoted string:
# "Here the cursor is 'outside' the X selection"
#
# view.run_command("expand_selection_to_quotes")

def my_replace_region(view, sel):
    start = sel.begin()
    end = sel.end() - 1
    view.sel().subtract(sel)
    view.sel().add(sublime.Region(start, end))

class ExpandSelectionToQuotesCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        for sel in self.view.sel():
            my_replace_region(self.view, sel)

            def replace_region(start, end):
                self.view.sel().subtract(sel)
                self.view.sel().add(sublime.Region(start, end))

            #replace_region( sel.begin(), sel.end()-1 )            
