import sublime, sublime_plugin

class AllCommand(sublime_plugin.TextCommand):

    def done(self,arg):
        self.foldstr = arg
        self.all()

    def all(self):
        view = self.view
        view.run_command("unfold_all")
        endline, endcol = view.rowcol(view.size())
        line = 0
        firstRegion = None
        currRegion = None
        regions = []

        while line < endline:
            region = view.full_line(view.text_point(line, 0))
            data = view.substr(region)
            if data.find(self.foldstr) == -1:
                if firstRegion == None:
                    firstRegion = region
                    lastRegion  = region
                else:
                    lastRegion  = region
            else:
                if firstRegion:
                    currRegion = firstRegion.cover(lastRegion)
                    regions.append(currRegion)
                    firstRegion = None
            line += 1
            if currRegion:
                regions.append(currRegion)
                currRegion = None

        if firstRegion:
            currRegion = firstRegion.cover(lastRegion)
            regions.append(currRegion)
            firstRegion = None
        view.fold(regions)

    def run(self, edit):
        window = self.view.window()
        for reg in self.view.sel():
            defstr = self.view.substr(reg)
            break
        window.show_input_panel("Show Only Lines Containing",defstr,self.done,None,None)
