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
from pims.sheep.gather_data import process_date_range
from pims.sheep.limits_measures import GROUP_MEASURES, YLIMS

_SIXTEENDAYSAGO = str( datetime.now().date() - timedelta(days=16) )

# input parameters
defaults = {
'file_prefix':      '/tmp/eehsplots_',  # string 1st part of VOLTS or TEMPS png filename
'date_start':       _SIXTEENDAYSAGO,    # date object for start time of plots
'num_days':         '14',               # integer number of days to plot
'minvol':           '40000',            # integer min # of samples for day (count); otherwise, gray candle
'pickle_dir':       '/Users/ken/Downloads', # where to find ee_stats pickle files
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
        #self.fig, self.axarr = plt.subplots(nrows, ncols, sharex='col', sharey='row', figsize=self.figsize, dpi=self.dpi)
        self.fig, self.axarr = plt.subplots(nrows, ncols, sharex='col', figsize=self.figsize, dpi=self.dpi)
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
        
        return self.axarr[r, c]

    def save(self):
        print 'writing', self.save_file, '...',
        self.fig.savefig(self.save_file, dpi=self.dpi, orientation='landscape', transparent=False)
        print 'done'

class StatusHealthEePlot(object):
    """query, then Status and Health EE Plot"""

    def __init__(self, date_start, num_days, minvol, file_prefix, group_measures=GROUP_MEASURES, pickle_dir='/Users/ken/Downloads'):
        self.date_start = date_start
        self.num_days = num_days
        self.minvol = minvol
        self.file_prefix = file_prefix
        self.group_measures = group_measures
        self.pickle_dir = pickle_dir
        self.stats = None

    def _OLD_DUMMY_QUERY(self):
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
    
    def _DUMMY_QUERY(self):
        from collections import namedtuple
        CandlePoint = namedtuple('CandlePoint', ['datenum', 'yesterday_median', 'high', 'low', 'median', 'volume'])

        #             datenum  yestmed  todayhi   todaylo  todaymed  todayvolume
        results = [
                    CandlePoint(735974.0, 125.979, 127.896, 125.9274, 127.332,  4974400.0),
                    CandlePoint(735975.0, 127.736, 127.858, 125.3256, 127.018,  5078700.0),
                    CandlePoint(735976.0, 127.591, 128.336, 125.297,  125.364,    43199.0),
                    CandlePoint(735977.0, 126.094, 127.867, 125.4117, 127.026,  5709600.0),
                    CandlePoint(735978.0, 124.258, 125.086, 123.1651, 124.274,  8895400.0),
                    CandlePoint(735979.0, 124.359, 126.252, 122.3914, 122.439,  9979600.0),
                    CandlePoint(735980.0, 113.213, 118.501, 112.7767, 116.466, 16157800.0),
                    CandlePoint(735981.0, 115.939, 119.562, 115.2426, 117.469,  8851600.0),
                    CandlePoint(735982.0, 119.155, 119.218, 116.379,  117.077,  9238400.0),
                    CandlePoint(735983.0, 116.699, 118.731, 116.255,  116.676,  5446000.0),
                    CandlePoint(735984.0, 116.837, 118.138, 116.8293, 117.163,  4617800.0),
                    CandlePoint(735985.0, 117.293, 117.909, 115.3095, 115.605,  9943199.0),
                    CandlePoint(735986.0, 115.89,  117.393, 115.6531, 116.810,  3942500.0),
                    CandlePoint(735987.0, 117.827, 119.266, 117.5174, 119.266,  8248100.0)
                    ]
        return results

    def OLDquery(self):
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

    def gather_stats(self):
        date_end = self.date_start + relativedelta(days=self.num_days)
        self.stats = process_date_range(self.date_start, date_end, self.group_measures, self.pickle_dir)

    def get_ee_ids(self):
        ees = None
        if self.stats:
            tmp = [ t[1] for t in self.stats.keys() ]
            ees = sorted(list(set(tmp)))
        return ees

    def plot(self, group):
        """candlestick plot (datenum, yesterday_median, high, low, median, volume)

        high-low is a vertical line for that span
        yesterday-today is a rectangular bar for median span

        high is 75% percentile from today
        low  is 25% percentile from today

        if yesterday_median >= today_median, use colorup to color (red) the bar; otherwise use colordown (blue)
        """

        if len(self.stats) == 0:
            print 'no stats! not gathered yet?'

        ## FIXME to make this fit more than 4 EEs in 4 rows
        #if group == 'TEMPS':
        #    nrows, ncols = 4, 7
        #elif group == 'VOLTS':
        #    nrows, ncols = 4, 9
        #else:
        #    raise Exception('unrecognized data type identifier: %s' % group)

        # each group (figure) has RxC subplots
        measures = self.group_measures[group]
        ees = self.get_ee_ids()
        nrows = len(ees)       # Rows are EEs
        ncols = len(measures)  # Columns are measures

        plt.close('all')
        save_file = self.file_prefix + group + '.png'
        figset = FigureSet(nrows, ncols, save_file, minvol=self.minvol)

        figset.fig.suptitle('%s for %d Days Starting on GMT %s' % (group, self.num_days, self.date_start), fontsize=18)

        measures = self.group_measures[group]
        ees = self.get_ee_ids()
        
        # outer-loop is rows (of EES)
        r = 0
        for ee in ees:
            # inner-loop is columns (of measures)
            c = 0
            for measure in measures:
                # key into dict that has measures stats
                key = (group, ee, measure)
                subplot_stats = self.stats[key]
                # add subplot for this EE-measure combo
                ax = figset.add_subplot(r, c, subplot_stats, measure)
                ax.set_ylim(YLIMS[measure])
                c += 1
            r += 1

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
        
        ## for temperatures, use this range
        #if group == 'TEMPS':
        #    for r in range(nrows):
        #        plt.setp([a.set_ylim([23, 30]) for a in figset.axarr[r, :]])

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
       
    # get parameters for: getting data and candlestick plotting
    date_start = parameters['date_start']
    num_days = parameters['num_days']
    minvol = parameters['minvol']
    file_prefix = parameters['file_prefix']
    group_measures = GROUP_MEASURES # FIXME are we ever going to change what we trend track?
    pickle_dir = parameters['pickle_dir']

    # initialize object that will get/hold stats, then later produce plot(s)
    sheep = StatusHealthEePlot(date_start, num_days, minvol, file_prefix, group_measures, pickle_dir)
    
    # gather stats data now
    sheep.gather_stats()

    # produce plots here
    sheep.plot('TEMPS')
    sheep.plot('VOLTS')

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
