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

    # convert like 2014:077:00:02:04 to dates
    df.GMT = [ doytimestr_to_datetime( doy_gmtstr ) for doy_gmtstr in df.GMT ]
    
    return df

def show_columns(stofile):
    """convert sto file to dataframe, then process and write to xlsx"""
    
    # get dataframe from sto file
    df = strata_sto2dataframe(stofile)
    column_list = df.columns.tolist()
    
    print column_list
    return None

    #df.to_csv(stofile.replace('.sto', '_from_dataframe.csv'))
    
    # convert like 2014:077:00:02:04 to dates
    df['Date'] = [ doytimestr_to_datetime( doy_gmtstr ).date() for doy_gmtstr in df.GMT ]

    # get date range from sto file
    date_min = min(df['Date'])
    date_max = max(df['Date'])

    # convert datetimes to str and overwrite GMT with those strings
    df['GMT'] = [ d.strftime('%Y-%m-%d/%j,%H:%M:%S') for d in df.Date ]

    ################################
    ### CIR ###
    # new dataframe (subset) for CIR with grouped_cir being sum of payload hours on daily basis
    df_cir, grouped_cir = process_cir_fir(df, 'cir', 'TSH_ES05_CIR_Power_Status', column_list, stofile)

    ################################
    ### FIR ###
    # new dataframe (subset) for FIR with grouped_fir being sum of payload hours on daily basis
    df_fir, grouped_fir = process_cir_fir(df, 'fir', 'TSH_ES06_FIR_Power_Status', column_list, stofile)
    
    # FIXME
    # - move zero_list and one_list up to here
    # - refactor commonanilty for ER3, ER4, MSG1, and MSG2
    
    ################################
    ### ER3 ###
    # new dataframe (subset) for ER3 (ER3_EE_F04_Power_Status == 'CLOSED')
    df_er3 = dataframe_subset(df, 'er3', 'ER3_EE_F04_Power_Status', column_list)
    
    # normalize to change CLOSED to one, and OPENED to zero
    zero_list = ['off', 'power off', 'opened']
    one_list =  ['on' , 'power on' , 'closed']
    df_er3.ER3_EE_F04_Power_Status = [ normalize_generic(v, one_list, zero_list) for v in df_er3.ER3_EE_F04_Power_Status.values ]        
    
    # pivot to aggregate daily sum for "rack hours" column (similar to grouped_cir)
    grouped_er3 = df_er3.groupby('Date').aggregate(np.sum)
    
    ################################    
    ### ER4 ###    
    # new dataframe (subset) for ER4 (ER4_Drawer2_Power_Status == 'CLOSED')
    df_er4 = dataframe_subset(df, 'er4', 'ER4_Drawer2_Power_Status', column_list)
    
    # normalize to change CLOSED to one, and OPENED to zero
    df_er4.ER4_Drawer2_Power_Status = [ normalize_generic(v, one_list, zero_list) for v in df_er4.ER4_Drawer2_Power_Status.values ]    
    
    # pivot to aggregate daily sum for "rack hours" column
    grouped_er4 = df_er4.groupby('Date').aggregate(np.sum)    

    ################################
    ### MSG OUTLET #1 ###
    # new dataframe (subset) for MSG1 (MSG_Outlet1_Status == 'ON')
    df_msg1 = dataframe_subset(df, 'msg1', 'MSG_Outlet1_Status', column_list)
    
    # normalize to change CLOSED to one, and OPENED to zero
    df_msg1.MSG_Outlet1_Status = [ normalize_generic(v, one_list, zero_list) for v in df_msg1.MSG_Outlet1_Status.values ]    
    
    # replace NaNs wit zeros
    df_msg1.fillna(0)
    
    # pivot to aggregate daily sum for "rack hours" column
    grouped_msg1 = df_msg1.groupby('Date').aggregate(np.sum)    

    ################################
    ### MSG OUTLET #2 ###
    # new dataframe (subset) for MSG2 (MSG_Outlet2_Status == 'ON')
    df_msg2 = dataframe_subset(df, 'msg2', 'MSG_Outlet2_Status', column_list)
    
    # normalize to change CLOSED to one, and OPENED to zero
    df_msg2.MSG_Outlet2_Status = [ normalize_generic(v, one_list, zero_list) for v in df_msg2.MSG_Outlet2_Status.values ]    
    
    # replace NaNs wit zeros
    df_msg2.fillna(0)
    
    # pivot to aggregate daily sum for "rack hours" column
    grouped_msg2 = df_msg2.groupby('Date').aggregate(np.sum)    

    ################################
    ### CU ###
    # get dataframe with CU hour count info
    cu = CuMonthlyQuery(_HOST_SAMS, _SCHEMA_SAMS, _UNAME_SAMS, _PASSWD_SAMS, date_min, date_max)
    cu_querystr = cu._get_query(date_min, date_max)
    s = StringIO()
    s.write(str(cu))
    s.seek(0) # "rewind" to the beginning of the StringIO object
    df_cu = pd.read_csv(s, sep='\t', parse_dates=True, index_col = [0])

    ################################
    ### PAD ###    
    # get dataframe for padtimes
    df_tmp = pd.read_csv('/misc/yoda/www/plots/batch/padtimes/padtimes.csv', parse_dates=True, index_col = [0])
    df_pad = df_tmp.filter(regex='Date|.*_hours')
        
    # create wall clock dataframe
    df_wall_clock = grouped_er3.copy(deep=True)

    # rename column to Wall_Clock
    df_wall_clock.rename(columns={'ER3_EE_F04_Power_Status':  'Wall_Clock'}, inplace=True)
    df_wall_clock['Wall_Clock'] = 24
    
    # merge (union via how='outer') all dataframes except for df_pad...
    #bamf_df = df_wall_clock.join([grouped_er3, grouped_er4, grouped_cir, grouped_fir, grouped_msg1, grouped_msg2, df_cu, df_pad])
    bamf_df = df_wall_clock   
    for gr in [grouped_er3, grouped_er4, grouped_cir, grouped_fir, grouped_msg1, grouped_msg2, df_cu]:
        bamf_df = bamf_df.merge(gr, left_index=True, right_index=True, how='outer')
        
    #...now merge df_pad too, but now get intersection (based on Date index) using how='inner' this time
    bamf_df = bamf_df.merge(df_pad, left_index=True, right_index=True, how='inner')

    # drop unwanted columns
    unwanted_columns = ['mams_ossbtmf_hours', 'iss_radgse_hours', 'mma_0bba_hours', 'mma_0bbb_hours', 'mma_0bbc_hours', 'mma_0bbd_hours']
    for uc in unwanted_columns:
        bamf_df = bamf_df.drop(uc, 1)    

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(xlsxfile, engine='xlsxwriter')

    # Create kpi sheet for monthly percentages
    df_config = read_config_template()
    df_config.to_excel(writer, sheet_name='kpi', index=False)
    
    # Create sheets for dataframes
    bamf_df.to_excel(writer, sheet_name='raw', index=True)
    
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    print 'wrote raw and kpi template sheets to %s' % xlsxfile

    # Reckon GMT range and overwrite last row with totals; where last row is day 1 of next month
    # and write GMT range into kpi sheet cell B1
    overwrite_last_row_with_totals(xlsxfile, df_config, bamf_df)
    print 'reckoned GMT range\nmodified and saved %s with formulas and totals' % xlsxfile

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
    
    #show_columns(sto_file)
    #raise SystemExit
    
    xlsx_file = sto_file.replace('.sto', '.xlsx')

    if False:
        df = read_xlsx(xlsx_file)
        plot_currents(df);
    else:
        df = strata_sto2dataframe(sto_file)
        writer = pd.ExcelWriter(xlsx_file, datetime_format='yyyy-mm-dd / hh:mm:ss')
        df.to_excel(writer, 'ER8_Telemetry', index=False)
        writer.save()
