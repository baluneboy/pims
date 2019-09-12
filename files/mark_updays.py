#!/usr/bin/env python

import os
import datetime
from bs4 import BeautifulSoup
import pandas as pd

from pims.database.pimsquery import query_heartbeat


HEADER = '''
<html>
    <head>
        <style>
            table {text-align: right;}
            table thead th {text-align: center;}
        </style>
    </head>
    <body>
'''

FOOTER = '\n<br><div class="text-align-left">Last modified at <b>GMT %s</b></div>' % str(datetime.datetime.now())[0:-7]

FOOTER += '''
    </body>
</html>
'''


def write_updays_html_file(htm_file):
    computers = os.environ['SPARKS'].split(' ')
    dfe = pd.DataFrame({'host': computers})
    df = query_heartbeat()
    dfm = pd.merge(df, dfe, on='host', how='outer')
    dfm = dfm.sort_values(by='host')
    dfm = dfm.reset_index(drop=True)
    with open(htm_file, 'w') as f:
        f.write(HEADER)
        f.write(dfm.to_html(bold_rows=True, justify='center', float_format=lambda x: '%.2f' % x))
        f.write(FOOTER)

    # re-read input file as html source this time for bs to work on
    with open(htm_file, 'r') as infile:
        html_src = infile.read()

    # convert html source to beautiful soup
    soup = BeautifulSoup(html_src, "lxml")

    # get first (only) table
    table = soup.findChildren('table')[0]

    # get rows from table
    rows = table.findChildren('tr')

    # iterate over rows, then columns
    for row in rows:
        cells = row.findChildren('td')
        if len(cells) < 4:
            continue
        updays_cell, host_cell = cells[3], cells[1]
        updays = float(updays_cell.getText())
        # change background color to gold if up more than 60 days
        if updays > 60.0:
            updays_cell.attrs['bgcolor'] = '#FFD700'
            host_cell.attrs['bgcolor'] = '#FFD700'

    # write marked up soup as html to new file
    with open(htm_file, 'w') as f:
        f.write(soup.prettify().encode('UTF-8'))


if __name__ == "__main__":
    htm_file = '/misc/yoda/www/plots/user/sams/status/southpark/updays.htm'
    write_updays_html_file(htm_file)
