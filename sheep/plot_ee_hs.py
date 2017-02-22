#!/usr/bin/env python

"""make use of matplotlib plt.subplots here to do daily Plot of EE HS
"""

import os
import sys
import numpy as np
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
from finplot import candlestick_yhltv
from pims.lib.niceresult import NiceResult

_SIXTEENDAYSAGO = str( datetime.now().date() - timedelta(days=16) )

"""
EE_FIELD  maps2 VARNAME isa MTYPE
----------------------------------
SE 0 Temp X --> se0tempx    TEMPS
SE 0 Temp Y --> se0tempy    TEMPS
SE 0 Temp Z --> se0tempz    TEMPS
SE 0 +5V    --> se0p5v      VOLTS
HEAD 0 +15V --> se0p15v     VOLTS
HEAD 0 -15V --> se0n15v     VOLTS
SE 1 Temp X --> se1tempx    TEMPS
SE 1 Temp Y --> se1tempy    TEMPS
SE 1 Temp Z --> se1tempz    TEMPS
SE 1 +5V    --> se1p5v      VOLTS
HEAD 1 +15V --> se1p15v     VOLTS
HEAD 1 -15V --> se1n15v     VOLTS
Base Temp   --> basetemp    TEMPS
PC104 +5V   --> pc104p5v    VOLTS
Ref +5V     --> refp5v      VOLTS
Ref 0V      --> ref0v       VOLTS

"""
# input parameters
defaults = {
'host':         'yoda',             # server to hit
'schema':       'samsmon',          # schema to use
'table':        'ee_packet',        # table to query
'file_prefix':  '/tmp/eehsplots_',  # string 1st part of VOLTS or TEMPS png filename
'date_start':   _SIXTEENDAYSAGO,    # date object for start time of plots
'num_days':     '18',               # integer number of days to plot
'minvol':       '43200',            # integer min # of samples for day; otherwise candle is gray
}
parameters = defaults.copy()

class FigureSet(object):
    """handle setup, plotting and figure saving for EE HS
    for 4 EEs, there should ultimately be two of these used:
    one figure 4x7 of voltages, and
    one figure 4x9 of temperatures
    """

    def __init__(self, nrows, ncols, save_file, minvol=43200):
        self.nrows = nrows
        self.ncols = ncols
        self.save_file = save_file
        self.minvol = minvol
        self.figsize = (10, 7.5)
        self.dpi = 300
        self.fig, self.axarr = plt.subplots(nrows, ncols, sharex='col', sharey='row', figsize=self.figsize, dpi=self.dpi)
        self._get_format_info()

    def _get_format_info(self):
        self.mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
        self.alldays = DayLocator()                  # minor ticks on the days
        self.weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12

    def add_subplot(self, r, c, sub_results, title):

        self.axarr[r, c].xaxis.set_major_locator(self.mondays)
        self.axarr[r, c].xaxis.set_minor_locator(self.alldays)
        self.axarr[r, c].xaxis.set_major_formatter(self.weekFormatter)
        candlestick_yhltv(self.axarr[r, c], sub_results, minvol=self.minvol)

        if c == 0:
            self.axarr[r, c].set_ylabel('%d%d' % (r,c))
        if r == 0:
            self.axarr[r, c].set_title(title)

        # date axis and autoscale view
        self.axarr[r, c].xaxis_date()
        self.axarr[r, c].autoscale_view()

    def save(self):
        print 'writing', self.save_file, '...',
        self.fig.savefig(self.save_file, dpi=self.dpi, orientation='landscape', transparent=False)
        print 'done'

