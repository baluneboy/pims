#!/usr/bin/env python

import os
import calendar
from calendar import month_name
import datetime
from dateutil.relativedelta import relativedelta

class IntRmsCalendar(calendar.HTMLCalendar):
    
    def formatmonth(self, theyear, themonth, basepath, sensor, withyear=True):
        """return a formatted month as a table"""
        self.theyear = theyear
        self.themonth = themonth
        self.basepath = basepath
        self.sensor = sensor
        v = []
        a = v.append
        a('<table border="4" cellpadding="2" cellspacing="2" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)
        
    def formatday(self, day, weekday):
        """return a day as a table cell"""
        if day == 0:
            return '<td class="noday">&nbsp;</td>' # day outside month
        else:
            linkname = '%d_%02d_%02d_hh_mm_%srms.jpg' % (self.theyear, self.themonth, day, self.sensor)
            link = os.path.join(self.basepath, linkname)
            return '<td class="%s"><a href="%s">%d</a></td>' % (self.cssclasses[weekday], link, day)

# return HTML code for calendar tables for this and last month
def get_html_calendar_tables_last2months(sensor='121f05', basepath='/misc/yoda/www/plots/user/buffer'):
    """return HTML code for calendar tables for this and last month"""
    today = datetime.date.today()
    this_month = datetime.date(today.year, today.month, 1)
    eom = this_month - relativedelta(days=1)
    prev_month = datetime.date(eom.year, eom.month, 1)
    
    intrmsCal = IntRmsCalendar(calendar.SUNDAY)
    last_month = intrmsCal.formatmonth(prev_month.year, prev_month.month, basepath, sensor)
    this_month = intrmsCal.formatmonth(this_month.year, this_month.month, basepath, sensor)
    
    both_months = last_month + '<br><br>' + this_month
    return both_months

if __name__ == "__main__":
    last2months = get_html_calendar_tables_last2months(sensor='121f02')
    print last2months
