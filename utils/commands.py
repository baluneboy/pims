#!/usr/bin/env python
version = '$Id$'

import os
import sys
import time
import subprocess
import threading

# FIXME we should refactor where Command is class without logging and new CommandWithLog is based on that
#       we currently have foobarred this with Command having the logging feature

def get_app_name():
    """Get application name string."""
    base = os.path.basename(sys.argv[0])
    return os.path.splitext(base)[0]


class Command(object):
    """Run a command in a thread."""
    def __init__(self, cmd, log):
        self.cmd = cmd
        self.log = log
        self.process = None

    def run(self, timeout):
        def target():
            self.log.info( 'Thread started' )
            self.process = subprocess.Popen(self.cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            out, err = self.process.communicate()
            if err:
                self.log.error( 'here is stderr...\n' + err )
            else:
                self.log.info( 'there was no stderr' )
            self.log.info( 'here is stdout...\n' + out )
            self.log.info( 'Thread finished' )

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.log.warning( 'Terminating process' )
            self.process.terminate()
            thread.join()
        return self.process.returncode


class CommandWithoutLog(object):
    """Run a command in a thread."""
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            out, err = self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
        return self.process.returncode


def timeLogRun(command, timeoutSec, log=None):
    """
    Function that returns (returnCode, elapsedSec) from given command string.
    Also has timeout and logging features.
    """
    if not log:
        from pims.files.log import TrashLog
        log = TrashLog().process
    cmdObj = Command(command, log)
    tzero = time.time()
    log.info( 'START: ' + command )
    retCode = cmdObj.run(timeout=timeoutSec)
    elapsedSec = time.time() - tzero
    log.info( 'Took about %.3f seconds' % elapsedSec )
    log.info( 'Return code = %d' % retCode)
    return retCode, elapsedSec


def time_run(command, timeoutSec):
    """
    Function that returns (returnCode, elapsedSec) from given command string.
    Also has timeout feature.
    """
    cmdObj = CommandWithoutLog(command)
    tzero = time.time()
    retCode = cmdObj.run(timeout=timeoutSec)
    elapsedSec = time.time() - tzero
    return retCode, elapsedSec


if __name__ == "__main__":
    print get_app_name()   