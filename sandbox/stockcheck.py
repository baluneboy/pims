#!/usr/bin/env python

import datetime
#import pandas.io.data as web
from pandas_datareader import data as web

csa = ['SNXFX', 'SKSEX', 'SWHGX', 'GTCSX']
bmo = ['LTRYX', 'FIHBX', 'PARCX', 'VBIAX', 'DAGVX', 'HACAX', 'MLRRX', 'VFIAX', 'PCBIX', 'JVMRX', 'RPMGX', 'STSVX', 'LSSIX', 'CSRSX']
#start = datetime.datetime(2001,8,1)
#end = datetime.datetime(2015,2,13)
start = datetime.datetime(2017,8,10,12,0,0)
end = datetime.datetime(2017,8,10,16,0,0)

def get_port_dataframe(funds, start, end):
    port = web.DataReader(funds, 'yahoo', start, end)
    return port.to_frame()

df_csa = get_port_dataframe(csa, start, end)
df_csa.to_csv('/tmp/csa.csv')

df_bmo = get_port_dataframe(bmo, start, end)
df_bmo.to_csv('/tmp/bmo.csv')
