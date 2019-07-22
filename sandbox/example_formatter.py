#!/usr/bin/env python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def format_x_date_month_day(ax):   
    # Standard date x-axis formatting block, labels each month and ticks each day
    days = mdates.DayLocator()
    months = mdates.MonthLocator()  # every month
    dayFmt = mdates.DateFormatter('%D')
    monthFmt = mdates.DateFormatter('%Y-%m')
    ax.figure.autofmt_xdate()
    ax.xaxis.set_major_locator(months) 
    ax.xaxis.set_major_formatter(monthFmt)
    ax.xaxis.set_minor_locator(days)

def df_stacked_bar_formattable(df, ax, **kwargs):
    P = []
    lastBar = None

    for col in df.columns:
        X = df.index
        Y = df[col]
        if lastBar is not None:
            P.append(ax.bar(X, Y, bottom=lastBar, **kwargs))
        else:
            P.append(ax.bar(X, Y, **kwargs))
        lastBar = Y
    plt.legend([p[0] for p in P], df.columns)

span_days = 90
start = pd.to_datetime("1-1-2012")
idx = pd.date_range(start, periods=span_days).tolist()
df = pd.DataFrame(index=idx, data={'A':np.random.random(span_days), 'B':np.random.random(span_days)})

plt.close('all')
fig, ax = plt.subplots(1)
df_stacked_bar_formattable(df, ax)
format_x_date_month_day(ax)
plt.show()