#!/usr/bin/env python

"""Concatenate HTML files via BeautifulSoup"""

import re
import copy
import datetime
import unicodedata
from dateutil import parser
from bs4 import BeautifulSoup, NavigableString

from pims.patterns.handbookpdfs import _TIGDUR_PATTERN

# non-printable characters
CONTROL_CHARS = ''.join(map(unichr, range(0, 32) + range(127, 160)))
CONTROL_CHAR_RE = re.compile('[%s]' % re.escape(CONTROL_CHARS))

# a placeholder is day zero = Jan 1, 1970
ZERODAY = datetime.date(1970, 1, 1)


def demo_soup(html_file):

    with open(html_file, 'r') as infile:
        html_src = infile.read()
    soup = BeautifulSoup(html_src, 'lxml')

    columns = soup.findAll('td', text=re.compile('TIG|DUR'))

    rows = set()
    for text in columns:
        tr = text.findParents('tr')[0]
        tr.attrs['bgcolor'] = '#ffa'
        rows.add(tr)

    for r in rows:
        r.attrs['color'] = '#fff'

    with open('/home/pims/Documents/ATL/test2.html', 'w') as f:
        f.write(soup.prettify().encode('UTF-8'))


def get_soup(html_file):
    """return [beautiful] soup from html file input"""
    with open(html_file, 'r') as infile:
        html_src = infile.read()
    soup = BeautifulSoup(html_src, 'lxml')
    return soup


def remove_control_chars_and_extra_spaces(s):
    """return string with control characters removed
       also, multi-spaces [and underscores] get collapsed"""
    tmp = CONTROL_CHAR_RE.sub('', s)
    tmp2 = re.sub('_+', '_', tmp)
    return re.sub('\s+', ' ', tmp2)


def concatenate_htmls(html_files, html_out):
    """append html files and write to html_out"""

    # get soup from first html file
    soup = get_soup(html_files[0])

    # iterate over remaining html files
    soup2 = None
    for f in html_files[1:]:
        del soup2
        soup2 = get_soup(f)
        for element in soup2.body:
            soup.body.append(copy.copy(element))

    # write marked up as html to new file
    with open(html_out, 'w') as f:
        f.write(soup.encode('UTF-8'))


def concat_thru_inc52_partial():
    """concatenate ATL html files as of Inc52 (partial Inc52)"""
    html_files = [
        '/home/pims/Documents/ATL/header.html',
        '/home/pims/Documents/ATL/Inc48_as-flown_GUA.html',
        '/home/pims/Documents/ATL/Inc49_as-flown.html',
        '/home/pims/Documents/ATL/Inc50_as-flown.html',
        '/home/pims/Documents/ATL/Inc51_as-flown.html',
        '/home/pims/Documents/ATL/Inc52_as-flown_PARTIAL.html',
        ]
    html_out = '/home/pims/Documents/ATL/IncThru52_as-flown_PARTIAL.html'
    concatenate_htmls(html_files, html_out)


def is_two_event_cells(cells):
    """return True if 2 cells that match event-date profile; else return False"""
    bln = False
    if len(cells) == 2:
        bln = True
    return bln


