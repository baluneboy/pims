#!/usr/bin/env python
version = '$Id$'

# FIXME major kludges when I added "every 5 minutes" intrms (new page and more links)

import os
import sys
import datetime
import shutil
import glob
import re
import calendar
from calendar import month_name
from HTMLgen import *
from collections import OrderedDict
from pims.realtime.buffer_move import main as cleanBuffer
from recipes_fileutils import fileAgeDays
from dateutil.relativedelta import relativedelta
from pims.files.utils import listdir_filename_pattern
# http://pims.grc.nasa.gov/plots/sams/121f05/intrms_10sec_5hz.html
# Linux command for future reference:
# find /misc/yoda/www/plots/sams -mindepth 2 -maxdepth 2 -type f -mmin -60 -name "*.jpg" -exec ls -l --full-time {} \; | grep -v "/interesting/"

# regardless, always do RMS to 121f05intrms.html (every 5 minutes)
# if minutes in [00 30], then also do non-RMS to index.html

##################################################################################################################################
# GLOB PATTERN                                           REGEXP TO PARSE SENSOR                       SUFFIX FOR HTML  STEPMINUTES
_GLOB_PATS = [
('/misc/yoda/www/plots/sams/121f0*/121f0*.jpg',         '/misc/yoda/www/plots/sams/(.*)/.*',            '',               30 ),
('/misc/yoda/www/plots/sams/es0*/es0*.jpg',             '/misc/yoda/www/plots/sams/(.*)/.*',            '',               30 ),
('/misc/yoda/www/plots/sams/laible/121f0*/121f0*.jpg',  '/misc/yoda/www/plots/sams/laible/(.*)/.*',     'ten',            30 ),
('/misc/yoda/www/plots/oss/osstmf/ML_OSSTMF.jpg',       '/misc/yoda/www/plots/oss/(.*)/.*',             '',               30 ),
('/misc/yoda/www/plots/sams/hirap/hirap.jpg',           '/misc/yoda/www/plots/sams/(.*)/.*',            '',               30 ),
('/misc/yoda/www/plots/sams/121f0*/intrms_*.png',       '/misc/yoda/www/plots/sams/(.*)/.*',            'rms',             5 ),
#('/misc/yoda/www/plots/sams/cirfanmon/es05/es05.jpg',   '/misc/yoda/www/plots/sams/cirfanmon/(.*)/.*',  'cirfanmon',       5 ),
]

def getRecentlySnappedSensors(stepMinutes=30, minutesOld=60):
    """ return OrderedDict of sensors with recently-snapped real-time images, some
    examples:
    sensors['121f02']    = '/misc/yoda/www/plots/sams/121f02/121f02.jpg'
    sensors['hirap']     = '/misc/yoda/www/plots/sams/hirap/hirap.jpg'
    sensors['ossbtmf']   = '/misc/yoda/www/plots/oss/osstmf/ML_OSSTMF.jpg'
    # Below are special cases for Mike Laible (JSC/Boeing) or Hayato Ohkuma (JAXA)
    sensors['121f03ten'] = '/misc/yoda/www/plots/sams/laible/121f03/121f03.jpg'
    sensors['121f04one'] = '/misc/yoda/www/plots/sams/laible/121f04/121f04_grid.jpg'
    sensors['121f05ten'] = '/misc/yoda/www/plots/sams/laible/121f05/121f05.jpg'
    sensors['121f08one'] = '/misc/yoda/www/plots/sams/laible/121f08/121f08_grid.jpg'
    """
    sensors = OrderedDict()
    ###                     GLOB PATTERN                                           REGEXP TO PARSE SENSOR                   SUFFIX FOR HTML
    ##snapGlobPats = [    ('/misc/yoda/www/plots/sams/121f0*/121f0*.jpg',         '/misc/yoda/www/plots/sams/(.*)/.*',         '' ),
    ##                    ('/misc/yoda/www/plots/sams/es0*/es0*.jpg',             '/misc/yoda/www/plots/sams/(.*)/.*',         '' ),
    ##                    ('/misc/yoda/www/plots/sams/laible/121f0*/121f0*.jpg',  '/misc/yoda/www/plots/sams/laible/(.*)/.*',  'ten' ),
    ##                    ('/misc/yoda/www/plots/oss/osstmf/ML_OSSTMF.jpg',       '/misc/yoda/www/plots/oss/(.*)/.*',          '' ),
    ##                    ('/misc/yoda/www/plots/sams/hirap/hirap.jpg',           '/misc/yoda/www/plots/sams/(.*)/.*',         '' ),
    ##                    ('/misc/yoda/www/plots/sams/121f0*/intrms_*.png',       '/misc/yoda/www/plots/sams/(.*)/.*',         'rms' ),
    ##                ]
    ##for wildPath, pat, suffix in snapGlobPats:
    for wildPath, pat, suffix, step in _GLOB_PATS:
        results = glob.glob(wildPath)
        regexp = re.compile(pat)
        #print wildPath, len(results)
        for fname in results:
            match = regexp.match(fname)
            if match:
                sensor = match.group(1)
            else:
                sensor = 'unknown'
            sensor += suffix
            fileAgeMinutes = fileAgeDays(fname) * 1440
            if fileAgeMinutes < minutesOld and stepMinutes == step:
                sensors[sensor] = fname
    return sensors

