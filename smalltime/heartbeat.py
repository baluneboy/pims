#!/usr/bin/env python

from pims.bigtime.timemachine import TimeGetter

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
    
    """
    
    def __init__(self, table, host='manbearpig', Tsec=1.0):
        self.table = table
        self.host = host
        self.Tsec = float(Tsec)
        self.time_getter = TimeGetter(table, host=host)

    def __str__(self):
        s = ''
        s += 'table: %s, host: %s, Tsec: %.3f' % (self.table, self.host, self.Tsec)
        return s
        
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