class StatusHealthEePlot(object):
    """query, then Status and Health EE Plot"""

    def __init__(self, host, schema, table, file_prefix, date_start, num_days, minvol):
        self.host = host
        self.schema = schema
        self.table = table
        self.file_prefix = file_prefix
        self.date_start = date_start
        self.num_days = num_days
        self.minvol = minvol
        self.results = None

    def _DUMMY_QUERY(self):
        #             datenum  yestmed  todayhi   todaylo  todaymed  todayvolume
        results = [
                    (735974.0, 125.979, 127.896, 125.9274, 127.332,  4974400.0),
                    (735975.0, 127.736, 127.858, 125.3256, 127.018,  5078700.0),
                    (735976.0, 127.591, 128.336, 125.297,  125.364,    43199.0),
                    (735977.0, 126.094, 127.867, 125.4117, 127.026,  5709600.0),
                    (735978.0, 124.258, 125.086, 123.1651, 124.274,  8895400.0),
                    (735979.0, 124.359, 126.252, 122.3914, 122.439,  9979600.0),
                    (735980.0, 113.213, 118.501, 112.7767, 116.466, 16157800.0),
                    (735981.0, 115.939, 119.562, 115.2426, 117.469,  8851600.0),
                    (735982.0, 119.155, 119.218, 116.379,  117.077,  9238400.0),
                    (735983.0, 116.699, 118.731, 116.255,  116.676,  5446000.0),
                    (735984.0, 116.837, 118.138, 116.8293, 117.163,  4617800.0),
                    (735985.0, 117.293, 117.909, 115.3095, 115.605,    43199.0),
                    (735986.0, 115.89,  117.393, 115.6531, 116.810,  3942500.0),
                    (735987.0, 117.827, 119.266, 117.5174, 119.266,  8248100.0)
                    ]
        return results

    def query(self):
        """query to get results; each record (row) is for a given EE and timestamp"""

        # FIXME the yahoo junk below gets replaced with new samsquery
        # results = samsquery.fetch_num_days(host, schema, date1, date2)

        # FIXME (Year, month, day) tuples suffice as args for quotes_historical_yahoo
        date1 = self.date_start - relativedelta(days = 1) # pre-pend extra day for "yesterday"
        date2 = self.date_start + relativedelta(days = self.num_days)
        #print date1, date2

        results = self._DUMMY_QUERY()
        if len(results) == 0:
            print 'no results!?'

        # FIXME next we do some pandas dataframe crap to get results into newly-defined
        #       group by date
        # NOTE: for candlestick, results [quotes] is list of tuples: (utime, open, high, low, close, volume)
        # FIXME return query as list of tuples, where (for a given date)
        #       utime is unix time
        #       open is yesterday's median value
        #       close is today's median value
        #       high is today's max value
        #       low is today's min value
        #       volume is number of records for today
        self.results = results

    def plot(self, dtype):
        """plot date, open, high, low, close

        high-low is a vertical line for span
        open-close is a rectangular bar for span

        high is max value from today
        low  is min value from today

        open  is median value from yesterday
        close is median value from today

        if close >= open, use colorup to color (red) the bar; otherwise use colordown (blue)
        """

        if len(self.results) == 0:
            print 'no results!?'

        if dtype == 'temps':
            nrows, ncols = 4, 7
        elif dtype == 'volts':
            nrows, ncols = 4, 9
        else:
            error('unrecognized data type identifier: %s' % dtype)

        plt.close('all')
        save_file = self.file_prefix + dtype + '.png'
        figset = FigureSet(nrows, ncols, save_file, minvol=self.minvol)

        figset.fig.suptitle('%s for %d Days Starting on GMT %s' % (dtype.upper(), self.num_days, 'DAYONE'), fontsize=18)

        for r in range(nrows):
            for c in range(ncols):
                # FIXME how best to get this (r, c) subresults from uber query results?
                subresults = self.results
                figset.add_subplot(r, c, subresults, 'title')

        # make subplots a bit farther from each other
        # DEFAULTS ARE:
        # left  = 0.125  # the left side of the subplots of the figure
        # right = 0.9    # the right side of the subplots of the figure
        # bottom = 0.1   # the bottom of the subplots of the figure
        # top = 0.9      # the top of the subplots of the figure
        # wspace = 0.2   # the amount of width reserved for blank space between subplots,
        #                # expressed as a fraction of the average axis width
        # hspace = 0.2   # the amount of height reserved for white space between subplots,
                         # expressed as a fraction of the average axis height
        figset.fig.subplots_adjust(left=0.1, hspace=0.25, wspace=0.15)

        # hide x ticks for top plots and y ticks for right plots
        plt.setp([a.get_xticklabels() for a in figset.axarr[0, :]], visible=False)
        plt.setp([a.get_yticklabels() for a in figset.axarr[:, 1]], visible=False)
        plt.setp([a.get_xticklabels() for a in figset.axarr[-1, :]], rotation=90, horizontalalignment='center')

        figset.save()

def parameters_ok():
    """check for reasonableness of parameters"""    

    # FIXME with a great way to quickly verify connectivity to host.schema.table

    # verify that base part of file_prefix exists
    bpath = os.path.dirname(parameters['file_prefix'])
    if not os.path.exists(bpath):
        print 'file_prefix (%s) does not start with valid base path' % parameters['file_prefix']
        return False
    
    # convert start day to date object
    try:
        parameters['date_start'] = parse( parameters['date_start'] ).date()
    except Exception, e:
        print 'could not get date_start input as date object: %s' % e.message
        return False
    
    # make sure we can get an integer value here, as expected
    try:
        parameters['num_days'] = int(parameters['num_days'])
    except Exception, e:
        print 'could not get num_days as int: %s' % e.message
        return False    
    
    # make sure we can get an integer value here, as expected
    try:
        parameters['minvol'] = int(parameters['minvol'])
    except Exception, e:
        print 'could not get minvol as int: %s' % e.message
        return False
    
    # be sure user did not mistype or include a parameter we are not expecting
    s1, s2 = set(parameters.keys()), set(defaults.keys())
    if s1 != s2:
        extra = list(s1-s2)
        missing = list(s2-s1)
        if extra:   print 'extra   parameters -->', extra
        if missing: print 'missing parameters -->', missing
        return False    

    return True # all OK; otherwise, return False somewhere above

def print_usage():
    """print helpful text how to run the program"""
    #FIXME with git keyword sub via following:
    # http://stackoverflow.com/questions/11534655/git-keyword-substitution-like-those-in-subversion
    #print version << BETTER GO AT THIS???
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])
    
def process_data(params):
    """process data with parameters here (after we checked them earlier)"""
       
    # get parameters, mostly for query of samsmon.ee_packet on yoda
    host = parameters['host']
    schema = parameters['schema']
    table = parameters['table']
    file_prefix = parameters['file_prefix']
    date_start = parameters['date_start']
    num_days = parameters['num_days']
    minvol = parameters['minvol'] # half a day's worth, nominally

    # initialize object that will do query, then later produce plot(s)
    sheep = StatusHealthEePlot(host, schema, table, file_prefix, date_start, num_days, minvol)
    
    # perform query
    sheep.query()

    # produce plots
    sheep.plot('temps')
    sheep.plot('volts')

    return 0

def main(argv):
    """describe main routine here"""
    
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parameters_ok():
            nr = NiceResult(process_data, parameters)
            nr.do_work()
            result = nr.get_result()
            return 0 # zero for unix success
        
    print_usage()  

if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))
