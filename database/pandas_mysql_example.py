#!/usr/bin/env python

import datetime
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

from pims.database.samsquery import query_ee_packet_hs

def pickle_example(d1, d2):
    t1 = d1.strftime('%Y-%m-%d')
    print datetime.datetime.now(), '<<< BEG'
    df = query_ee_packet_hs(d1, d2)
    print datetime.datetime.now(), '<<< END'
    df.to_pickle('/home/pims/temp/df_' + t1 + '.pkl')

def read_plot_pickle(fname, ee, head, ylim):
    meanprops = {
        'marker': 'D',
        'markeredgecolor': 'firebrick',
        'markerfacecolor': 'lightgray',
                  }
    df = pd.read_pickle(fname)
    dfss = df[ df['ee_id'] == ee ]
    print dfss.describe()
    h = 'head%d_temp' % head
    ax = dfss.boxplot(column=[h + 'X', h + 'Y', h + 'Z'],return_type='axes', showmeans=True, meanprops=meanprops)
    plt.setp(ax.set_ylim(ylim))
    plt.title(ee)
    plt.show()
    
if __name__ == "__main__":
    
    #d1 = datetime.datetime(2017,2,16).date()
    #d2 = datetime.datetime(2017,2,17).date()
    #pickle_example(d1, d2)
    #d1 = datetime.datetime(2017,2,17).date()
    #d2 = datetime.datetime(2017,2,18).date()
    #pickle_example(d1, d2)
    #d1 = datetime.datetime(2017,2,18).date()
    #d2 = datetime.datetime(2017,2,19).date()
    #pickle_example(d1, d2)
    
    read_plot_pickle('/home/pims/temp/df_2017-02-18.pkl', '122-f03', 0, [25, 26])
   
    