#!/usr/bin/env python

import datetime
import pandas as pd
from samsquery import query_tsh_packet_temps

TSHINFO = {
    'tshes-05': [datetime.datetime(2018,8,27), datetime.datetime(2018,9,14), datetime.datetime(2018,11,8)],
    'tshes-06': [datetime.datetime(2018,8,28), datetime.datetime(2018,9,10), datetime.datetime(2018,11,30)],
    'tshes-09': [datetime.datetime(2018,6,8), datetime.datetime(2018,11,27), datetime.datetime(2018,11,28)],
}

def write_excel_file(tsh_id, d1, d2):
    """write tsh temperatures for given id, start and stop times"""
    df = query_tsh_packet_temps(tsh_id, d1, d2)
    xlsx_file = '/tmp/%s_%s.xlsx' % (tsh_id, d1.strftime('%Y_%m_%d'))
    writer = pd.ExcelWriter(xlsx_file, datetime_format='yyyy-mm-dd / hh:mm:ss')
    sheet_name = 'raw'
    df.to_excel(writer, sheet_name, index=False)
    writer.save()
    

if __name__ == "__main__":
    for tsh, start_dates in TSHINFO.iteritems():
        for d1 in start_dates:
            d2 = d1 + datetime.timedelta(days=1)
            write_excel_file(tsh, d1, d2)
            