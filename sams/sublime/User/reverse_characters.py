import sublime, sublime_plugin

class ReverseCharactersCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            stringContents = self.view.substr(region)
            self.view.replace(edit, region, stringContents[::-1])