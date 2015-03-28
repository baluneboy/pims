#!/usr/bin/env python

import pandas as pd

# Create 2 Pandas dataframes.
a = [1,2,3,4]
b = [2*i for i in a]
df1 = pd.DataFrame({'Stimulus Time': a, 'Reaction Time': b})
df2 = pd.DataFrame({'Chrominance':   b, 'Octaviance':    a})

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('/tmp/simple.xlsx', engine='xlsxwriter')

# Create 2 sheets for 2 DataFrames
df1.to_excel(writer, sheet_name='Sheet1', index=False)
df2.to_excel(writer, sheet_name='Sheet2')

# Close the Pandas Excel writer and output the Excel file.
writer.save()
