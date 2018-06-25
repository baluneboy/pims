#!/usr/bin/env python

import re
import os
import sys
import csv
import glob
import numpy as np
import scipy.io as spio
import pandas as pd
import datetime
from cStringIO import StringIO
import matplotlib
import matplotlib.pyplot as plt
from dateutil import parser

from pims.utils.pimsdateutil import hours_in_month, doytimestr_to_datetime, datestr_to_datetime
from pims.files.utils import mkdir_p, most_recent_file_with_suffix
from pims.database.samsquery import CuMonthlyQuery, _HOST_SAMS, _SCHEMA_SAMS, _UNAME_SAMS, _PASSWD_SAMS
from pims.excel.modification import overwrite_last_row_with_totals, kpi_sheet_fill
from openpyxl.reader.excel import load_workbook
from xlsxwriter.utility import xl_rowcol_to_cell, xl_range

from pims.database.samsquery import query_ee_packet_count
from pims.config.conf import get_db_params

# Get sensitive authentication credentials for internal MySQL db query
_SCHEMA_SAMS, _UNAME_SAMS, _PASSWD_SAMS = get_db_params('drawers')
_HOST_SAMS = 'localhost'  # FIXME, WE ASSUME THIS IS RUN ON MIMSY

ER4_DRWRS_MSID_MAP = {
        'UEZE01RT1393C': 'RTS_Drawer1_Current',
        'UVZV01RT1206J': 'RTS_Drawer1_BaseTemp',
        'UEZE04RT1394C': 'RTS_Drawer2_Current',
        'UVZV01RT1306J': 'RTS_Drawer2_BaseTemp',
        }

ER5_DRWRS_MSID_MAP = {
        'UEZE01RT1393C': 'RTS_Drawer1_Current',
        'UVZV01RT1206J': 'RTS_Drawer1_BaseTemp',
        'UEZE05RT1393C': 'IGNORE',
        'UEZE04RT1394C': 'IGNORE',
        'UEZE05RT1394C': 'RTS_Drawer2_Current',
        'UVZV01RT1306J': 'RTS_Drawer2_BaseTemp',
        }

MSID_TEMPLATES = {
    '/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/drwrs2017001-2017032.sto':           ER4_DRWRS_MSID_MAP,
    '/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/drawer_current_tempER5.sto':         ER5_DRWRS_MSID_MAP,
    '/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/dwr_curr_tem_D2_ER5_D1_ER1_031.sto': ER4_DRWRS_MSID_MAP,
    '/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/drwrs2018019-2018039.sto':           ER5_DRWRS_MSID_MAP,
}


def get_sto_header_lines(sto_file, num_lines=3):
    """get first num_lines of sto file"""
    with open(sto_file) as f:
        head = [next(f) for x in xrange(num_lines)]
    return head


def get_msid_map(sto_file, templates=MSID_TEMPLATES):
    msid_map = None
    for temp_file, msid_map in templates.iteritems():
        template = get_sto_header_lines(temp_file)
        h = get_sto_header_lines(sto_file)
        if h == template:
            # header lines for sto_file matches current template file
            return msid_map


def drawers_sto2dataframe(stofile, msid_map=ER4_DRWRS_MSID_MAP):
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


def ee_pkt_gap_check(d1, host='localhost', schema='samsnew', table='ee_packet'):
    _SCHEMA, _UNAME, _PASSWD = get_db_params('drawers')
    d2 = d1 + datetime.timedelta(days=1, minutes=5)
    df = query_ee_packet_count(d1, d2, table='ee_packet', schema=_SCHEMA, host=host, user=_UNAME, passwd=_PASSWD)
    df['deltasec'] = df.timestamp.diff().shift(-1) / np.timedelta64(1, 's')
    return df


def loop_days_ee_pkt_gaps(d1):
    d2 = d1 + datetime.timedelta(days=31)
    drange = pd.date_range(d1, d2)
    for d in drange:
        df = ee_pkt_gap_check(d)
        df_gaps = df[df['deltasec'] > 600.0]
        if df_gaps.empty:
            print d.date(), 'empty'
        else:
            print d.date()
            print df_gaps
            print '-' * 32


def run_ee_pkt_gap_check(daystr):
    d1 = parser.parse(daystr)
    loop_days_ee_pkt_gaps(d1)


