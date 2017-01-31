#!/usr/bin/env python

import calendar
import xml.etree.ElementTree as etree

class MyCustomCalendar(calendar.HTMLCalendar):
    def formatday(self, day, weekday, *notes):
        """
        Return a day as a table cell.
        """        
        if day == 0:
            return '<td class="noday">&nbsp;</td>' # day outside month
        else:
            return '<td class="%s">_%d_</td>' % (self.cssclasses[weekday], day)

myCal = MyCustomCalendar(calendar.SUNDAY)
htmlStr = myCal.formatmonth(2009, 7)
htmlStr = htmlStr.replace("&nbsp;"," ")

root = etree.fromstring(htmlStr)
for elem in root.findall("*//td"):
    if elem.get("class") != "tue":
        continue
    elem.text += "!"

    br = etree.SubElement(elem, "br")
    br.tail = "!"

print etree.tostring(root)