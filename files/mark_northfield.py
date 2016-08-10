#!/usr/bin/env python

import os
import re
import sys
import numpy as np
import datetime
from dateutil import parser
from collections import OrderedDict
from bs4 import BeautifulSoup, Tag
import pandas as pd
from shutil import copyfile

from mark_samsdevicetimes import replace_columns
from pims.utils.text2num import small_ordinal_to_num
from pims.utils.pimsdateutil import northfield_fullfilestr_to_date
from pims.strings.utils import count_letter

# TODO << probably in some other 'fileutils' folder under pims
# - remove dot bak files in /Users/ken/NorthfieldBackups that
#   have filename prefix date field older than 2 months ago

# Regexp for "Cr Hershberger" or maybe "Crist Hershberger" (no quotes)
_PATTERN = r'(?P<first>Cr[^>]*)([^<]+)(?P<last>Hershberger)'


# convert string for time like 1:57.3 to time object like 00:01:56.300000
def to_seconds(s):
    prefix = '0:'
    if ':' not in s:
        prefix += '0:'
    t = parser.parse(prefix + s).time()
    seconds = t.hour * 3600.0 + t.minute * 60.0 + t.second + t.microsecond/1000000.0
    # they use zeros for (I think) disqualified racers, so we need to make that huge
    if seconds < 1.0:
        seconds = np.inf
    return seconds


# convert race order string to int (from like '1o-2' to 1)
def race_orderstr_to_int(ros):
    try:
        v = int(re.match(r'\D*(\d+).*', ros).group(1))
    except AttributeError, e:
        v = np.NaN
    return v


# FIXME -- I would think a class is in order here!?
# Map result row headings to pandas column headings
_HEADINGSMAP = OrderedDict([
    # ORIG         NEW          TYPE             CONVERTER
    ('Date',     ('DATE', 		datetime.date,   None)),
    ('Race',     ('RACE', 		int,             None)),
    ('HN',       ('HN', 		int,             int)),
    ('Horse',    ('HORSE', 	    str,             str)),
    ('Meds',     ('MEDS', 		str,             str)),
    ('PP',       ('PP', 		int,             race_orderstr_to_int)),
    ('1/4',      ('Q1', 		int,             race_orderstr_to_int)),
    ('1/2',      ('Q2', 		int,             race_orderstr_to_int)),
    ('3/4',      ('Q3', 		int,             race_orderstr_to_int)),
    ('STR',      ('STRETCH',	int,             race_orderstr_to_int)),
    ('FIN',      ('FINISH', 	int,             race_orderstr_to_int)),
    ('Time',     ('TIME', 		float,           to_seconds)),
    ('Last Q',   ('LASTQTR', 	float,           to_seconds)),
    ('Odds',     ('ODDS', 		str,             str)),
    ('Driver',   ('DRIVER', 	str,             str)),
    ('Trainer',  ('TRAINER', 	str,             str)),    
])


#def get_matches(fname, pat):
#    matches = set()
#    with open(fname, 'r') as f:
#        contents = f.read()
#        for match in re.finditer(pat, contents):
#            s = match.group(0)
#            matches.add(s)
#    return matches
#
#
#def mark_matches(file_old, matches, file_new):
#    with open(file_new, "wt") as fout:
#        with open(file_old, "rt") as fin:
#            contents = fin.read()
#            for str_old in matches:
#                str_new = '<mark>' + str_old + '</mark>'
#                contents = contents.replace(str_old, str_new)
#        fout.write(contents)
#

def demo_test():
    pth = '/tmp/raw'
    files = ['2016-06-22.htm', '2016-06-27.htm', '2016-06-29.htm', '2016-06-28.htm', '2016-07-02.htm']
    files = ['070216.htm', '070516.htm']
    for f in files:
        old_htm_file = os.path.join(pth,f)
        new_htm_file = os.path.join(pth + '/new', f)
        matches = get_matches(old_htm_file, _PATTERN)
        print matches
        mark_matches(old_htm_file, matches, new_htm_file)
        print new_htm_file

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


