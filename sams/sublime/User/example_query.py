# 2014-03-28 11:29:02
# above is results from: select from_unixtime(max(time)) from 121f05;
import sublime, sublime_plugin
import subprocess

def run_query(host, schema, query):
    cmdQuery = 'mysql --skip-column-names -h %s -D %s -u pims -pYOUKNOW --execute="%s"' % (host, schema, query)
    p = subprocess.Popen([cmdQuery], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    results, err = p.communicate()
    return results

class ExampleCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		#self.view.insert(edit, 0, sys.version + "Hello, World!")
		querystr = 'select from_unixtime(max(time)) from 121f05;'
		results = run_query('chef', 'pims', querystr)
		self.view.insert(edit, 0, '# ' + results + '# above is results from: %s\n' % querystr)