def plot_data(bname, df, title, ylabel, ymin, ymax, interval_sec=300, rot_deg=20, out_dir='/tmp'):

    if interval_sec is None:
        # no rolling mean
        df = df.dropna(subset=[title])
        df.plot(kind='line', x='GMT', y=title)
        
    else:
        # FIXME we assume original df has time steps of 10 seconds
        if interval_sec < 10:
            error('abort, we are assuming original data has time step of 10 seconds')
            
        df_new = df.copy()
        prefix = interval_sec / 60.0
        prefix_str = '%0.2fmRollingMean_' % prefix
        prefix_str = prefix_str.replace('0.', 'Zp')
        df_new[prefix_str + title] = df[title].rolling(window=interval_sec/10).mean()
        df_new.plot(kind='line', x='GMT', y=prefix_str + title)

    plt.ylabel(ylabel)
    plt.xticks(rotation=rot_deg)
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, ymin, ymax))
    plt.grid()        
    pdf_bname = bname + '_' + title + '.pdf'
    pdf = os.path.join(out_dir, pdf_bname)
    fig = plt.gcf()
    fig.set_size_inches(11, 8.5)
    plt.savefig(pdf, dpi=120)
    print 'evince %s &' % pdf
    

def concat_drawers_sto_files(bname, glob_pat=None):
    if glob_pat is None:
        glob_pat = '/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/drwrs2017???-201????.sto'
        
    sto_files = glob.glob(glob_pat)
    sto_files.sort()
    df = drawers_sto2dataframe(sto_files[0])
    for f in sto_files[1:]:
        df2 = drawers_sto2dataframe(f)
        df = df.append(df2)
        #print len(df2), len(df)
    
    print 'done concat, now plot...'
    
    #bname = 'concat2017'
    ROT_DEG = 20
    INT_SEC = 60*5  # INT_SEC-second rolling mean
    matplotlib.rc('xtick', labelsize=8)
    
    pdir = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_RTSD2_in_ER5'
    cdir = os.path.join(pdir, 'current')
    tdir = os.path.join(pdir, 'temperature')
    cdir1 = os.path.join(cdir, 'Drawer1')
    cdir2 = os.path.join(cdir, 'Drawer2')
    tdir1 = os.path.join(tdir, 'Drawer1')
    tdir2 = os.path.join(tdir, 'Drawer2')    
    plot_data(bname, df, 'RTS_Drawer1_Current', 'Current (A)', -0.1, 1.1, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=cdir1)
    plot_data(bname, df, 'RTS_Drawer2_Current', 'Current (A)', -0.1, 1.1, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=cdir2)
    plot_data(bname, df, 'RTS_Drawer1_BaseTemp', 'Temp. (C)',    20,  28, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=tdir1)
    plot_data(bname, df, 'RTS_Drawer2_BaseTemp', 'Temp. (C)',    20,  28, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=tdir2)

#concat_drawers_sto_files('concat201678', glob_pat='/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/drwrs201????-201????.sto')
#sys.exit('bye')

def old_main():
    """this is 5-minute rolling mean for spans on the order of days/months"""
    
    sto_file = sys.argv[1]
    bname = os.path.basename(sto_file).replace('.sto', '')
    
    # /misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/drwrs2018004-2018015.sto
    # if basename does not match expected pattern, then abort
    pat = 'drwrs\d{7}-\d{7}'
    if re.match(pat, bname) is None:
        print 'abort because basename of STO file does not match day-to-day pattern'
        sys.exit(-1)
    
    df = drawers_sto2dataframe(sto_file)

    ROT_DEG = 20
    INT_SEC = 10  # INT_SEC-second rolling mean
    matplotlib.rc('xtick', labelsize=8)
    
    pdir = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_RTSD2_in_ER5'
    cdir = os.path.join(pdir, 'current')
    tdir = os.path.join(pdir, 'temperature')
    cdir1 = os.path.join(cdir, 'Drawer1')
    cdir2 = os.path.join(cdir, 'Drawer2')
    tdir1 = os.path.join(tdir, 'Drawer1')
    tdir2 = os.path.join(tdir, 'Drawer2')    
    plot_data(bname, df, 'RTS_Drawer1_Current', 'Current (A)', -0.1, 1.1, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=cdir1)
    plot_data(bname, df, 'RTS_Drawer2_Current', 'Current (A)', -0.1, 1.1, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=cdir2)
    plot_data(bname, df, 'RTS_Drawer1_BaseTemp', 'Temp. (C)',    20,  28, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=tdir1)
    plot_data(bname, df, 'RTS_Drawer2_BaseTemp', 'Temp. (C)',    20,  28, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=tdir2)
    

