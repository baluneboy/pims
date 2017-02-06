#!/usr/bin/env python

import datetime
from dateutil import relativedelta
import pandas as pd

def iter_date_range(start_date, end_date, just_weekdays=False):
    if just_weekdays:
        date_range_func = pd.bdate_range # just weekdays
    else:
        date_range_func = pd.date_range  # all days
    date_range = date_range_func(start=start_date, end=end_date)
    for d in date_range:
        print d.strftime('%Y-%m-%d')

if __name__ == "__main__":
    year = 2017
    month = 2
    start_day_this_month = datetime.date(year, month, 1)
    start_day_next_month = start_day_this_month + relativedelta.relativedelta(months=1)
    end_day_this_month = start_day_next_month - relativedelta.relativedelta(days=1)
    iter_date_range(start_day_this_month, end_day_this_month, just_weekdays=True)
