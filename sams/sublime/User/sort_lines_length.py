import sublime, sublime_plugin
import sort

def line_length_sort(txt):
    txt.sort(lambda a, b: cmp(len(a), len(b)))
    return txt

class SortLinesLengthCommand(sublime_plugin.TextCommand):
    def run(self, edit, reverse=False,
                        remove_duplicates=False):
        view = self.view

        sort.permute_lines(line_length_sort, view, edit)