#!/usr/bin/env python

import datetime
from datetime import date
from infinity import inf
from intervals import DateInterval
import pandas as pd
from itertools import islice
from copy import copy

from openpyxl import Workbook
from openpyxl import load_workbook


class MyDateInterval(DateInterval):

    @property
    def radius(self):
        if self.length == inf:
            return inf
        return self.length / 2

    @property
    def third(self):
        if self.length == inf:
            return inf
        return self.length / 3


def demo():

    di = MyDateInterval([date(2018, 1, 1), date(2018, 2, 1)])
    print di.radius

    di2 = MyDateInterval([date(2018, 1, 1), date(2018, 1, 2)])
    print di2.third


def OLDdemo_openpyxl_pandas():
    wb = load_workbook(filename='/Users/ken/Documents/20190204_sample.xlsx')
    ws = wb['Sheet1']
    sheet_ranges = wb['Sheet1']
    print sheet_ranges['F2'].value
    data = ws.values
    cols = next(data)[1:]
    data = list(data)
    idx = [r[0] for r in data]
    data = (islice(r, 1, None) for r in data)
    df = pd.DataFrame(data, index=idx, columns=cols)
    print df
    print df.columns


def update_zin_spreadsheet():
    """update zin spreadsheet"""

    # load workbook
    wb = load_workbook(filename='/Users/ken/Documents/20190204_sample.xlsx')
    ws = wb['Sheet1']
    # sheet_ranges = wb['Sheet1']

    # fill first blank A1
    ws['A1'] = 'Category'

    # get dataframe values
    data = ws.values
    cols = next(data)
    data = list(data)
    # idx = [r[0] for r in data]
    data = (islice(r, 0, None) for r in data)
    df = pd.DataFrame(data, columns=cols)
    # print df
    # print df.columns

    # verify header row matches
    expected_columns = [u'Category',
                        u'Inv Manager or Sub-Advisor\nInvestment Option',
                        u'Current Investment Mix',
                        u'Units/Shares',
                        u'Unit Value/Share Price',
                        u'Total Balance']
    if all(df.columns == expected_columns):
        print 'Got %d matching column names' % len(expected_columns)
    else:
        print 'hey wait, our column names do not match'

    # verify current investment mix totals 100%
    df['Current Investment Mix'] = df['Current Investment Mix'].apply(lambda x: float(x[:-1])/100.0)
    cim = df['Current Investment Mix'].sum()
    if cim == 1.0:
        print 'Current Investment Mix adds up to {:,.2f}%'.format(cim * 100.0)
    else:
        print 'not so fast, our current investment mix does not total to 100%'
    ws['C11'] = cim * 100.0

    # insert grand total balance at bottom
    total = df['Total Balance'].sum()
    print 'Grand Total Balance is ${:,.2f}'.format(total)
    ws['F11'] = total

    # copy format to newly inserted cim & grand total balance
    from_to = [('F10', 'F11'), ('C10', 'C11')]
    for c1, c2 in from_to:
        ws[c2].font = copy(ws[c1].font)
        ws[c2].border = copy(ws[c1].border)
        ws[c2].fill = copy(ws[c1].fill)
        ws[c2].number_format = copy(ws[c1].number_format)
        ws[c2].protection = copy(ws[c1].protection)
        ws[c2].alignment = copy(ws[c1].alignment)

    ws['A11'] = 'Grand Total'
    rd = ws.row_dimensions[11]  # get dimension for row 11
    rd.height = 25  # value in points, there is no "auto"

    # save new file
    wb.save("/Users/ken/Documents/20190204_sample_NEW.xlsx")


def demo_openpyxl():
    wb = Workbook()

    # grab the active worksheet
    ws = wb.active

    # Data can be assigned directly to cells
    ws['A1'] = 42

    # Rows can also be appended
    ws.append([1, 2, 3])

    # Python types will automatically be converted
    ws['A2'] = datetime.datetime.now()

    # Save the file
    wb.save("/Users/ken/Documents/20190204_sample.xlsx")


if __name__ == '__main__':
    update_zin_spreadsheet()
    # demo()
