#!/usr/bin/python
import subprocess, threading

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        return self.process.returncode

def timeRun(command, timeoutSec):
    tzero = time.time()
    retcode = command.run(timeout=timeoutSec)
    elapsedSec = time.time() - tzero
    return retcode, elapsedSec

if __name__ == '__main__':
    import time
    command = Command("echo 'Process started'; sleep 3; echo 'Process finished'")
    
    retcode, elapsedSec = timeRun(command, 4)
    print "It took ", elapsedSec, "seconds."
    
    retcode, elapsedSec = timeRun(command, 2)
    print "It took ", elapsedSec, "seconds."
