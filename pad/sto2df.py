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

#from pims.utils.pimsdateutil import hours_in_month, doytimestr_to_datetime, datestr_to_datetime
#from pims.files.utils import mkdir_p, most_recent_file_with_suffix
#from pims.database.samsquery import CuMonthlyQuery, _HOST_SAMS, _SCHEMA_SAMS, _UNAME_SAMS, _PASSWD_SAMS
#from pims.excel.modification import overwrite_last_row_with_totals, kpi_sheet_fill
#from openpyxl.reader.excel import load_workbook
#from xlsxwriter.utility import xl_rowcol_to_cell, xl_range

# read NRT List Request output (sto, tab delimited) file into a dataframe
def emcs_sto2dataframe(sto_file):
    """read ascii sto file into a dataframe"""
    
    s = StringIO()
    with open(sto_file, 'r') as f:
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

    # use nomenclature to rename column labels    
    msid_map = {
            'UEZE08RT1001J': 'HS_Caution_Warning',
            'UEZE08RT1002J': 'HS_Cycle_Count',
            'UEZE08RT1003C': 'HS_ACS_Pump_Current',
            'UEZE08RT1004T': 'HS_ACS_TemperatureAcsSensorPEU',
            'UEZE08RT1005T': 'HS_ACS_TemperatureAcsSensorCEU',
            'UEZE08RT1006T': 'HS_TCS_TemperatureOTDAHX1',
            'UEZE08RT1007T': 'HS_TCS_TemperatureOTDAHX2',
            'UEZE08RT1008T': 'HS_TCS_TemperatureOTDAHX3',
            'UEZE08RT1009T': 'HS_TCS_TemperatureColdPlate1',
            'UEZE08RT1010T': 'HS_TCS_TemperatureColdPlate2',
            'UEZE08RT1011T': 'HS_TCS_TemperatureOTDPEU1',
            'UEZE08RT1012T': 'HS_TCS_TemperatureOTDPEU2',
            'UEZE08RT1013T': 'HS_TCS_TemperatureCEU',
            'UEZE08RT1014T': 'HS_TCS_TemperatureFan',
            'UEZE08RT1015T': 'HS_DA_Temperature1',
            'UEZE08RT1016T': 'HS_DA_Temperature2',
            'UEZE08RT1017T': 'HS_DB_Temperature1',
            'UEZE08RT1018T': 'HS_DB_Temperature2',
            'UEZE08RT1019T': 'HS_SPLC_Temperature',
            'UEZE08RT1020T': 'HS_VAS_Temperature',
            'UEZE08RT1021T': 'HS_VCR_Temperature',
            'UEZE08RT1022T': 'HS_DCDC_Temperature_EBox1',
            'UEZE08RT1023T': 'HS_DCDC_Temperature_EBox2',
            'UEZE08RT1024T': 'HS_DCDC_Temp RBLSS_Box1',
            'UEZE08RT1025T': 'HS_DCDC_Temp RBLSS_Box2',
            'UEZE08RT1026T': 'HS_EC1_Illumination_Temp',
            'UEZE08RT1027T': 'HS_EC2_Illumination_Temp',
            'UEZE08RT1028T': 'HS_EC3_Illumination_Temp',
            'UEZE08RT1029T': 'HS_EC4_Illumination_Temp',
            'UEZE08RT1030T': 'HS_DCDC_Temperature_Ebox1',
            'UEZE08RT1031T': 'HS_DCDC_Temperature_EBox2',
            'UEZE08RT1032T': 'HS_DCDC_Temp_RBLSS_Box1',
            'UEZE08RT1033T': 'HS_DCDC_Temp_RBLSS_Box2',
            'UEZE08RT1034T': 'HS_EC1_Illumination_Temp',
            'UEZE08RT1035T': 'HS_EC2_Illumination_Temp',
            'UEZE08RT1036T': 'HS_EC3_Illumination_Temp',
            'UEZE08RT1037T': 'HS_EC4_Illumination_Temp',
            'UEZE08RT1100J': 'Subset_ID',
            'UEZE08RT1101J': 'PEP_Service_Request_Word',
            'UEZE08RT1102J': 'PEP_Request_Supporting_Data',
            'UEZE03RT1005U': 'ER3_Data_Cycle_Counter',
            'UEZE03RT1389C': 'Unsign_28V_Output_18_Current_Locker3',
            'UEZE03RT1390C': 'Unsign_28V_Output_19_Current_Locker4',
            'UEZE03RT1391C': 'Unsign_28V_Output_20_Current_Locker7',
            'UEZE03RT1392C': 'Unsign_28V_Output_21_Current_Locker8',
            'UEZE03RT1393C': 'Unsign_28V_Output_22_Current_ISIS1)',
            'UEZE03RT1578J': 'Chan_18_OP_State',
            'UEZE03RT1584J': 'Chan_19_OP_State',
            'UEZE03RT1590J': 'Chan_20_OP_State',
            'UEZE03RT1596J': 'Chan_21_OP_State',
            'UEZE03RT1602J': 'Chan_22_OP_State',
            'UEZE03RT1840J': 'HRLC_PLD_Ether9_Active_Inactive',
            'LADP20MDJ764J': 'PL92_Active_Flag',
            'LADP20MDJ765J': 'PL92_HS_Data_Received'
        }
    
    # rename columns based on msid_map
    for k, v in msid_map.iteritems():
        df.rename(columns={k: v}, inplace=True)

    # write csv file to same name as sto, but with csv extension
	csv_file = sto_file.replace('.sto', '.csv')
    df.to_csv(csv_file)
    print 'csv file at %s' % csv_file

    return df

def main(sto_file):
    # convert sto file to dataframe
    df = emcs_sto2dataframe(sto_file)
    #print df
    
if __name__ == '__main__':
    sto_file = sys.argv[1]
    main(sto_file)
