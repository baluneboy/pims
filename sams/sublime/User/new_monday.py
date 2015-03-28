import sublime, sublime_plugin
import datetime

class NewMondayCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		_today = datetime.datetime.today().date()
		s  = '\n\n'
		s += '=' * 67
		s += '\n' + _today.strftime('%Y GMT %j')
		s += '\nCMD LINE CMD monday\n'
		s += '\n# wait 2 minutes since sending "monday" cmd'
		s += '\nFILE DOWNLINK /usr/tgz/samslogs' + _today.strftime('%Y%j.tgz')

		# This would insert new string at beginning of document
		#self.view.insert(edit, 0, s)

		# This moves cursor to past last line and inserts new string there
		# NOTE: GotoLineCommand is in a sample plugin
		# FIXME why do we need offset of two from lines value?
		lines, _ = self.view.rowcol(self.view.size())
		self.view.run_command("goto_line", {"line": lines + 2} ) # why plus 2?
		self.view.insert(edit, self.view.sel()[0].end(), s)