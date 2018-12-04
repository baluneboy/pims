#!/usr/bin/env pythonimp

import datetime
import decimal
import argparser
from main import plotnsave_daterange_histpad, plotnsave_monthrange_histpad, save_range_of_months


def demo_eng_units():
    for n in (10 ** e for e in range(-1, -8, -1)):
        d = decimal.Decimal(str(n))
        print d.to_eng_string()
    x = decimal.Decimal(str(11334264123))
    print x.to_eng_string()


def demo_plotnsave_monthrange_histpad():
    start = datetime.date(2017, 1, 1)
    stop = datetime.date(2017, 3, 1)
    plotnsave_monthrange_histpad(start, stop, sensor='121f03')


def demo_save_range_of_months():
    # FIXME this has to be able to step year boundaries!
    year = 2018
    month1 = 4
    month2 = 11
    save_range_of_months(year, month1, month2, sensor='121f05')


def demo_plotnsave_daterange_histpad():
    #start = datetime.date(2016, 1, 1)
    #stop = datetime.date(2016, 3, 31)
    start = datetime.date(2018, 1, 18)
    stop = datetime.date(2018, 11, 30)    
    stop = datetime.date(2018, 1, 22)    
    plotnsave_daterange_histpad(start, stop, sensor='121f05')


if __name__ == '__main__':
    #demo_eng_units()
    #demo_save_range_of_months()
    demo_plotnsave_daterange_histpad()
