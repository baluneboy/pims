#!/usr/bin/env python

import os
import re
import sys
from bs4 import BeautifulSoup, Tag
from shutil import copyfile

from mark_samsdevicetimes import replace_columns

# TODO << probably in some other 'fileutils' folder under pims
# - remove dot bak files in /Users/ken/NorthfieldBackups that
#   have filename prefix date field older than 2 months ago

# Regexp for "Cr Hershberger" or maybe "Crist Hershberger" (no quotes)
_PATTERN = r'(?P<first>Cr[^>]*)([^<]+)(?P<last>Hershberger)'

def get_matches(fname, pat):
    matches = set()
    with open(fname, 'r') as f:
        contents = f.read()
        for match in re.finditer(pat, contents):
            s = match.group(0)
            matches.add(s)
    return matches

def OLDmark_matches(file_old, str_old, file_new):
    with open(file_new, "wt") as fout:
        with open(file_old, "rt") as fin:
            for line in fin:
                str_new = '<mark>' + str_old + '</mark>'
                print str_old, ' to ', str_new
                fout.write(line.replace(str_old, str_new))

def mark_matches(file_old, matches, file_new):
    with open(file_new, "wt") as fout:
        with open(file_old, "rt") as fin:
            contents = fin.read()
            for str_old in matches:
                str_new = '<mark>' + str_old + '</mark>'
                contents = contents.replace(str_old, str_new)
        fout.write(contents)

def demo_test_OLD():
    pth = '/tmp/raw'
    files = ['2016-06-22.htm', '2016-06-27.htm', '2016-06-29.htm', '2016-06-28.htm', '2016-07-02.htm']
    files = ['070216.htm', '070516.htm']
    for f in files:
        old_file = os.path.join(pth,f)
        new_file = os.path.join(pth + '/new', f)
        matches = get_matches(old_file, _PATTERN)
        print matches
        mark_matches(old_file, matches, new_file)
        print new_file

def demo_test():
    pth = '/tmp/raw'
    files = ['2016-06-22.htm', '2016-06-27.htm', '2016-06-29.htm', '2016-06-28.htm', '2016-07-02.htm']
    files = ['070216.htm', '070516.htm']
    for f in files:
        old_file = os.path.join(pth,f)
        new_file = os.path.join(pth + '/new', f)
        matches = get_matches(old_file, _PATTERN)
        print matches
        mark_matches(old_file, matches, new_file)
        print new_file

def demo_soup(html_file):

    with open(html_file, 'r') as infile:
        html_src = infile.read()
    soup = BeautifulSoup(html_src)

    columns = soup.findAll('td', text = re.compile('C.*Hershberger'))
    if len(columns) > 0:
        style6_color = 'blue'
    else:
        style6_color = 'red'

    for node in soup.findAll(attrs={'class': re.compile(r".*\bstyle6\b.*")}):
        node.attrs['color'] = style6_color # RED TO STOP READING
                                           # BLUE IS CLUE TO CONTINUE

    # blue font for "FIRST RACE" cell
    replacement_racenum = '<td><font color="blue">{text}</font></td>'
    
    # TODO the replace_with does not seem to work???
    
    # FIXME exhaustive testing to see if we can identify and mark just RACE table top line
    #       we also may need workaround if replace_with does not work (to include FIN #)
    #       which has to be parsed from CrH's "white-on-black" cell
    
    rows = set()
    for text in columns:
        tr = text.findParents('tr')[0]
        # tr is your now your most recent `<tr>` parent
        table1 = tr.findParents('table')[0]
        table2 = tr.findParents('table')[1]
        table_cols = table2.findAll('td')
        for tc in table_cols:
            cell_text = tc.text.encode('UTF-8')
            # FIXME for this "if" use regular expression FIRST RACE, SECOND RACE, ... NINETEENTH RACE
            if 'FIRST RACE' in cell_text or 'THIRD RACE' in cell_text:
                tc.attrs['bgcolor'] = '#ffa'
                print type(tc), type(tc.text), tc.text
                #tc.replace_with(BeautifulSoup(replacement_racenum.format(text=tc.text), 'html.parser'))

        rows.add(tr)
        cols = tr.findAll('td')
        if len(cols) == 14:
            cols[8].attrs['bgcolor'] = 'black'
            cols[8].attrs['style'] = 'color:white'

    for r in rows:
        r.attrs['bgcolor'] = '#ffa'

    with open('/tmp/raw/trash2.html', 'w') as f:
        f.write(soup.prettify().encode('UTF-8'))

#demo_soup('/tmp/raw/070516.htm'); raise SystemExit

def markup(old_file, new_file):

    # read old input file as html source
    with open(old_file, 'r') as infile:
        html_src = infile.read()

    # convert html source to beautiful soup
    soup = BeautifulSoup(html_src)

    # find jockey name with regular expression among table cells (td)
    columns = soup.findAll('td', text = re.compile('C.*Hershberger'))

    # for jockey name matches, turn style6 color blue (top text); else red
    if len(columns) > 0:
        style6_color = 'blue'
    else:
        style6_color = 'red'

    # this is the code that actually makes the top text color change
    for node in soup.findAll(attrs={'class': re.compile(r".*\bstyle6\b.*")}):
        node.attrs['color'] = style6_color # RED TO STOP READING
                                           # BLUE IS CLUE TO CONTINUE

    # get UNIQUE set of table rows that contain matching jockey name
    rows = set()
    for text in columns:
        tr = text.findParents('tr')[0]
        # tr is your now your most recent `<tr>` parent
        table = tr.findParents('table')[0]
        print table
        rows.add(tr)
        cols = tr.findAll('td')
        # FIXME we assume when num of columns (cells) for this row is 14 it's to highlight
        if len(cols) == 14:
            cols[8].attrs['bgcolor'] = 'black'
            cols[8].attrs['style'] = 'color:white'

    # change bg color of table row that matches jockey name to yellow
    for r in rows:
        r.attrs['bgcolor'] = '#ffa'

    # write marked up as html to new file
    with open(new_file, 'w') as f:
        f.write(soup.prettify().encode('UTF-8'))

if __name__ == "__OLDmain__":
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    print 'marking matches in %s ' % new_file,
    matches = get_matches(old_file, _PATTERN)
    if matches:
        mark_matches(old_file, matches, new_file)
    else:
        # just copy old_file to new_file
        copyfile(old_file, new_file)
    print 'done',

if __name__ == "__main__":
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    print 'markup matches in %s ' % new_file,
    markup(old_file, new_file)
    print 'done',
