#!/usr/bin/env python

import time
import threading
from Queue import Queue

from pims.bigtime.timemachine import TimeGetter, LocalTimeGetter
from pims.utils.pimsdateutil import unix2dtm

# TODO - handle these scenarios:
#        -- table does not exist -> initialize and for all time, this will be some form of stale indication
#        -- table exists, but empty
#        -- table exists, and deltaT > threshold
#        -- table exists, and deltaT <= threshold

# every T seconds, get heartbeat indication from real-time db table unix time (like from es05rt table)
class Heartbeat(object):
    """every T seconds, get heartbeat indication from real-time db table unix time (like from es05rt table)

    >>> hb = Heartbeat('es05rt', host='manbearpig', Tsec=1.0)
    >>> print hb
    table: es05rt, host: manbearpig, Tsec: 1.000
    >>> hb.run()
    >>> print unix2dtm(hb.get())
    >>> hb = Heartbeat('121f03rt', host='manbearpig', Tsec=1.0); hb.run()
    >>> print unix2dtm(hb.get())
    """
    
    def __init__(self, table, host='manbearpig', Tsec=1.0):
        self.table = table
        self.host = host
        self.Tsec = float(Tsec)
        self.time_getter = TimeGetter(table, host=host)
        self.q = Queue() # this is how we get results from thread after we run it
        self.thread = threading.Thread(target=self.get_time, args=(), kwargs={})

    def get_time(self):
        """get time into queue"""
        if self.table.endswith('f02rt'):
            time.sleep(5)
        t = self.time_getter.get_time()
        self.q.put(t)

    def run(self):
        """run thread"""
        self.thread.start()
    
    def get(self):
        """get thread result out of queue"""
        return self.q.get()
    
    def check(self):
        """check if thread is running"""
        return self.thread.is_alive()
    
    def join(self):
        """waits until thread is done"""
        self.thread.join()

    def __str__(self):
        s = ''
        s += 'table: %s, host: %s, Tsec: %.3f' % (self.table, self.host, self.Tsec)
        return s

# FIXME this can probably all be [better?] done by parsing:
# /misc/yoda/www/plots/user/sams/status/sensortimes.txt

# FIXME this is what we will be comparing to butters
LTG = LocalTimeGetter() 
print "jimmy local", unix2dtm(LTG.get_time())

for sensor_table in ['121f02rt', '121f03rt', '121f04rt']:
    hb = Heartbeat(sensor_table, host='manbearpig', Tsec=1.0)
    hb.run()
    time.sleep(2)
    print sensor_table, hb.check(), unix2dtm(hb.get()) # .strftime
    time.sleep(1)
raise SystemExit

    
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
