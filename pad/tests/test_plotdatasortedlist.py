#!/usr/bin/python

import unittest
from random import shuffle
from pims.pad.padstream import XyzPlotDataSortedList

class PlotDataSortedListTestCase(unittest.TestCase):
    """
    Test suite for XyzPlotDataSortedList.
    """

    def setUp(self):
        """
        set up with shuffled list of txyz tuples
        """
        self.count = 123
        self.txyzs = []
        for k in range(self.count):
            txyz = tuple()
            txyz = txyz + ( float(k+1), )
            for i, ax in enumerate( ['x', 'y', 'z'] ):
                txyz = txyz + ( float(k+1) + float((i+1)/10.0), )
            self.txyzs.append(txyz)
        shuffle( self.txyzs )

    def test_init(self):
        """
        Tests the init method of the XyzPlotDataSortedList object.
        """        
        # without maxlen kwarg input, the maxlen should be 123456
        data = XyzPlotDataSortedList() # maxlen kwarg is missing here
        self.assertEqual(123456, data.maxlen)
        maxlen = 7654321
        data = XyzPlotDataSortedList(maxlen=maxlen)
        self.assertEqual(maxlen, data.maxlen)

    def test_add_privacy(self):
        """
        Tests that add method of the XyzPlotDataSortedList object raises AttributeError
        """        
        # this thwarts loophole around maxlen via add of parent class
        maxlen = 999
        data = XyzPlotDataSortedList(maxlen=maxlen)
        self.assertRaises( AttributeError, data.add, (1,2,3,4) )

    def test_append(self):
        """
        Tests the append method of the XyzPlotDataSortedList object.
        """
        # simple test
        data = XyzPlotDataSortedList(maxlen=4)
        for i in range(11,0,-1):
            data.append( (i, i/10.0) )
        data.append( (10.5, 10.5/10.0) )
        data.append( (10.6, 10.6/10.0) )
        #print data
        self.assertEqual( [(10, 1.0), (10.5, 1.05), (10.6, 1.06), (11, 1.1)], list(data) )
        
        # better test
        txyzs = self.txyzs
        for maxlen in range(1, self.count+1):
            plotdata = XyzPlotDataSortedList(maxlen=maxlen)
            for txyz in txyzs:
                plotdata.append( txyz )
            times = [ tup[0] for tup in plotdata ]
            all_times = [float(i+1) for i in range(self.count)]
            all_times.reverse()
            all_times = all_times[0:maxlen]
            all_times.reverse()
            self.assertEqual(all_times, times)
            
def suite():
    return unittest.makeSuite(PlotDataSortedListTestCase, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