def concatenate_two_column_htmls(html_files, html_out):
    """parse out two-column entries and append"""

    # get soup from first html file
    soup = get_soup(html_files[0])

    # iterate over remaining html files
    soup2 = None
    for f in html_files[1:]:
        del soup2
        soup2 = get_soup(f)
        for element in soup2.body:
            soup.body.append(copy.copy(element))

    rows = soup.find_all('tr')
    print 'total of %d event rows' % len(rows)

    event_rows = set()
    bln_got_evt = False
    for i, row in enumerate(rows):
        cells = row.find_all(['td', 'th'])
        if bln_got_evt:
            print 'ROW: %d' % i
        if is_two_event_cells(cells):
            row.attrs['bgcolor'] = '#bcbcbc'  # gray bg matching row
            evt = cells[0].text.strip().encode('utf-8').decode('ascii', 'ignore')
            dat = cells[1].text.strip().encode('utf-8').decode('ascii', 'ignore')
            if re.match('\d{2}/\d{2}/\d{4}', dat):
                if 'reboost' in evt.lower():
                    print 'ROW: %d, DATE: %s, EVT: <<%s>>' % (i, dat, remove_control_chars_and_extra_spaces(evt))
                    bln_got_evt = True
                    event_rows.add((i, row))
                    row.attrs['class'] = 'bigevent'
                else:
                    bln_got_evt = False

    columns = soup.findAll(['td', 'th'], text=re.compile('TIG|DUR'))

    # put yellow bg on entire rows that have cell matching TIG|DUR
    tigdur_rows = list()
    for j, c in enumerate(columns):
        print '\n%d: %s' % (j, c.text.strip())
        tr = c.findParents('tr')[0]
        tr.attrs['bgcolor'] = '#ffa' # yellow
        tr.findPrevious('tr').attrs['bgcolor'] = '#bcdada' # scrubsgreen
        tr.findNext('tr').attrs['bgcolor'] = '#bc1234' # bloodred
        tigdur_rows.append(tr)

    # try looking at previous row's first cell and next row's first cell
    tigdur_addresses = soup.findAll(text=re.compile('TIG|DUR'))
    for tigdur_address in tigdur_addresses:
        print '=' * 33
        print tigdur_address.findPrevious('tr').contents[0].string
        print tigdur_address.string
        print tigdur_address.findNext('tr').contents[0].string
        print '-' * 22
        print

    # write soup as html to new file
    soup.prettify()
    with open(html_out, 'w') as f:
        f.write(soup.encode('UTF-8'))


def add_class_attr_to_event_rows(html_file, html_out):
    """add class=bigevent attribute [tag] to two-column rows
       also, for each of 2 columns, align left and bold font
    """

    # get soup from first html file
    soup = get_soup(html_file)

    rows = soup.find_all('tr')
    print 'total of %d event rows' % len(rows)

    for i, row in enumerate(rows):
        cells = row.find_all(['td', 'th'])
        if is_two_event_cells(cells):
            row.attrs['bgcolor'] = '#bcbcbc'  # gray bg matching row
            evt = cells[0].text.strip().encode('utf-8').decode('ascii', 'ignore')
            dat = cells[1].text.strip().encode('utf-8').decode('ascii', 'ignore')
            if re.match('\d{2}/\d{2}/\d{4}', dat):
                row.attrs['class'] = 'bigevent'
                row.attrs['style'] = 'font-weight:bold'
                cells[0].attrs['align'] = 'left'
                cells[1].attrs['align'] = 'left'

    # write soup as html to new file
    soup.prettify()
    with open(html_out, 'w') as f:
        f.write(soup.encode('UTF-8'))


def process_reboost_tigdur_info(html_file, html_out):
    """add class=reboostevent attribute [tag] to 'tig|dur' rows
       also...
    """

    # get soup from first html file
    soup = get_soup(html_file)

    reboosts = dict()

    # find all cells that match 'TIG|DUR' regular expression
    tigdur_addresses = soup.findAll(text=re.compile('TIG|DUR', re.IGNORECASE))
    for tigdur_address in tigdur_addresses:

        # FIXME why doesn't text input work in findPrevious with regular expression?
        # FIXME ...this would find previous bigevent row that matches like ".*reboost.*"

        # rewind to find previous bigevent row
        prev_bigevent_row = tigdur_address.findPrevious('tr', attrs={'class': 'bigevent'})

        # skip this one if we do not have "reboost" in first cell
        tmp = prev_bigevent_row.contents[0].string.strip().encode('utf-8').decode('ascii', 'ignore')
        evt = remove_control_chars_and_extra_spaces(tmp)
        if not re.match('.*reboost.*', evt, re.IGNORECASE):
            continue

        # we now have a bigevent that matches "reboost", so process it
        date_str = prev_bigevent_row.findAll(['td', 'th'])[1].string

        try:
            day = parser.parse(date_str).date()
        except ValueError:
            day = ZERODAY
        except TypeError:
            day = ZERODAY

        tigdur_str = remove_control_chars_and_extra_spaces(tigdur_address.string.replace('\n', ' '))
        reboosts[(evt, day)] = tigdur_str

    for k, r in reboosts.iteritems():
        # TODO for "OK" [matches] construct ssh cmd for mr-hankey matlab reboost_gvt_disposal
        my_regex = re.compile(_TIGDUR_PATTERN)
        if my_regex.match(r):
            print "OK ", k[1], k[0], r
        else:
            print "-- ", k[1], k[0], r

    # # write soup as html to new file
    # soup.prettify()
    # with open(html_out, 'w') as f:
    #     f.write(soup.encode('UTF-8'))


