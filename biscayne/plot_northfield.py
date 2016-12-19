#!/usr/bin/env python

"""
Plot dataframe from concatenated from race day pickle files.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pims.files.mark_northfield import count_e


def read_pik(pik_file):
    return pd.read_pickle(pik_file)


def get_new_column(df):
    df['NUME'] = map(count_e, df.HORSE)
    return df

    
def plot_dataframe(df, gridsize=9):
    #my_axes = df.plot(kind='scatter', x='NUME', y='FINISH', alpha=0.15)
    my_axes = df.plot(kind='hexbin', x='NUME', y='FINISH', gridsize=gridsize)
    xmin, xmax = -1, 10
    ymin, ymax = -1, 10
    my_axes.set_xlim([xmin, xmax])
    my_axes.set_ylim([ymin, ymax])
    my_axes.invert_yaxis()
    my_axes.xaxis.set_ticks(np.arange(xmin + 1, xmax, 1.0))
    my_axes.yaxis.set_ticks(np.arange(ymin + 1, ymax, 1.0))
    

def cat_dataframes(files):
    df = pd.concat(read_pik(f) for f in files)      
    return df


def plot_files(files):
    df = cat_dataframes(files)
    df = get_new_column(df)
    plot_dataframe(df, gridsize=9)
    plt.show()


def demo_scatter():
    N = 50
    x = np.random.rand(N)
    y = np.random.rand(N)
    colors = np.random.rand(N)
    area = np.pi * (15 * np.random.rand(N))**2  # 0 to 15 point radiuses
    
    #plt.scatter(x, y, s=area, c=colors, alpha=0.5)
    plt.scatter(x, y, alpha=0.3)
    plt.show()


def demo_quick():
    pik_file = sys.argv[1]
    df = read_pik(pik_file)
    df = get_new_column(df)
    #print df
    plot_dataframe(df)
    plt.show()

    
def demo_hexbin():
    pth = '/Users/ken/NorthfieldBackups/raw'
    my_files = [
    '031616.pik', '060116.pik', '060416.pik', '060616.pik', '060716.pik',
    '060816.pik', '061116.pik', '061316.pik', '061416.pik', '061516.pik',
    '061816.pik', '062116.pik', '062215.pik', '062216.pik', '062516.pik',
    '062716.pik', '062816.pik', '062916.pik', '070216.pik', '070316.pik',
    '070516.pik', '070616.pik', '071316.pik', '071616.pik', '071816.pik',
    '071916.pik', '072316.pik', '072516.pik', '072616.pik', '072716.pik',
    '073016.pik', '080116.pik', '080216.pik', '080316.pik', 
    ]
    files = [os.path.join(pth, f) for f in my_files]
    plot_files(files)


if __name__ == '__main__':
    #demo_scatter()
    #demo_quick()
    demo_hexbin()
