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


def mark_the_table(table, which_class):
    # modify class and border on this table
    table.attrs['class'] = which_class
    table.attrs['border'] = 2
    #headings = table.find_all('th')
    #
    ## modify 6 column headings attrs for our css formatting
    #headings[0].attrs['class'] = 'column-1 column-gmt'
    #headings[1].attrs['class'] = 'column-2 column-device'
    #headings[2].attrs['class'] = 'column-3 column-type'

    # format first 3 columns of all table rows
    all_rows = table.find_all('tr')
    for row in all_rows:
        cells = row.find_all(['th','td'])
        cells[0].attrs['style'] = 'text-align: right'
        cells[1].attrs['style'] = 'text-align: center'
        cells[2].attrs['style'] = 'text-align: left'    
        
        
# css implementation for improved (colorized) html
def NOTYET_device_tables_css_html(html_file):
    """css implementation for improved (colorized) html"""

    # read html input file as html source
    with open(html_file, 'r') as infile:
        html_src = infile.read()

    # convert html source to beautiful soup
    soup = BeautifulSoup(html_src, 'html.parser')
   
    # yellow highlight mark on "HOST" rows (two of them)
    replace_columns(soup, '(\s*)(HOST|MON|TUE|WED|THU|FRI|SAT|SUN)(\s*)', '<td><mark>{text}</mark></td>')
    
    # get the one and only table here
    tables = soup.find_all('table')
    #if len(tables) != 2:
    #    raise Exception('expected exactly two tables here')
    
    for table in tables:
        mark_the_table(tables[0], "okay")
    #mark_the_table(tables[1], "olds")

    # write marked up as html to new file
    tmp_file = html_file.replace('.html', '.temp')
    with open(tmp_file, 'w') as f:
        f.write(soup.encode('UTF-8'))

    #return f.name
    return tmp_file

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
    if len(sys.argv) > 1:
        html_file = sys.argv[1]
    else:
        html_file='/misc/yoda/www/plots/user/sams/status/sensortimes.html'
    new_file = markup_devices(html_file)
    #new_file = device_tables_css_html(html_file)
    move(new_file, html_file)
