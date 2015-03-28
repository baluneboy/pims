#!/usr/bin/python

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.figure import Figure
from pims.gui import DUMMYDATA
from pims.database.samsquery import SimpleQueryAOS, get_samsops_db_params
from pims.pad.padstream import XyzPlotDataSortedList, RssPlotDataSortedList

#########################################
# NOTE: we use matplotlibrc conventions
#import matplotlib
#print matplotlib.get_configdir()
#print matplotlib.matplotlib_fname()
#raise SystemExit
#########################################
    
class Plot3x1(object):
    """Container class for general purpose 3x1 plot, like for xyz vs. time."""
    # it does not appear to be straightforward to subclass Figure class!?
    
    def __init__(self):
        self.aos_gmt_callback = self.fake_aos_tiss_time_callback().next
        self.fig = plt.figure()
        self.suptitle = plt.suptitle("GridSpec3x1")
        self.gs = gridspec.GridSpec(3, 1)
        self.init_plot()
        
        # connect to mouse click event for testing
        self.clickid = None
        self.clickid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
    
    # A generator for *fake* AOS/LOS updates
    def fake_aos_tiss_time_callback(self):
        aos_gmt = True, datetime.now()
        while 1:
            aos_gmt = not aos_gmt[0], datetime.now()
            yield aos_gmt
    
    def init_plot(self):
        """
        plot the data as a line series, and save the reference 
        to the plotted line series and axes as attributes of self
        """
        x = DUMMYDATA['x']
        y = DUMMYDATA['y']
        for i in range(3):
            suffix = '%d1' % (i + 1)
            hax = plt.subplot(self.gs[i], gid='ax' + suffix)
            hline = hax.plot_date(x, y, '.-', gid='line' + suffix)[0]
            setattr(self, 'ax' + suffix, hax)
            setattr(self, 'line' + suffix, hline)
        
        # attach AOS/LOS GMT to "last" axes
        ax = self.fig.axes[-1]
        self.text_aos_gmt = ax.text(1.02, -0.2, '???\n00:00:00\ndd-Mon-yyyy',
                                                horizontalalignment='center',
                                                verticalalignment='center',
                                                transform = ax.transAxes,
                                                bbox=dict(facecolor='LightBlue', alpha=0.3))

    def on_click(self, event):
        #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        #    event.button, event.x, event.y, event.xdata, event.ydata)
        self.aos, self.gmt = self.aos_gmt_callback()
        if self.aos:
            self.text_aos_gmt.set_backgroundcolor('LightGreen')
            self.text_aos_gmt.set_text('AOS\n%s' % self.gmt.strftime('%H:%M:%S\n%d-%h-%Y'))    
        else:
            self.text_aos_gmt.set_backgroundcolor('LightPink')
            self.text_aos_gmt.set_text('LOS\n%s' % self.gmt.strftime('%H:%M:%S\n%d-%h-%Y'))    

        self.fig.canvas.draw()

    #def show_demo(self):
    #    for i, ax in enumerate(self.fig.axes):
    #        ax.text(0.5, 0.5, "ax%d1" % (i+1), va="center", ha="center")
    #        for tl in ax.get_xticklabels() + ax.get_yticklabels():
    #            tl.set_visible(False)

class Plot1x1(Plot3x1): pass

PLOTMAP = {
                XyzPlotDataSortedList   : Plot3x1,
                RssPlotDataSortedList   : Plot1x1,
}

for k, v in PLOTMAP.iteritems():
    print k, v
#raise SystemExit

#_HOST, _SCHEMA, _UNAME, _PASSWD = get_samsops_db_params('samsquery')
#query_aos = SimpleQueryAOS(_HOST, _SCHEMA, _UNAME, _PASSWD)
#aos_los, gse_tiss_time = query_aos.get_aos_tisstime()
#print aos_los, gse_tiss_time

plotxyz = Plot3x1()
plt.show()
