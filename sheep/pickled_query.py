#!/usr/bin/env python

import datetime
from dateutil import relativedelta
import pandas as pd
from pims.database.samsquery import query_ee_packet_hs
    
def pickle_date_range(start_date, end_date, just_weekdays=False):
    if just_weekdays:
        date_range_func = pd.bdate_range # just weekdays
    else:
        date_range_func = pd.date_range  # all days
    date_range = date_range_func(start=start_date, end=end_date)
    for d1 in date_range:
        t1 = d1.strftime('%Y-%m-%d')
        d2 = d1 + relativedelta.relativedelta(days=1)
        print 'working on %s' % t1,
        df = query_ee_packet_hs(d1, d2)
        df.to_pickle('/misc/yoda/www/plots/user/sheep/df_ee_pkt_hs_' + t1 + '.pkl')
        print 'done'

if __name__ == "__main__":
    #d1 = datetime.datetime(2017,1,1).date()
    #d2 = datetime.datetime(2017,2,20).date()
    d1 = datetime.datetime(2016,12,31).date()
    d2 = datetime.datetime(2017,1,1).date()
    pickle_date_range(d1, d2, just_weekdays=False)
