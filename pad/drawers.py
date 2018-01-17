#!/usr/bin/env python

import re
import os
import sys
import csv
import numpy as np
import scipy.io as spio
import pandas as pd
import datetime
from cStringIO import StringIO
import matplotlib
import matplotlib.pyplot as plt

from pims.utils.pimsdateutil import hours_in_month, doytimestr_to_datetime, datestr_to_datetime
from pims.files.utils import mkdir_p, most_recent_file_with_suffix
from pims.database.samsquery import CuMonthlyQuery, _HOST_SAMS, _SCHEMA_SAMS, _UNAME_SAMS, _PASSWD_SAMS
from pims.excel.modification import overwrite_last_row_with_totals, kpi_sheet_fill
from openpyxl.reader.excel import load_workbook
from xlsxwriter.utility import xl_rowcol_to_cell, xl_range


DRWRS_MSID_MAP = {
        'UEZE01RT1393C': 'RTS_Drawer1_Current',
        'UVZV01RT1206J': 'RTS_Drawer1_BaseTemp',
        'UEZE04RT1394C': 'RTS_Drawer2_Current',
        'UVZV01RT1306J': 'RTS_Drawer2_BaseTemp',
        }


def drawers_sto2dataframe(stofile, msid_map=DRWRS_MSID_MAP):
    """read ascii sto file into dataframe for SAMS RTS drawers"""
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

    for k, v in msid_map.iteritems():
        df.rename(columns={k: v}, inplace=True)

    return df


if __name__ == '__main__':


    sto_file = sys.argv[1]
    df = drawers_sto2dataframe(sto_file)

    ROT_DEG = 20
    matplotlib.rc('xtick', labelsize=8)

    df.plot(kind='line', x='GMT', y='RTS_Drawer1_Current')
    plt.ylabel('Current (A)')
    plt.xticks(rotation=ROT_DEG)
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, -0.1, 1.1))
    plt.grid()
    plt.savefig('/tmp/RTS_Drawer1_Current.png')

    df.plot(kind='line', x='GMT', y='RTS_Drawer2_Current')
    plt.ylabel('Current (A)')
    plt.xticks(rotation=ROT_DEG)
    plt.axis((x1, x2, -0.1, 1.1))
    plt.grid()
    plt.savefig('/tmp/RTS_Drawer2_Current.png')

    df.plot(kind='line', x='GMT', y='RTS_Drawer1_BaseTemp')
    plt.ylabel('Temp. (C)')
    plt.xticks(rotation=ROT_DEG)
    plt.axis((x1, x2, 20, 28))
    plt.grid()
    plt.savefig('/tmp/RTS_Drawer1_BaseTemp.png')

    df.plot(kind='line', x='GMT', y='RTS_Drawer2_BaseTemp')
    plt.ylabel('Temp. (C)')
    plt.xticks(rotation=ROT_DEG)
    plt.axis((x1, x2, 20, 28))
    plt.grid()
    plt.savefig('/tmp/RTS_Drawer2_BaseTemp.png')

    #plt.show()
