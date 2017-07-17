#!/usr/bin/env python

import os
import sys
import copy
from bs4 import BeautifulSoup, Tag
from pims.files.mark_samsdevicetimes import replace_columns


def table_cat(html_file, new_file):
    replace_color_width = '<td width="33%"><font color="COLOR">{text}</font></td>'
    replace_color_width_bgcolor = '<td width="33%"><font color="COLOR"><mark>{text}</mark></font></td>'

    # read html input file as html source
    with open(html_file, 'r') as infile:
        html_src = infile.read()

    # convert html source to beautiful soup
    soup = BeautifulSoup(html_src, 'lxml')
    soup.prettify()
    
    # yellow highlight mark on "HOST" rows (two of them)
    replace_columns(soup, '(\s*)(HOST|MON|TUE|WED|THU|FRI|SAT|SUN)(\s*)', '<td><mark>{text}</mark></td>')
    
    rows = soup.find_all('tr')
    print 'total of %d rows' % len(rows),
    
    tables = soup.find_all('table')
    print 'in %d tables' % len(tables)
    
    colors = { 0:'black', 1:'red' }
    for i, table in enumerate(tables):
        color = colors[i]
        tr = table.find_all('tr')
        if len(tr) < 5:
            print 'SKIP table index %d, which only has %d rows' % (i, len(tr))
            continue
        print 'table index %d has %d rows' % (i, len(tr))
        cells = table.find_all('td')
        for td in cells:
            txt = td.text.strip()
            txt = txt.encode('utf-8').decode('ascii', 'ignore')
            if 'Dragon' in txt:
                td.replace_with(BeautifulSoup(replace_color_width_bgcolor.replace('COLOR', color).format(text=txt), 'html.parser'))

    # write marked up as html to new file
    with open(new_file, 'w') as f:
        f.write(soup.encode('UTF-8'))


def concatenate_htmls(html_one, html_two, html_out):
    """append html_two to html_one and write to html_out"""
    # read html input files
    with open(html_one, 'r') as infile1:
        html_src1 = infile1.read()
    with open(html_two, 'r') as infile2:
        html_src2 = infile2.read()

    # convert html source to beautiful soup
    soup = BeautifulSoup(html_src1, 'lxml')
    soup2 = BeautifulSoup(html_src2, 'lxml')

    # separator
    b = soup.new_tag('b')
    b.append("- " * 40 * 4)

    # append
    soup.body.append(b)
    for element in soup2.body:
        soup.body.append(copy.copy(element))

    # write marked up as html to new file
    with open(html_out, 'w') as f:
        f.write(soup.encode('UTF-8'))


if __name__ == "__main__":
    # html_file = sys.argv[1]
    # if html_file.endswith('.html'):
    #     new_file = html_file.replace('.html', '_parsed.html')
    # else:
    #     raise Exception('expecting ".html" input file')
    # if not os.path.exists(html_file):
    #     raise Exception('file not found')
    # print new_file
    # table_cat(html_file, new_file)
    html_one = '/home/pims/Documents/ATL/Inc49_as-flown.html'
    html_two = '/home/pims/Documents/ATL/Inc50_as-flown.html'
    html_out = '/home/pims/Documents/ATL/Inc49-50_as-flown.html'
    concatenate_htmls(html_one, html_two, html_out)