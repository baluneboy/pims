#!/usr/bin/env python

import cStringIO as StringIO
import numpy as np
import pandas as pd

if False:
    txtfile = '/tmp/big.txt'
    df = pd.read_csv(txtfile, sep='\s')
    print np.mean(df.bytes)/1024.0/1024.0 # to get megabytes
    pt = pd.pivot_table(df, rows=['month'], aggfunc=np.mean)
    print pt

txtfile = '/misc/yoda/www/plots/batch/padtimes/2014_du_121f03_kilobytes.txt'
df = pd.read_csv(txtfile, sep='\s')
df['gigabytes'] = df['kilobytes'] / 1024.0 / 1024.0
print df.groupby(['year','month','day'])['gigabytes'].sum()
print df.groupby(['year','month'])['gigabytes'].sum()