def concat_two_columns_thru_inc52_partial():
    """parse out two-column entries and append thru inc52"""
    # html_files = [
    #     '/home/pims/Documents/ATL/header.html',
    #     '/home/pims/Documents/ATL/Inc48_as-flown_GUA.html',
    #     '/home/pims/Documents/ATL/Inc49_as-flown.html',
    #     '/home/pims/Documents/ATL/Inc50_as-flown.html',
    #     '/home/pims/Documents/ATL/Inc51_as-flown.html',
    #     '/home/pims/Documents/ATL/Inc52_as-flown_PARTIAL.html',
    #     ]

    # we concatentated already, so just one, grand html file
    #html_files = ['/home/pims/Documents/ATL/IncThru52_as-flown_PARTIAL.html']
    html_files = ['/home/pims/Documents/ATL/sample.html']

    html_out = '/home/pims/Documents/ATL/test.html'
    concatenate_two_column_htmls(html_files, html_out)


def fix_bigevent_rows(html_file, html_out):
    # get soup from first html file
    soup = get_soup(html_file)

    # clean up bigevent rows to get rid of stray u'\n'
    bigevt_rows = soup.findAll('tr', attrs={'class': 'bigevent'})
    for r in bigevt_rows:
        r.contents = [x for x in r.contents if x != u'\n']

    # # write soup as html to new file
    soup.prettify()
    with open(html_out, 'w') as f:
        f.write(soup.encode('UTF-8'))

if __name__ == "__main__":

    #concat_two_columns_thru_inc52_partial()

    ####################################################################################
    # Classify big event (two-column) rows
    # html_file = '/home/pims/Documents/ATL/sample.html'
    # html_out =  '/home/pims/Documents/ATL/sample_bigeventrows.html'
    # add_class_attr_to_event_rows(html_file, html_out)
    #
    # html_file = '/home/pims/Documents/ATL/IncThru52_as-flown_PARTIAL.html'
    # html_out =  '/home/pims/Documents/ATL/IncThru52_as-flown_PARTIAL_bigeventrows.html'
    # add_class_attr_to_event_rows(html_file, html_out)

    # ###################################################################################
    # Fix bigevent rows
    # html_file = '/home/pims/Documents/ATL/sample_bigeventrows.html'
    # html_out =  '/home/pims/Documents/ATL/sample_bigeventrows_clean.html'
    # fix_bigevent_rows(html_file, html_out)
    #
    # html_file = '/home/pims/Documents/ATL/IncThru52_as-flown_PARTIAL_bigeventrows.html'
    # html_out =  '/home/pims/Documents/ATL/IncThru52_as-flown_PARTIAL_bigeventrows_clean.html'
    # fix_bigevent_rows(html_file, html_out)

    ####################################################################################
    # Further classify reboost event tig|dur rows
    # html_file =  '/home/pims/Documents/ATL/sample_bigeventrows.html'
    # html_out =  '/home/pims/Documents/ATL/sample_bigeventrows_reboosts.html'
    # process_reboost_tigdur_info(html_file, html_out)
    #
    html_file = '/home/pims/Documents/ATL/IncThru52_as-flown_PARTIAL_bigeventrows.html'
    html_out =  '/home/pims/Documents/ATL/IncThru52_as-flown_PARTIAL_bigeventrows_reboosts.html'
    process_reboost_tigdur_info(html_file, html_out)

    # demo_soup('/home/pims/Documents/ATL/sample.html')