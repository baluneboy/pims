#!/usr/bin/env python

import sys
import pandas as pd
import matplotlib
matplotlib.use('wx')
import matplotlib.pyplot as plt
import datetime
import numpy as np
import matplotlib.dates as dates
import mpl_toolkits.axes_grid.axes_size as Size
from mpl_toolkits.axes_grid import Divider

def plot_var(t, df, column):
    # Create plot
    fig, ax = plt.subplots(1, figsize=(11, 8.5))
    y = df[column].values
    ax.plot_date(t, y, '.-')
    
    mng = plt.get_current_fig_manager()
    mng.frame.Maximize(True)
    
    # the rect parameter will be ignored...we will set axes_locator
    rect = (0.1, 0.1, 0.8, 0.8)
    horiz = [Size.Fixed(9)]
    vert =  [Size.Fixed(7)]
    
    fig.suptitle(column, fontsize=20)
    
    # divide the axes rectangle into grid whose size is specified by horiz * vert
    divider = Divider(fig, rect, horiz, vert, aspect=False)

    ax.set_axes_locator(divider.new_locator(nx=0, ny=0))
    plt.setp(ax.get_xticklabels()+ax.get_yticklabels(), visible=True)  
    
    ylim = ax.get_ylim()
    ax.set_ylim( (ylim[0] - 1, ylim[1] + 1))
    # y-axis limits
    #ymin = np.min(y)
    #ymax = np.max(y)
    #yrange = ymax - ymin
    #ax.set_ylim([ymin - 0.1*np.abs(yrange), ymax + 0.1*np.abs(yrange)])
    
    # Note how the hour locator takes the hour or sequence of hours you want to
    # tick, NOT the base multiple
    ax.xaxis.set_major_locator( dates.DayLocator() )
    ax.xaxis.set_minor_locator( dates.HourLocator(np.arange(0,25,4)) )
    ax.xaxis.set_major_formatter( dates.DateFormatter('\n\n%Y-%m-%d') )
    ax.xaxis.set_minor_formatter( dates.DateFormatter('%H:%M') )
    ax.xaxis.grid(True, which="both")
    ax.yaxis.grid(True)
    #plt.tight_layout()
    #plt.show()
    plt.savefig('/tmp/' + column + '.png')

def main(infile):
    # Read data file into dataframe
    #infile = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_Columbus_EMCS_Candidates/EMCSdata3.csv'
    dateparse = lambda x: pd.datetime.strptime(x, '%Y:%j:%H:%M:%S')
    df = pd.read_csv(infile, parse_dates=['GMT'], date_parser=dateparse)
    t = pd.to_datetime(df['GMT'].values)
    
    for c in df.columns:
        if not c.startswith('GMT'):
            plot_var(t, df, c)

if __name__ == "__main__":
    main( sys.argv[1] )
