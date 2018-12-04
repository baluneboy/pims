#!/usr/bin/python

import pandas as pd

dr = pd.date_range('1/1/18', periods=3, freq='8H').to_pydatetime()

print dr
