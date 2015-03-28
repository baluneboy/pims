import sublime, sublime_plugin, subprocess

def insert_output(view, edit):
    r = sublime.Region(0, view.size())
    try:
        proc = subprocess.Popen( [ "bash", "-c", 'echo "$0" | tr [a-y] [A-Y]', view.substr(r) ], stdout=subprocess.PIPE )
        output = proc.communicate()[0]
        view.replace(edit, r, output)
    except:
        pass

class ReplaceWithOutputCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        e = self.view.begin_edit()
        insert_output(self.view, e)
        self.view.end_edit(e)