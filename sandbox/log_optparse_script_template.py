#!/usr/bin/env python

import logging
import logging.handlers
from optparse import OptionParser

# Setup logging to syslog and the console
log = logging.getLogger("KenExampleCode")
try:
    _syslog_handler = logging.handlers.SysLogHandler(address="/dev/log",
                             facility=logging.handlers.SysLogHandler.LOG_DAEMON)
    _syslog_handler.setLevel(logging.INFO)
    _syslog_formatter = logging.Formatter("%(name)s: %(levelname)s: "
                                          "%(message)s")
    _syslog_handler.setFormatter(_syslog_formatter)
except:
    pass
else:
    log.addHandler(_syslog_handler)
_console_handler = logging.StreamHandler()
_console_formatter = logging.Formatter("%(asctime)s %(name)s [%(levelname)s]: "
                                       "%(message)s",
                                       "%T")
_console_handler.setFormatter(_console_formatter)
log.addHandler(_console_handler)

class SayWhat(object):
    
    def __init__(self, options, title=None):
        self.options = options
        self.title = title
        
    def run(self):
        print 'title is %s' % self.title
        print 'options:'
        print self.options
        print 'you may want to get self.options as dict!'
    
def main():
    """Allow to run the daemon from the command line."""
    parser = OptionParser()
    parser.add_option("-t", "--disable-timeout",
                      default=False,
                      action="store_true", dest="disable_timeout",
                      help="Do not shutdown the daemon because of "
                             "inactivity")
    parser.add_option("", "--disable-plugins",
                      default=False,
                      action="store_true", dest="disable_plugins",
                      help="Do not load any plugins")
    parser.add_option("-d", "--debug",
                      default=False,
                      action="store_true", dest="debug",
                      help="Show internal processing "
                             "information")
    parser.add_option("-r", "--replace",
                      default=False,
                      action="store_true", dest="replace",
                      help="Quit and replace an already running "
                             "daemon")
    parser.add_option("", "--session-bus",
                      default=False,
                      action="store_true", dest="session_bus",
                      help="Listen on the DBus session bus (Only required "
                             "for testing")
    parser.add_option("", "--chroot", default=None,
                      action="store", type="string", dest="chroot",
                      help="Perform operations in the given "
                             "chroot")
    parser.add_option("-p", "--profile",
                      default=False,
                      action="store", type="string", dest="profile",
                      help="Store profile stats in the specified "
                             "file")
    parser.add_option("--dummy",
                      default=False,
                      action="store_true", dest="dummy",
                      help="Do not make any changes to the system (Only "
                             "of use to developers)")
    options, args = parser.parse_args()

    if options.debug == True:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
        _console_handler.setLevel(logging.INFO)

    sw = SayWhat(options, title='happy')

    if options.profile:
        import profile
        profiler = profile.Profile()
        profiler.runcall(sw.run)
        profiler.dump_stats(options.profile)
        profiler.print_stats()
    else:
        sw.run()

# Try this in ipython:
# import pims.log_optparse_script_template
# pims.log_optparse_script_template.main()