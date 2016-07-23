#!/usr/bin/env python

import os
import re
import sys
from tempfile import NamedTemporaryFile
from bs4 import BeautifulSoup, Tag
from shutil import copyfile, move

# FIXME (see TODOs in loop that does markup_devices)
# TODO << python module probably in some other 'fileutils' folder under pims

def demo_test():
    pth = '/tmp/raw'
    files = ['2016-06-22.htm', '2016-06-27.htm', '2016-06-29.htm', '2016-06-28.htm', '2016-07-02.htm']
    files = ['070216.htm', '070516.htm']
    for f in files:
        html_file = os.path.join(pth,f)
        new_file = os.path.join(pth + '/new', f)
        matches = get_matches(html_file, _PATTERN)
        print matches
        mark_matches(html_file, matches, new_file)
        print new_file

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

    print f.name
    return f.name

if __name__ == "__main__":
    html_file = sys.argv[1]
    new_file = markup_devices(html_file)
    move(new_file, html_file)