def get_cell_with_race(my_row):
    table = my_row.findParents('table')[0] # this is <tr>'s parent table = table
    td = table.find_parents('td')[0]   # this is <table>'s parent cell = td
    ptr = td.parent
    ptab = ptr.find_parents('table')[0]
    innercols = ptab.find_all('td', text = re.compile('.*RACE.*'))
    ic = innercols[0]
    return ic


def race_heading_to_num(race_heading):
    ord_str = race_heading.split(' ')[0]
    return small_ordinal_to_num(ord_str)


def convert_data(data_columns, headings):
    types = [ tup[1] for tup in _HEADINGSMAP.values() ]
    converters = [ tup[2] for tup in _HEADINGSMAP.values() ]    
    for i, col in enumerate(data_columns):
        my_type = types[i]
        if not isinstance(data_columns[i], my_type):
            converter = converters[i]
            data_columns[i] = converter(data_columns[i])
    return pd.DataFrame([data_columns], columns=headings)


def highlight_matching_driver_row(r):
    # entire row has yellow bgcolor
    r.attrs['bgcolor'] = '#ffa'
    cols = r.find_all('td')
    # finish order cell turns white on black
    cols[8].attrs['bgcolor'] = 'black'
    cols[8].attrs['style'] = 'color:white'
    # driver cell turns white on black
    cols[-2].attrs['bgcolor'] = 'black'
    cols[-2].attrs['style'] = 'color:white'
    # horse name cell turns white on black
    cols[1].attrs['bgcolor'] = 'black'
    cols[1].attrs['style'] = 'color:white'     


def highlight_top_race_cell(c):
    c.attrs['bgcolor'] = '#FEBC4E' # orange color
    txt = c.text.strip()
    c.string.replace_with('%s         "Hello Pops", said this orange line.' % txt)      


def count_e(hname):
    hname = hname.lower()
    return count_letter(hname, char='e')


