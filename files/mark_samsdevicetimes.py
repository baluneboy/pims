#!/usr/bin/env python

import os
import re
import sys
#from tempfile import NamedTemporaryFile
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
            cell_text = col.text.strip()
            col.replace_with(BeautifulSoup(replacement.format(text=cell_text), 'html.parser'))


def markup_devices(html_file):

    # read html input file as html source
    with open(html_file, 'r') as infile:
        html_src = infile.read()

    # convert html source to beautiful soup
    soup = BeautifulSoup(html_src, 'html.parser')
    
    # yellow highlight mark on "HOST" rows (two of them)
    replace_columns(soup, '(\s*)(HOST|MON|TUE|WED|THU|FRI|SAT|SUN)(\s*)', '<td><mark>{text}</mark></td>')
    
    ## FIXME in bigtime.py where html source is first created (for now and convenience we do otherwise here)
    ## iterate over cells and strip blanks
    #cells = soup.find_all('td')
    #td_replace = '<td>{text}</td>'
    #for cell in cells:
    #    cell_text = cell.text.strip()
    #    cell.replace_with(BeautifulSoup(td_replace.format(text=cell_text), 'html.parser'))
        
    ## iterate over tables
    #tables = soup.find_all('table', 'dataframe')
    #for table in tables:
    #    print table
    #    print '---------------------'

    # TODO and FIXME you need to adjust original code for table widths and column widths to get set as needed
    #tables = soup.findAll('table') # this does not find all my tables!?
    
    # TODO and FIXME in original html code, change 2nd and 3rd host_columns for th and td elements to
    #                go right-align and left-align, respectively; LIKE...
    #
    #<th style="text-align: right;">Device</th>
    #<th style="text-align: left;">Type</th>

    # write marked up as html to new file
    tmp_file = html_file.replace('.html', '.temp')
    #with NamedTemporaryFile(delete=False) as f:
    with open(tmp_file, 'w') as f:
        f.write(soup.encode('UTF-8'))

    #return f.name
    return tmp_file


if __name__ == "__main__":
    if len(sys.argv) > 1:
        html_file = sys.argv[1]
    else:
        html_file='/misc/yoda/www/plots/user/sams/status/sensortimes.html'
    new_file = markup_devices(html_file)
    move(new_file, html_file)