#!/usr/bin/env python

from cStringIO import StringIO
import numpy as np
import pandas as pd
from pims.utils.pimsdateutil import dtm2sdn, doytimestr_to_datetime

# read NRT List Request output (sto, tab delimited) file into dataframe
def polar_sto2dataframe(stofile):
    """read ascii sto file into dataframe"""
    s = StringIO()
    with open(stofile, 'r') as f:
        # Read and ignore header lines
        header = f.readline() # labels
        s.write(header)
        is_data = False
        for line in f:
            if line.startswith('#Start_Data'):
                is_data = True
            if line.startswith('#End_Data'):
                is_data = False
            if is_data and not line.startswith('#Start_Data'):
                s.write(line)
    s.seek(0) # "rewind" to the beginning of the StringIO object
    df = pd.read_csv(s, sep='\t')
    
    # drop the unwanted "#Header" column
    df = df.drop('#Header', 1)
    column_labels = [ s.replace('Timestamp : Embedded GMT', 'GMT') for s in df.columns.tolist()]
    df.columns = column_labels
    
    # drop Unnamed columns
    for clabel in column_labels:
        if clabel.startswith('Unnamed'):
            df = df.drop(clabel, 1)

    # use my nomenclature to rename column labels    
    msid_map = {
        'UGZG25RT2163F': 'Fan_Frequency_Hz',
        'UEZE04RT1841J': 'ER4_Drawer2_Ethernet',
        }
    for k, v in msid_map.iteritems():
        df.rename(columns={k: v}, inplace=True)

    ## normalize on/off (as one/zero) for CIR and FIR columns
    #df.TSH_ES05_CIR_Power_Status = [ normalize_cir_fir_power(v) for v in df.TSH_ES05_CIR_Power_Status.values ]
    #df.TSH_ES06_FIR_Power_Status = [ normalize_cir_fir_power(v) for v in df.TSH_ES06_FIR_Power_Status.values ]

    return df

stofile = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_POLAR_Effect_on_60Hz_RMS/polar_fan_freq.sto'
df = polar_sto2dataframe(stofile)
df['dtm'] = df['GMT'].apply(doytimestr_to_datetime)
df['sdn'] = df['dtm'].apply(dtm2sdn)
df.to_csv(stofile.replace('.sto', '.csv'))
raise SystemExit

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
