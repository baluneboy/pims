#!/usr/bin/env python

import datetime
from main import plotnsave_daterange_histpad, plotnsave_monthrange_histpad, save_range_of_months


def demo_plotnsave_monthrange_histpad():
    start = datetime.date(2017, 1, 1)
    stop = datetime.date(2017, 3, 1)
    plotnsave_monthrange_histpad(start, stop, sensor='121f03')


def demo_save_range_of_months():
    # FIXME this has to be able to step year boundaries!
    year = 2017
    month1 = 1
    month2 = 9
    save_range_of_months(year, month1, month2, sensor='121f03')


def demo_plotnsave_daterange_histpad():
    start = datetime.date(2017, 1, 1)
    stop = datetime.date(2017, 9, 30)
    plotnsave_daterange_histpad(start, stop, sensor='121f03')