def scrape_into_dataframe(old_htm_file, new_htm_file=None):

    # read old input file as html source
    with open(old_htm_file, 'r') as infile:
        html_src = infile.read()

    # convert html source to beautiful soup
    soup = BeautifulSoup(html_src)

    # convert html filename to date
    d = northfield_fullfilestr_to_date(old_htm_file)
    
    # initialize headings and dataframe
    headings = [ tup[0] for tup in _HEADINGSMAP.values() ]
    df_day = pd.DataFrame(columns=headings)
    
    # initialize flag for any race matching driver of interest
    any_race_has_driver = False
    
    # iterate over outermost (race) tables
    bad_row_counts = []
    race_tables = soup.find_all('table', border="0", cellpadding="0", cellspacing="0", style="border: 1px solid #999999;", width="940")
    for race_table in race_tables:

        # initialize dataframe for this race
        df_race = pd.DataFrame(columns=headings)

        # initialize flag for matching driver in this particular race
        this_race_has_driver = False
        
        # get inner, 1st gray table that contains cell like FIRST RACE
        gray_table = race_table.find_all('table', bgcolor="#e1e1e1", style="border: 1px solid #999999;", width="100%")[0]
        race_cell = gray_table.find_all('tr')[0].find_all('td')[0]
        race_text = race_cell.text.strip()
        race_num = race_heading_to_num(race_text)

        # get inner, 2nd white table that has result rows
        white_table = race_table.find_all('table', cellpadding="1", cellspacing="0", width="100%")[0]
        result_rows = white_table.find_all('tr')
        #print "\nrace #%02d had %02d entries" % (race_num, len(result_rows) - 1)

        # iterate over result rows to append to dataframe, but skip top heading row
        num_bad_rows = 0
        for result_row in result_rows[1:]:
            data_columns = [d, race_num] # prepend date and race number
            [data_columns.append(c.text.strip()) for c in result_row.find_all('td')]
            try:
                new_row = convert_data(data_columns, headings)
            except:
                num_bad_rows += 1
            else:
                df_race = df_race.append(new_row, ignore_index=True)
            # if the driver matches for Cr Hershberger, then yellow highlight this row
            if re.match(r'Cr.*Hershberger', new_row.DRIVER.values[0]):
                this_race_has_driver = True
                any_race_has_driver = True
                highlight_matching_driver_row(result_row)
        
        bad_row_counts.append(num_bad_rows)
        
        # append this race results to this day's dataframe
        df_day = df_day.append(df_race, ignore_index=True)
        
        # if driver was found, then highlight with orange bgcolor the race_cell
        if this_race_has_driver:
            highlight_top_race_cell(race_cell)
            
            # also, gather interesting info from df_race
            df_race['LASTQPCT'] = 100 * (df_race.LASTQTR / df_race.TIME)
            
            # number of O's in HORSE name
            df_race['NUME'] = map(count_e, df_race.HORSE)
            
            # interesting text to add to top, race cell (orange) line
            criteria = df_race.DRIVER.str.contains(r'Cr.*Hershberger')
            df_slice = df_race[criteria]
            fin = df_slice.FINISH.values[0]     # what place Hershberger finished
            tot = len(df_race)                  # number of horses in this race
            pct = df_slice.LASTQPCT.values[0]   # percentage of time was the Last Qtr
            num = df_slice.NUME.values[0]       # count the letter E in horse name
            if num == 0:
                numstr = 'that had no letter E in its name'
            elif num == 1:
                numstr = 'that had one letter E in its name'
            else:
                numstr = "that had %d letter E's in its name" % num
            fun_str = 'he finished %d of %d with last quarter being %.1f%% of his total time on a horse %s.' % (fin, tot, pct, numstr)
            
            # change race_cell text
            race_cell.string.replace_with("%s: %s" % (race_text, fun_str))

    if sum(bad_row_counts) > 0:
        print '\nrace-by-race count of bad rows =', bad_row_counts
    else:
        print '\nno bad rows in any race'

    # for driver name matches, turn style6 (very top text) blue; else turn red
    if any_race_has_driver:
        style6_color = 'blue'
    else:
        style6_color = 'red'
    for node in soup.findAll(attrs={'class': re.compile(r".*\bstyle6\b.*")}):
        node.attrs['color'] = style6_color # RED  TO STOP READING AT TOP, OR...
                                           # BLUE TO CONTINUE

    #print df_day
        
    # save to pickle (.pik) file
    pik_name = os.path.basename(old_htm_file.replace('.htm', '.pik'))
    pik_path = '/Users/ken/NorthfieldBackups/raw'
    pik_file = os.path.join(pik_path, pik_name)
    df_day.to_pickle(pik_file)
    print 'wrote pickle file %s' % pik_file,
    
    if new_htm_file:
        # write marked up soup as html to new file
        with open(new_htm_file, 'w') as f:
            f.write(soup.prettify().encode('UTF-8'))
        print 'and wrote markup htm file %s' % new_htm_file,


def batch_write():
    pth = '/Users/ken/NorthfieldBackups/raw'
    #my_files = [
    #'011616.htm', '031616.htm', '052115.htm', '052615.htm', '052715.htm',
    #'052815.htm', '060116.htm', '060416.htm', '060616.htm', '060716.htm',
    #'060816.htm', '061116.htm', '061316.htm', '061416.htm', '061516.htm',
    #'061816.htm', '062016.htm', '062116.htm', '062215.htm', '062216.htm',
    #'062315.htm', '062415.htm', '062516.htm', '062615.htm', '062716.htm',
    #'062816.htm', '062915.htm', '062916.htm', '063015.htm', '070216.htm',
    #'070316.htm', '070516.htm', '070616.htm', '070916.htm', '071010.htm',
    #'071116.htm', '071210.htm', '071216.htm', '071310.htm', '071316.htm',
    #'071610.htm', '071616.htm', '071710.htm', '071816.htm', '071910.htm',
    #'071916.htm', '072016.htm', '072215.htm', '072316.htm', '072415.htm',
    #'072516.htm', '072616.htm', '072715.htm', '072716.htm', '072815.htm',
    #'072915.htm', '073016.htm', '080116.htm', '080216.htm', '080316.htm',
    #]
    my_files = [    
    '011616.htm', '052115.htm', '052615.htm', '052715.htm', '052815.htm',
    '062016.htm', '062315.htm', '062415.htm', '062615.htm', '062915.htm',
    '063015.htm', '070916.htm', '071010.htm', '071116.htm', '071210.htm',
    '071216.htm', '071310.htm', '071610.htm', '071710.htm', '071910.htm',
    '072016.htm', '072215.htm', '072415.htm', '072715.htm', '072815.htm',
    '072915.htm',
    ]
    files = [os.path.join(pth, f) for f in my_files]
    for f in files:
        scrape_into_dataframe(f)

