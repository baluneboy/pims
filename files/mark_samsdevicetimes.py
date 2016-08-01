#!/usr/bin/env python

import os
import re
import sys
from tempfile import NamedTemporaryFile
from bs4 import BeautifulSoup, Tag
from shutil import copyfile, move

# FIXME (see TODOs in loop that does markup_devices)
# TODO << python module probably in some other 'fileutils' folder under pims


def replace_columns(soup, regex, replacement):
            
    # find text via regular expression among table cells (td)
    columns = soup.findAll('td', text = re.compile(regex))

    # replace each cell in table row that has a cell that matched regexp with <marked> version
    for td in columns:
        tr = td.findParents('tr')[0] # tr is your now your most recent `<tr>` parent
        cols = tr.findAll('td')
        for col in cols:
            col.replace_with(BeautifulSoup(replacement.format(text=col.text), 'html.parser'))

def markup_devices(html_file):

    # read html input file as html source
    with open(html_file, 'r') as infile:
        html_src = infile.read()

    # convert html source to beautiful soup
    soup = BeautifulSoup(html_src)
    
    # yellow highlight mark on "HOST" rows (two of them)
    replace_columns(soup, '(\s*)(HOST|MON|TUE|WED|THU|FRI|SAT|SUN)(\s*)', '<td><mark>{text}</mark></td>')
    
    # FIXME why does only hirap go blue?
    replace_columns(soup, '(\s*)MAM(\s*)', '<td><font color="blue">{text}</font></td>')

    # TODO and FIXME you need to adjust original code for table widths and column widths to get set as needed
    #tables = soup.findAll('table') # this does not find all my tables!?
    
    # TODO and FIXME in original html code, change 2nd and 3rd host_columns for th and td elements to
    #                go right-align and left-align, respectively; LIKE...
    #
    #<th style="text-align: right;">Device</th>
    #<th style="text-align: left;">Type</th>

    # write marked up as html to new file
    with NamedTemporaryFile(delete=False) as f:
        f.write(soup.encode('UTF-8'))

    return f.name


def table_cat(html_file, new_file):
    replace_color_width = '<td width="33%"><font color="COLOR">{text}</font></td>'
    replace_color_width_bgcolor = '<td width="33%"><font color="COLOR"><mark>{text}</mark></font></td>'
    #page = urllib2.urlopen('http://pims.grc.nasa.gov/plots/user/sams/status/sensortimes.html').read()

    # read html input file as html source
    with open(html_file, 'r') as infile:
        html_src = infile.read()

    # convert html source to beautiful soup
    soup = BeautifulSoup(html_src)
    soup.prettify()
    
    # yellow highlight mark on "HOST" rows (two of them)
    #replace_columns(soup, '(\s*)(HOST|MON|TUE|WED|THU|FRI|SAT|SUN)(\s*)', '<td><mark>{text}</mark></td>')      
    
    rows = soup.find_all('tr')
    print 'total of %d rows' % len(rows),
    
    tables = soup.find_all('table')
    print 'in %d tables' % len(tables)
    
    colors = { 0:'black', 1:'red' }
    for i, table in enumerate(tables):
        color = colors[i]
        tr = table.find_all('tr')
        print 'table %d has %d rows' % (i, len(tr))
        cells = table.find_all('td')
        for td in cells:
            txt = td.text.strip()
            if txt in ['HOST', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']:
                td.replace_with(BeautifulSoup(replace_color_width_bgcolor.replace('COLOR', color).format(text=txt), 'html.parser'))
            else:
                td.replace_with(BeautifulSoup(replace_color_width.replace('COLOR', color).format(text=txt), 'html.parser'))    

    # write marked up as html to new file
    with open(new_file, 'w') as f:
        f.write(soup.encode('UTF-8'))


def demo_test():
    html_file = '/Users/ken/Downloads/devtimes.html'
    new_file = '/tmp/trash2.html'
    table_cat(html_file, new_file)

#demo_test(); raise SystemExit

if __name__ == "__main__":
    html_file = sys.argv[1]
    new_file = markup_devices(html_file)
    move(new_file, html_file)