def helen(sto_file):
    #sto_file = '/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/drawer_current_tempER5.sto'
    #sto_file = '/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/dwr_curr_tem_D2_ER5_D1_ER1_031.sto'
    #sto_file = '/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/dwr_ER4_ER1_screen_008.sto'   
    #sto_file = '/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/dwr_ER4_ER1_pre-scr_008.sto'
    
    this_map = get_msid_map(sto_file)
    bname = os.path.basename(sto_file).replace('.sto', '')    
    df = drawers_sto2dataframe(sto_file, msid_map=this_map)    
    ROT_DEG = 20
    INT_SEC = 300  # None
    matplotlib.rc('xtick', labelsize=8)
    pdir = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_RTSD2_in_ER5'
    cdir = os.path.join(pdir, 'current')
    tdir = os.path.join(pdir, 'temperature')
    cdir1 = os.path.join(cdir, 'Drawer1')
    cdir2 = os.path.join(cdir, 'Drawer2')
    tdir1 = os.path.join(tdir, 'Drawer1')
    tdir2 = os.path.join(tdir, 'Drawer2')    
    plot_data(bname, df, 'RTS_Drawer1_Current', 'Current (A)', -0.1, 1.1, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=cdir1)
    plot_data(bname, df, 'RTS_Drawer2_Current', 'Current (A)', -0.1, 1.1, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=cdir2)
    plot_data(bname, df, 'RTS_Drawer1_BaseTemp', 'Temp. (C)',    20,  28, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=tdir1)
    plot_data(bname, df, 'RTS_Drawer2_BaseTemp', 'Temp. (C)',    20,  28, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=tdir2)


if __name__ == '__main__':
    """ASSUMED MSID MAP AND no rolling mean here, plot just for short/few hours span"""

    sto_file = '/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/drwrs2018019-2018039.sto'
    sto_file = '/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/drwrs201813310-13410.sto'  # no thinning
    sto_file = '/misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/drwrs201813310t13410.sto'  # every 10-second thinning
    helen(sto_file)
    sys.exit('bye')

    sto_file = sys.argv[1]
    bname = os.path.basename(sto_file).replace('.sto', '')
    
    # /misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/drwrs2017358_12-14.sto
    # /misc/yoda/www/plots/batch/padtimes/NRT_sto_files/drawers/drwrs2017036_13-15.sto
    # if basename does not match expected pattern, then abort
    #pat = 'drwrs\d{7}_\d{2}-\d{2}'
    pat = 'drwrs\d{7}-\d{7}'
    if re.match(pat, bname) is None:
        #print 'abort because basename of STO file does not match hour-to-hour pattern'
        print 'abort because basename of STO file does not match day-to-day pattern'
        sys.exit(-1)
    
    df = drawers_sto2dataframe(sto_file)

    ROT_DEG = 20
    INT_SEC = 300  # None for no rolling mean; 300 for 5-minute rolling mean
    matplotlib.rc('xtick', labelsize=8)
    
    pdir = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_RTSD2_in_ER5'
    cdir = os.path.join(pdir, 'current')
    tdir = os.path.join(pdir, 'temperature')
    cdir1 = os.path.join(cdir, 'Drawer1')
    cdir2 = os.path.join(cdir, 'Drawer2')
    tdir1 = os.path.join(tdir, 'Drawer1')
    tdir2 = os.path.join(tdir, 'Drawer2')    
    plot_data(bname, df, 'RTS_Drawer1_Current', 'Current (A)', -0.1, 1.1, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=cdir1)
    plot_data(bname, df, 'RTS_Drawer2_Current', 'Current (A)', -0.1, 1.1, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=cdir2)
    plot_data(bname, df, 'RTS_Drawer1_BaseTemp', 'Temp. (C)',    20,  28, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=tdir1)
    plot_data(bname, df, 'RTS_Drawer2_BaseTemp', 'Temp. (C)',    20,  28, interval_sec=INT_SEC, rot_deg=ROT_DEG, out_dir=tdir2)