#    
#def RECENT_markup(old_htm_file, new_htm_file):
#
#    # read old input file as html source
#    with open(old_htm_file, 'r') as infile:
#        html_src = infile.read()
#
#    # convert html source to beautiful soup
#    soup = BeautifulSoup(html_src)
#
#    # find driver name with regular expression among table cells (td)
#    driver_cells = soup.findAll('td', text = re.compile('C.*Hershberger'))
#
#    # for driver name matches, turn style6 (very top text) blue; else red
#    if len(driver_cells) > 0:
#        style6_color = 'blue'
#    else:
#        style6_color = 'red'
#    for node in soup.findAll(attrs={'class': re.compile(r".*\bstyle6\b.*")}):
#        node.attrs['color'] = style6_color # RED  TO STOP READING AT TOP, OR...
#                                           # BLUE TO CONTINUE
#
#    # get UNIQUE SET of table unique_driver_rows that contain matching driver name
#    # and likewise for the Nth RACE he was in
#    unique_driver_rows = set()
#    unique_race_cells = set()
#    pattern = re.compile("\s*Cr.*Hershberger\s*")
#    for text in driver_cells:
#        tr = text.findParents('tr')[0]     # this is <td>'s parent row   = tr
#        race_cell = get_cell_with_race(tr) # a race cell from a table that has a driver row
#        unique_driver_rows.add(tr)
#        unique_race_cells.add(race_cell)
#        cols = tr.findAll('td')
#        # FIXME we assume when num of columns (cells) for this row is 14 it's to highlight
#        if len(cols) == 14:
#            # finish order turns white on black
#            cols[8].attrs['bgcolor'] = 'black'
#            cols[8].attrs['style'] = 'color:white'
#            # driver turns white on black
#            cols[-2].attrs['bgcolor'] = 'black'
#            cols[-2].attrs['style'] = 'color:white'
#            # horse name turns white on black
#            cols[1].attrs['bgcolor'] = 'black'
#            cols[1].attrs['style'] = 'color:white'
#
#    # change bgcolor of table unique_driver_rows that matches driver name to yellow
#    #print 'there were %d unique driver rows' % len(unique_driver_rows)
#    for r in unique_driver_rows:
#        r.attrs['bgcolor'] = '#ffa'
#        #my_cols = r.find_all('td')
#        ## get driver (Driver) column
#        #jcol = my_cols[-2]
#        #driver_name = jcol.text
#        #if pattern.match(driver_name):
#        #    #print driver_name
#        #    pass
#        ##print my_cols[-2]
#
#    # change bgcolor of cell for the Nth RACE the driver was in
#    for c in unique_race_cells:
#        race_text = c.text.strip()
#        c.attrs['bgcolor'] = '#FEBC4E' # orange color
#        #c.string.replace_with("%s   A useful race summary will eventually go here on this orange line." % race_text)
#
#    # write marked up as html to new file
#    with open(new_htm_file, 'w') as f:
#        f.write(soup.prettify().encode('UTF-8'))

##mdf = pd.read_pickle('/Volumes/serverHD2/data/northfield/raw/072716.pik')
##print mdf
##raise SystemExit

if __name__ == "__main__":
    old_htm_file = sys.argv[1]
    new_htm_file = sys.argv[2]
    print 'Scraping %s,' % old_htm_file,
    scrape_into_dataframe(old_htm_file, new_htm_file=new_htm_file)
    #scrape_into_dataframe(old_htm_file)
    print 'done.',
