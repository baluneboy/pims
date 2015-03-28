#!/usr/bin/env python

import os
import calendar
from calendar import month_name
import datetime
from dateutil.relativedelta import relativedelta
from HTMLgen import *

def createDoc(title):
    " Create HTML document with heading. "
    heading = title + ' (updated at GMT %s)' % datetime.datetime.now().strftime("%d-%b-%Y/%H:%M:%S")
    doc = SimpleDocument(title=title)
    doc.append( Heading(3, heading) )
    return doc

class MyRmsCalendar(calendar.HTMLCalendar):
    
    # return iterator for one day every N minutes
    def iterminutes(self, everyN):
        """return iterator for one day every N minutes"""
        for i in [''] + ['%02d' % i for i in range(0, 60, everyN)]:
            yield i
            
    # return a minute name as a table header
    def formatminutes(self, m):
        """return a minute name as a table header"""
        if not m:
            return '<th class="noday">%s</th>' % m
        else:
            return '<th class="noday">%sm</th>' % m
        
    # return a hour's minute entry
    def formathourmin(self, h, m):
        """return a hour's minute entry"""
        if not m:
            return '<th>%02dh</th>' % h
        else:
            return '<td>%02d:%02d</td>' % (h, int(m))
        
    # return day name as table row
    def formatdayname(self, theyear, themonth, theday, withyear=True):
        """return day name as table row"""
        s = 'GMT %d-%02d-%02d' % (theyear, themonth, theday)
        v = 60 / self.everyN
        return '<tr><th colspan="%d" class="month">%s</th></tr>' % (v + 1, s)
    
    # return a header for minutes (everyN) as a table row
    def formatminuteheader(self):
        """return a header for a week as a table row"""
        s = ''.join(self.formatminutes(i) for i in self.iterminutes(self.everyN))
        return '<tr>%s</tr>' % s    

    #  return a complete hour as a table row
    def formathour(self, h):
        """return a complete hour as a table row"""
        s = ''.join(self.formathourmin(h, i) for i in self.iterminutes(self.everyN))
        return '<tr>%s</tr>' % s    
    
    # return a formatted day as a table   
    def formatdayeveryNmin(self, theday, basepath, sensor, everyN):
        """return a formatted day as a table"""
        self.theday = theday
        self.basepath = basepath
        self.sensor = sensor
        self.everyN = everyN
        v = []
        a = v.append
        a('<table border="4" cellpadding="2" cellspacing="2" class="month">')
        a('\n')
        a(self.formatdayname(theday.year, theday.month, theday.day, withyear=True))
        a('\n')
        a(self.formatminuteheader())
        a('\n')
        for hour in range(0,24):
            a(self.formathour(hour))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)

# return HTML code for one day, every 5 minutes
def get_html_oneday_every5min(theday):
    """return HTML code for one day, every 5 minutes"""
    cal = MyRmsCalendar(calendar.SUNDAY)
    return cal.formatdayeveryNmin(theday, 'basepath', 'sensor', 5)

def newUpdate():

    # Create HTML doc with title and heading
    doc = createDoc('EXAMPLE')
   
    doc.append(HR())
    doc.append('<br>')
    
    # Append this and last month calendar tables
    oneday_every5min = get_html_oneday_every5min(datetime.date.today())
    doc.append(oneday_every5min)

    # Write to output HTML file
    doc.write("/tmp/oneday_every5min.html")

if __name__ == "__main__":
    newUpdate()
