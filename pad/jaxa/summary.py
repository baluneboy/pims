#!/usr/bin/env python
import datetime
from datetimeranger import DateRange
from plot_intervals import BirchenoughSummary
bs = BirchenoughSummary( sensorSubDirRx='mma_accel_.*', dateRange=DateRange( datetime.datetime(2013,9,4), datetime.datetime(2013,9,27) ) )