def midnight(d):
    return datetime.datetime.combine(d,datetime.time(0,0,0))

def nextHalfHour(d):
    dtm = midnight(d) - datetime.timedelta(minutes=30)
    while 1:
        dtm += datetime.timedelta(minutes=30)
        yield (dtm)

def nextFiveMinutes(d):
    dtm = midnight(d) - datetime.timedelta(minutes=5)
    while 1:
        dtm += datetime.timedelta(minutes=5)
        yield (dtm)

# return True if input describes date within last 2 days
def within2days(theyear, themonth, day):
    theday = datetime.date(theyear, themonth, day)
    today = datetime.date.today()
    return relativedelta(today, theday).days <= 1

def timeStampedSensorName(dtm, sensor):
    return dtm.strftime('%Y_%m_%d_%H_%M_') + sensor + '.jpg'

# return HTML code for calendar tables for this and last month
def get_html_calendar_tables_last2months(basepath='/misc/yoda/www/plots/user/buffer'):
    """return HTML code for calendar tables for this and last month"""
    today = datetime.date.today()
    this_month = datetime.date(today.year, today.month, 1)
    eom = this_month - relativedelta(days=1)
    prev_month = datetime.date(eom.year, eom.month, 1)
    
    intrmsCal = IntRmsCalendar(calendar.SUNDAY)
    last_month = intrmsCal.formatmonth(prev_month.year, prev_month.month, basepath)
    this_month = intrmsCal.formatmonth(this_month.year, this_month.month, basepath)
    
    both_months = last_month + '<br>' + this_month
    return both_months

# this creates web page of links for past just one day (every 5 min)
def createIntRMSHTML(basepath, theyear, themonth, day, files):
   
    # Build html filename and link
    htmlname = '%d_%02d_%02d_intrms.html' % (theyear, themonth, day)
    link = 'http://pims.grc.nasa.gov/plots/user/buffer/intrms/' + htmlname
    htmlfile = os.path.join(basepath, 'intrms', htmlname)

    # Create HTML doc with title and heading
    doc = createDoc('PIMS Near Real-Time Interval RMS Screenshots')

    # Use files to get list of sensors
    regexPatString = '.*_(?P<sensor>.*rms)\.jpg$'
    regex = re.compile(regexPatString)
    sensorSuperset = list(set( [m.group(1) for m in [regex.match(f) for f in files] if m] ))
    
    # Append ~2-day buffer links
    theday = datetime.date(theyear, themonth, day)
    #dc1 = DayContainerFive(day=theday, sensorSuperset=sensorSuperset)
    cal = IntRmsCalendar(calendar.SUNDAY)
    for sensor in sensorSuperset:
        doc.append( cal.formatdayeveryNmin(theday, basepath, sensor, 5, files) )
        doc.append(HR())

    # Write to output HTML file
    doc.write(htmlfile)
    
    return link

