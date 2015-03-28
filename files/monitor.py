#!/usr/bin/python

import os
import pyinotify
from pims.patterns.dailyproducts import _PLOTSPATH
from pims.database.pimsquery import JaxaPostPlotFile

# process transient file
class ProcessTransientFile(pyinotify.ProcessEvent):
    """process transient file"""
    
    def process_IN_CREATE(self, event):
        #print event.pathname, ' -> in_create'
        pass

    def process_IN_DELETE(self, event):
        #print event.pathname, ' -> in_delete'
        pass

    def process_IN_CLOSE_WRITE(self, event):
        print event.pathname, ' -> in_close_write'
        # query for event.pathname
        # if no records, then insert as 'found'
        # if 'found', then change to 'pending' and queue up changes
        # if 'pending', then log message to ignore because previous_timestamp still pending
        # if 'problem', then change to 'found'

# JaxaFileHandler with quick_check method to see if we created or deleted file of interest
class JaxaFileHandler(object):
    """JaxaFileHandler with quick_check method to see if we created or deleted file of interest"""

    csvpath = os.path.join(_PLOTSPATH, 'sams', 'params')
    
    def __init__(self, sensor='121f05', plot_type='intrms', handler=ProcessTransientFile, timeout=3):
        # The watch manager stores the watches and provides operations on watches
        self.sensor = sensor
        self.plot_type = plot_type
        self.basename = self.sensor + '_' + self.plot_type + '.csv'
        self.watch_file = os.path.join(self.csvpath, self.basename)
        self.handler = handler
        self.wm = pyinotify.WatchManager()
        #self.mask =  pyinotify.IN_DELETE|pyinotify.IN_CREATE|pyinotify.IN_CLOSE_WRITE # watched events
        self.mask =  pyinotify.IN_CLOSE_WRITE # watched events
        self.timeout = timeout
        self.notifier =  pyinotify.Notifier(self.wm, timeout=self.timeout)
        self.wm.watch_transient_file(self.watch_file, self.mask, self.handler)
        # create object to keep track of jaxa posting plotfile
        self.jaxa_post = JaxaPostPlotFile() # host='localhost')
        dtm, status = self.jaxa_post.file_status(self.basename)
        if status != 'found':
            raise Exception( 'We need db basename entry for "%s" file to start with!' % self.watch_file )

    def quick_check(self):
        assert self.notifier._timeout is not None, 'Notifier must be constructed with a short timeout'
        self.notifier.process_events()
        while self.notifier.check_events():  #loop in case more events appear while we are processing
            self.notifier.read_events()
            self.notifier.process_events()

def demo():
    import time
    jaxa_file_handler = JaxaFileHandler()
    for i in range(9):
        jaxa_file_handler.quick_check()
        time.sleep(2)

if __name__ == "__main__":
    demo()

# apt-get install inotify-tools
# DIR=/tmp/p; while RES=$(inotifywait -e create $DIR --format %f .); do echo RES is $RES at `date`; done

# EXAMPLE for 121f05_intrms.csv
#------------------------------
#data.scale_factor,1e6,scale factor for accel. data (e.g. use 1e6 for units of ug)
#time.analysis_interval,10,number of seconds in analysis interval (e.g.  use 10 for 10-second interval RMS)
#time.analysis_overlap,9,number of seconds to overlap with previous analysis interval (e.g. use 9 for 9-second overlap)
#time.plot_span,600,target number of seconds for plot span (e.g. use 600 for ~10-minute plot span)
#pw.startTime,2014-02-10 18:55:00,start GMT for display (note: PIMS real-time databases cover at least last 12 hours or so)
