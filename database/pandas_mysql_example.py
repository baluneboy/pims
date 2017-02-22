#!/usr/bin/env python

import datetime
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

from pims.database.samsquery import query_ee_packet_hs

def demo_query(host, uname, pword):
    constr = 'mysql://%s:%s@%s/samsnew' % (uname, pword, host)
    engine = create_engine(constr, echo=False)
    df = pd.read_sql_query('select * from ee_packet ORDER BY timestamp DESC LIMIT 500;', con=engine)
    print df

if __name__ == "__main__":
    d1 = datetime.datetime(2017,2,16).date()
    d2 = datetime.datetime(2017,2,17).date()
    df = query_ee_packet_hs(d1, d2)
    df_ee02 = df[ df['ee_id'] == '122-f02' ]
    print len(df)
    print len(df_ee02)