class IntRmsCalendar(calendar.HTMLCalendar):
    
    # return a formatted month as a table
    def formatmonth(self, theyear, themonth, basepath, withyear=True):
        """return a formatted month as a table"""
        self.theyear = theyear
        self.themonth = themonth
        self.basepath = basepath
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
        
    # return a day as a table cell
    def formatday(self, day, weekday):
        """return a day as a table cell"""
        # check for rms.jpg files on this day
        if day == 0:
            return '<td class="noday">&nbsp;</td>' # day outside month
        else:
            fname_pat = '%d_%02d_%02d_.*rms.jpg' % (self.theyear, self.themonth, day)
            recentpath = os.path.join(self.basepath, 'recent')
            files = listdir_filename_pattern(self.basepath, fname_pat) + listdir_filename_pattern(recentpath, fname_pat)
            
            # no hyperlinks because no files for this day
            if not files:
                return '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)
            
            # create intrms.html page for this day
            link = createIntRMSHTML(self.basepath, self.theyear, self.themonth, day, files)
            return '<td class="%s"><a href="%s">%d</a></td>' % (self.cssclasses[weekday], link, day)

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
        
    # return hourminute entry
    def formathourmin(self, h, mstr):
        """return hourminute entry"""
        if not mstr:
            return '<th>%02dh</th>' % h
        else:
            # get file subset
            regexPatString = '.*\d{4}_\d{2}_\d{2}_%02d_%s_%s\.jpg$' % (h, mstr, self.sensor)
            regex = re.compile(regexPatString)
            filesubset = [m.group(0) for m in [regex.match(f) for f in self.files] if m]
            if filesubset:
                thefile = filesubset[0] # FIXME should check for exactly one file match (2+ is unexpected)
                thelink = thefile.replace(self.basepath, 'http://pims.grc.nasa.gov/plots/user/buffer')
                return '<td><a href="%s">%02d:%02d</a></td>' % (thelink, h, int(mstr))
            else:
                return '<td>%02d:%02d</td>' % (h, int(mstr))
        
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
    def formatdayeveryNmin(self, theday, basepath, sensor, everyN, files):
        """return a formatted day as a table"""
        self.theday = theday
        self.basepath = basepath
        self.sensor = sensor
        self.everyN = everyN
        self.files = files
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

# class for every 30 minutes
class SensorContainer(Container):
    """class for every 30 minutes"""
    
    def __init__(self, *args, **kw):
        Container.__init__(self, *args, **kw)
        self.day = kw['day']
        self.sensor = kw['sensor']
        #self.append(Heading(3, self.sensor))
        self.append(Bold(Text(self.sensor)))
        self.append(BR(1))
        self.appendTimeSubdivisions()
        self.append(BR(1))

    def appendTimeSubdivisions(self):
        n = nextHalfHour(self.day)
        for k in range(3):
            half = [n.next() for i in range(0,16)]
            for h in half:
                linkPath = os.path.join('/misc/yoda/www/plots/user/buffer/' + timeStampedSensorName(h, self.sensor))
                if os.path.exists(linkPath):
                    self.append(Href('http://pims.grc.nasa.gov/plots/user/buffer/' + timeStampedSensorName(h, self.sensor), h.strftime('%H:%M')))
                else:
                    self.append(Text(h.strftime('%H:%M')))
            self.append(BR(1))

# class for every 5 minutes
class SensorContainerFive(SensorContainer):
    """class for every 5 minutes"""

    def appendTimeSubdivisions(self):
        n = nextFiveMinutes(self.day)
        for k in range(12):
            twelfth = [n.next() for i in range(0,24)]
            for h in twelfth:
                linkPath = os.path.join('/misc/yoda/www/plots/user/buffer/' + timeStampedSensorName(h, self.sensor))
                linkPathRecent = os.path.join('/misc/yoda/www/plots/user/buffer/recent/' + timeStampedSensorName(h, self.sensor))
                if os.path.exists(linkPath):
                    self.append(Href('http://pims.grc.nasa.gov/plots/user/buffer/' + timeStampedSensorName(h, self.sensor), h.strftime('%H:%M')))
                elif os.path.exists(linkPathRecent):
                    self.append(Href('http://pims.grc.nasa.gov/plots/user/buffer/recent/' + timeStampedSensorName(h, self.sensor), h.strftime('%H:%M')))
                else:
                    self.append(Text(h.strftime('%H:%M')))
            self.append(BR(1))

class DayContainerFive(Container):

    def __init__(self, *args, **kw):
        Container.__init__(self, *args, **kw)
        self.day = kw['day']
        self.sensorSuperset = kw['sensorSuperset']
        self.append(HR())
        self.append(Heading(3, self.day.strftime('GMT %d-%b-%Y')))
        self.appendSensors()
    
    def appendSensors(self):
        for s in self.sensorSuperset:
            self.append( SensorContainerFive(day=self.day, sensor=s) )   
            
class DayContainer(DayContainerFive):
    
    def __init__(self, *args, **kw):
        DayContainerFive.__init__(self, *args, **kw)
        
    def appendSensors(self):
        for s in self.sensorSuperset:
            self.append( SensorContainer(day=self.day, sensor=s) )

def createDoc(title):
    " Create HTML document with heading. "
    heading = title + ' (updated at GMT %s)' % datetime.datetime.now().strftime("%d-%b-%Y/%H:%M:%S")
    doc = SimpleDocument(title=title)
    doc.append( Heading(3, heading) )
    return doc

