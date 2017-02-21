#!/usr/bin/env python

import sys
import pandas as pd
from cStringIO import StringIO
import matplotlib.pyplot as plt

from strata_helper import STRATA_MSID_MAP, normalize_generic
from pims.utils.pimsdateutil import doytimestr_to_datetime

_UNWANTEDCOLS = ['ER8_CYCLE_COUNTER', 'ER8_CYCLE_COUNTER_STATUS',
'STRATA_CURRENT_STATUS', 'POLAR2_CURRENT_STATUS', 'STRATA_ENABLED_STATUS']

def strata_sto2dataframe(stofile, unwanted_columns=_UNWANTEDCOLS):
    """read ascii strata sto file into dataframe"""
    
    s = StringIO()
    with open(stofile, 'r') as f:
        # read and ignore header lines for now
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
    
    for k, v in STRATA_MSID_MAP.iteritems():
        df.rename(columns={k: v}, inplace=True)
        
    # drop the unwanted "#Header" column
    df = df.drop('#Header', 1)
    column_labels = [ s.replace('Timestamp : Embedded GMT', 'GMT') for s in df.columns.tolist()]
    df.columns = column_labels
   
    # drop unwanted columns
    for clabel in column_labels:
        if clabel in unwanted_columns or clabel.startswith('Unnamed'):
            df = df.drop(clabel, 1)

    # normalize to change CLOSED to one, and OPENED to zero
    zero_list = ['off', 'power off', 'opened']
    one_list =  ['on' , 'power on' , 'closed']
    df.STRATA_ENABLED = [ normalize_generic(v, one_list, zero_list) for v in df.STRATA_ENABLED.values ]        

    # convert like 2014:077:00:02:04 to date objects
    df.GMT = [ doytimestr_to_datetime( doy_gmtstr ) for doy_gmtstr in df.GMT ]
    
    return df

def show_columns(stofile):
    """convert sto file to dataframe, then process and write to xlsx"""
    
    # get dataframe from sto file
    df = strata_sto2dataframe(stofile)
    column_list = df.columns.tolist()
    print column_list
    
def plot_currents(df):
    import matplotlib
    matplotlib.style.use('ggplot')
    plt.figure();
    df.plot();
    plt.show();

def read_xlsx(xlsx_file):
    df = pd.read_excel(xlsx_file)
    return df

if __name__ == "__main__":
    #sto_file = sys.argv[1]
    
    #sto_file = '/misc/yoda/www/plots/user/strata/er8telemetry/strataISS.IN50.Flight.0002-sam20000019411000-4.sto'
    sto_file = '/misc/yoda/www/plots/user/strata/er8telemetry/strataISS.IN50.Flight.0002-sam20000019427000-5.sto'
        
    xlsx_file = sto_file.replace('.sto', '.xlsx')

    if False:
        df = read_xlsx(xlsx_file)
        plot_currents(df);
    else:
        df = strata_sto2dataframe(sto_file)
        writer = pd.ExcelWriter(xlsx_file, datetime_format='yyyy-mm-dd / hh:mm:ss')
        df.to_excel(writer, 'ER8_Telemetry', index=False)
        writer.save()
