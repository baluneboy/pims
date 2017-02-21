#!/usr/bin/env python

import datetime
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

def demo_query():
    engine = create_engine('mysql://UNAME:PWORD@HOST/SCHEMA', echo=False)
    df = pd.read_sql_query('select * from ee_packet ORDER BY timestamp DESC LIMIT 500;', con=engine)
    print df

demo_query()