def disclaimer():
    #
    d = Text('Plots linked below may show time gaps due to LOS, however, those will get filled in ')
    d.append( Href('http://pims.grc.nasa.gov/roadmap','roadmap PDFs.') )
    d.append(BR(1))
    d = Text('Near real-time plots Interval RMS plots are buffered more frequently at ')
    d.append( Href('http://pims.grc.nasa.gov/plots/user/buffer/intrms.html','this link.') )
    d.append(BR(1))    
    d.append('For help, contact')
    d.append(Href('mailto:pimsops@grc.nasa.gov','pimsops@grc.nasa.gov'))
    return d

def otherLinksTable(clean_msg):
    table = Table(
    tabletitle='Other PIMS Products',
    border=2, width=240, cell_align="center",
    heading=[ "Try The Links in This Table" ])
    table.body = []       # Empty list.
    table.body.append( [
        Href('http://pims.grc.nasa.gov/roadmap', 'roadmaps') ] )
    table.body.append( [
        Href('http://pims.grc.nasa.gov/plots/user/buffer/recent','recent (' +
        clean_msg + ')') ] )
    return table

def updateIndexHTML(clean_msg, sensorSuperset):

    # Create HTML doc with title and heading
    doc = createDoc('PIMS ~30-Day Buffer for Real-Time Screenshots')

    # Append disclaimer
    doc.append(disclaimer())

    # Append ~2-day buffer links
    today = datetime.date.today()
    dc1 = DayContainer(day=today, sensorSuperset=sensorSuperset)
    doc.append(dc1)
  
    yesterday = datetime.date.today() - datetime.timedelta(days=1)  
    dc2 = DayContainer(day=yesterday, sensorSuperset=sensorSuperset)
    doc.append(dc2)

    doc.append(HR())

    ## Do "old file" clean-up
    #clean_msg = cleanBuffer()
    
    # Append other links table
    doc.append(otherLinksTable(clean_msg))

    # Write to output HTML file    
    doc.write("/misc/yoda/www/plots/user/buffer/index.html")

# this creates web page of links for past 2 days (every 5 min) and...
# calendar tables for this + last month
def updateRMSHTML(clean_msg, sensorSuperset):

    # Create HTML doc with title and heading
    doc = createDoc('PIMS ~30-Days of Near Real-Time Interval RMS Screenshots')

    ### Append ~2-day buffer links
    ##today = datetime.date.today()
    ##dc1 = DayContainerFive(day=today, sensorSuperset=sensorSuperset)
    ##doc.append(dc1)
    ##
    ##yesterday = datetime.date.today() - datetime.timedelta(days=1)  
    ##dc2 = DayContainerFive(day=yesterday, sensorSuperset=sensorSuperset)
    ##doc.append(dc2)
    
    # Note about using calendar table of links
    doc.append('Use hyperlinks in calendars below to navigate to day of interest.')
    
    doc.append(HR())
    doc.append('<br>')
    
    # Append this and last month calendar tables
    cals = get_html_calendar_tables_last2months()
    doc.append(cals)

    # Write to output HTML file
    doc.write("/misc/yoda/www/plots/user/buffer/intrms.html")

def roundTime(dt=None, roundTo=60):
   """Round a datetime object to any time lapse in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   if dt == None : dt = datetime.datetime.now()
   seconds = (dt - dt.min).seconds
   # // is a floor division, not a comment on following line:
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

def copySnaps(sensorDict, roundTo):
    """ copy screenshots produced by real-time to buffer directory with
    timestamp and sensor in name """
    for theSensor, snapFile in sensorDict.iteritems():
        dtm = roundTime(roundTo=roundTo)
        shutil.copy2(snapFile, os.path.join('/misc/yoda/www/plots/user/buffer/' +
            timeStampedSensorName(dtm, theSensor)))
        #print snapFile, "copied"
    
    # Do "old file" clean-up
    clean_msg = cleanBuffer()
    return clean_msg

def main(stepMinutes):
    sensorDict = getRecentlySnappedSensors(stepMinutes=stepMinutes, minutesOld=60)
    sensorSuperset = sensorDict.keys()
    if stepMinutes == 30:
        clean_msg = copySnaps(sensorDict, roundTo=1800) # 30 minutes
        updateIndexHTML(clean_msg, sensorSuperset)
    elif stepMinutes == 5:
        clean_msg = copySnaps(sensorDict, roundTo=300)  # 5 minutes
        updateRMSHTML(clean_msg, sensorSuperset)
    else:
        return -1
    return 0

if __name__ == '__main__':
    stepMinutes = int( sys.argv[1] )
    sys.exit(main(stepMinutes))
