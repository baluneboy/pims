#!/usr/bin/env python

import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
from matplotlib import animation
import matplotlib.pyplot as plt
import time as tm
import numpy as np
from datetime import datetime, date, time


def demo_query():
    engine = create_engine('mysql://samsops:1sposmas@yoda/samsmon', echo=False)
    df = pd.read_sql_query('select * from ee_packet ORDER BY timestamp DESC LIMIT 500;', con=engine)
    print df


def demo_near_realtime_plot():
    columns = [ "A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5", "prex"]
    df = pd.DataFrame()
    plt.ion()
    plt.show()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    while True:
        now = datetime.now()
        adata = 5 * np.random.randn(1,10) + 25.
        prex = 1e-10 * np.random.randn(1,1) + 1e-10
        outcomes = np.append(adata, prex)
        ind = [now]
        idf = pd.DataFrame(np.array([outcomes]), index=ind, columns=columns)
        df = df.append(idf)
        df.plot(secondary_y=['prex'], ax=ax)
        plt.draw()
        tm.sleep(0.5)

#demo_query()
demo_near_realtime_plot()
