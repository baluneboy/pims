#!/usr/bin/env python

import numpy as np
from obspy import Stream
from blist import sortedlist

# acceleration data stream with channel/time sorting
class PadStream(Stream):
    """acceleration data stream with channel/time sorting"""
    
    def __str__(self, extended=False):
        """Returns short summary string of the current stream."""
        # get longest id
        id_length = self and max(len(tr.id) for tr in self) or 0
        out = str(len(self.traces)) + ' Trace(s) in PadStream:\n'
        if len(self.traces) <= 20 or extended is True:
            out = out + "\n".join([tr.__str__(id_length) for tr in self])
        else:
            out = out + "\n" + self.traces[0].__str__() + "\n" + \
                    '...\n(%i other traces)\n...\n' % (len(self.traces) - \
                    2) + self.traces[-1].__str__() + '\n\n[Use "print(' + \
                    'PadStream.__str__(extended=True))" to print all Traces]'
        return out    
    
    def sort(self, keys=['channel', 'starttime', 'endtime'], reverse=False):
        """Sort by channel (axis), then by starttime (override)."""
        super(PadStream, self).sort(keys=keys, reverse=reverse)

    def span(self):
        """Return timespan in seconds."""
        self.sort()
        span = self[-1].stats.endtime - self[0].stats.starttime # FIXME assumptions okay!?
        return span
    
    def is_valid_substream(self):
        """Return boolean True if has 3 traces (x,y,z) in that order."""
        if [tr.stats.channel for tr in self] == ['x', 'y', 'z']:
            return True
        else:
            return False

# container for sorted list of (t, x, y, z) tuples
class XyzPlotDataSortedList(sortedlist):
    """container for sorted list of (t, x, y, z) tuples"""
    
    def __init__(self, *args, **kwargs):
        # clobber key intentionally so we sort by tuple's first element
        kwargs['key'] = lambda tup: tup[0]
        self.maxlen = int( kwargs.pop('maxlen', 123456) )
        super(XyzPlotDataSortedList, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "%s(maxlen=%d)" % (self.__class__.__name__, self.maxlen)

    def __add(self, *args, **kwargs):
        # note leading double-underscore for private method
        super(XyzPlotDataSortedList, self).add(*args, **kwargs)
    
    def add(self, *args, **kwargs):
        raise AttributeError('"add" method does not work for %s, try "append" method' % self.__class__.__name__)
    
    def append(self, txyz):
        self.__add( txyz )
        # FIXME this is incredibly crude way to do the needed pruning
        while len(self) > self.maxlen:
            toss = self.pop(0)

# container for sorted list of (t, RSS ) tuples
class RssPlotDataSortedList(XyzPlotDataSortedList):
    """container for sorted list of (t, rss) tuples"""
    
    def append(self, txyz):
        t = txyz[0]
        xyz = np.asarray( txyz[1:] )
        rss = np.sqrt( np.sum((xyz)**2) )
        super(RssPlotDataSortedList, self).append( (t, rss) )

def demo_ingest(offset):
    from pims.utils.iterabletools import quantify
    # Trace 1: 1111
    # Trace 2:          555
    # 1 + 2  : 1111.....555
    #          123456789^
    from obspy import UTCDateTime, Trace

    tr1 = Trace(data=np.ones(3, dtype=np.int32) * 1)
    tr2 = Trace(data=np.ones(2, dtype=np.int32) * 2)
    tr2.stats.starttime = tr1.stats.endtime + ( tr1.stats.delta + offset )
    stream = PadStream([tr1, tr2])
    print "span", stream.span()
    for tr in stream: print tr
    stream.verify()
    stream.merge()
    print "span", stream.span()
    for tr in stream: print tr, "offset",
    print ( tr1.stats.delta + offset )
    print stream[-1][:], "mean=", stream[-1][:].mean(), "std=", stream[-1][:].std()
    print '-' * 100

def demo_bisect():
    DELTA = 1
    b = XyzPlotDataSortedList()
    txyzs = [
        (0, 0),
        (1, 1),
        (3, 3),
        (6, 6),
        (4, 4),
    ]
    for txyz in txyzs:
        i, tup = b._bisect_left(txyz)
        print b, "app", txyz, "at", i
        if tup:
            # inserting out of order (playback data?)
            delta = txyz[0] - b[i-1][0]
            print " leftDelta is %g - %g = %g" % ( txyz[0], b[i-1][0], delta ),
            if delta > 1.25 * DELTA:
                print "TOO BIG"
            else:
                print
            delta = b[i][0] - txyz[0] # RIGHT DELTA
            print "rightDelta is %g - %g = %g" % ( b[i][0], txyz[0], delta ),
            if delta > 1.25 * DELTA:
                print "TOO BIG"
            else:
                print
        elif len(b) > 0:
            # if appendDelta > analysis_interval, then also insert some/what number of NaNs?
            delta = txyz[0] - b[i-1][0]
            if delta > DELTA:
                print " appendDelta TOO BIG: %g - %g = %g" % ( txyz[0], b[i-1][0], delta )
            elif delta <= 0:
                print " appendDelta OVERLAP: %g - %g = %g" % ( txyz[0], b[i-1][0], delta )
            else:
                print " appendDelta okay: %g - %g = %g" % ( txyz[0], b[i-1][0], delta )
        b.append(txyz)
    print '-' *25, '\n', b
    
def demo_rss():
    b = RssPlotDataSortedList()
    txyzs = [
        (0, 0, 0, 0),
        (1, 1, 2, 3),
        (3, 3, 4, 5),
        (6, 6, 7, 8),
        (4, 4, 5, 6),
    ]
    for txyz in txyzs:    
        b.append(txyz)

    print '-' *25, '\n', b

if __name__ == "__main__":
    
    demo_rss(); raise SystemExit
    
    demo_bisect(); raise SystemExit
    
    for offset in range(-200,200,50):
        demo_ingest(offset/100.0)