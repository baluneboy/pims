#!/usr/bin/env python

import sys
import time
import logging
from daemon import runner

class App():

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/foo_daemon.pid'
        self.pidfile_timeout = 5

    def status(self):
        print 'status goes here'

    def run(self):
        while True:
            print("Howdy World!")
            time.sleep(5)

if __name__ == '__main__':

    app = App()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.do_action()