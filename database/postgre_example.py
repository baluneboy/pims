#!/usr/bin/env python

import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://ken@localhost:5432/testzero')

df = pd.read_sql_query('select * from "ts"', con=engine)
print df
