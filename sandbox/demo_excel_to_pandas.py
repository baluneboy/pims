#!/usr/bin/env python

import datetime
import pandas as pd
import numpy as np

file_name = '/home/pims/Documents/xactions.xlsx'
file_name = '/misc/yoda/www/plots/user/cir/rmsgauge95th/samsdata_es05_f03.xlsx'
file_name = '/tmp/trash.xlsx'
xl_file = pd.ExcelFile(file_name)

dfs = {sheet_name: xl_file.parse(sheet_name) for sheet_name in xl_file.sheet_names}
df = dfs['Sheet1']

# drop unwanted columns from dataframe
unwanted_columns = [ 'xfpk_hz_1to30hz', 'yfpk_hz_1to30hz', 'zfpk_hz_1to30hz',
                     'xfpk_hz_30to100hz', 'yfpk_hz_30to100hz', 'zfpk_hz_30to100hz',
                     'tmax', 'vmax_mg', 'vmed_mg', 'v95p_mg', 'xmax_mg', 'ymax_mg', 'zmax_mg' ]
for uc in unwanted_columns:
    df = df.drop(uc, 1)

df_es05 = df[ df['sensor'] == 'es05' ]
df_f03 = df[ df['sensor'] == 'f03' ]

pt = pd.pivot_table(df, rows=['sensor'], aggfunc=np.mean)
writer = pd.ExcelWriter('/misc/yoda/www/plots/user/cir/rmsgauge95th/pivot.xlsx', engine='xlsxwriter')
pt.to_excel(writer, sheet_name='pivot', index=True)
writer.save()
