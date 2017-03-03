#!/usr/bin/env python

import sys
import pandas as pd
from cStringIO import StringIO
import matplotlib.pyplot as plt

from pims.utils.pimsdateutil import doytimestr_to_datetime

_UNWANTEDCOLS = ['status']

def labtemp_sto2dataframe(stofile, unwanted_columns=_UNWANTEDCOLS):
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
        
    # drop the unwanted "#Header" column
    df = df.drop('#Header', 1)
    column_labels = [ s.replace('Timestamp : Embedded GMT', 'GMT') for s in df.columns.tolist()]
    df.columns = column_labels
   
    # drop unwanted columns
    for clabel in column_labels:
        if clabel in unwanted_columns or clabel.startswith('Unnamed'):
            df = df.drop(clabel, 1)

    # convert like 2014:077:00:02:04 to date objects
    df.GMT = [ doytimestr_to_datetime( doy_gmtstr ) for doy_gmtstr in df.GMT ]
    
    return df

def show_columns(stofile):
    """convert sto file to dataframe, then process and write to xlsx"""
    
    # get dataframe from sto file
    df = labtemp_sto2dataframe(stofile)
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
    sto_file = '/misc/yoda/www/plots/user/sams/opsnotes/ISS.IN51.Flight.0002-sam20000020107000-1.sto'
        
    xlsx_file = sto_file.replace('.sto', '.xlsx')

    if False:
        df = read_xlsx(xlsx_file)
        plot_currents(df);
    else:
        df = labtemp_sto2dataframe(sto_file)
        writer = pd.ExcelWriter(xlsx_file, datetime_format='yyyy-mm-dd / hh:mm:ss')
        df.to_excel(writer, 'LABtemp', index=False)
        writer.save()
