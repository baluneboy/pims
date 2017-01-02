#!/usr/bin/env python

import os
import re
import sys
import numpy as np
import datetime
from dateutil import parser
from bs4 import BeautifulSoup, Tag

from pims.files.utils import filter_filenames

SENSOR_MAP = {
    '121f02': ('SE-F02', 'COL', 'EDR Rack'),
    '121f03': ('SE-F03', 'LAB', 'EXPRESS Rack 2'),
    '121f05': ('SE-F05', 'JEM', 'EXPRESS Rack 4'),
    '121f08': ('SE-F08', 'COL', 'EPM Rack'),
    }

FREQ_MAP = {
    '0p01to10': 'below 10 Hz',
    '0p01to200': 'below 200 Hz',
}

FILE_PATTERN = r'(?P<basepath>/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_MARES_SARCOLAB-3_2016-11-28/rmstracker_2bands)/(?P<sensor>%s)/rmstracker_comprehensive_stats_for_mares_sarcolab3_2bands_.*(?P=sensor)_(?P<ax>%s)_sams(?P=sensor)RMS(?P<freq>%s)_(?P<date>%s)\.pdf\Z'


def file_info(file_name, file_pattern):
    """return parsed file info

    file_name should be a string with full path to file
    
    """
    match = re.compile(file_pattern).match(file_name)
    if match:
        basepath = match.group('basepath')
        sensor = match.group('sensor')
        ax = match.group('ax')
        freq = match.group('freq')
        date = match.group('date')
        return basepath, sensor, ax, freq, date
    else:
        return None       # there is no file extension to file_name


def get_pdfs_list(sensor, ax, freq, date, dirpath):
    fullfile_pattern = FILE_PATTERN % (sensor, ax, freq, date)
    return list(filter_filenames(dirpath, re.compile(fullfile_pattern).match))

#<br>SE-F02, X-axis: <a href="BELOWTEN">below 10 Hz</a> and <a href="BELOW200">below 200 Hz</a><br>

def mares_sarcolab3_list():
    dirpath = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_MARES_SARCOLAB-3_2016-11-28/rmstracker_2bands'
    for date in ['28-Nov-2016', '29-Nov-2016', '30-Nov-2016', '01-Dec-2016']:
            print '\nWeb page for %s' % date
            for sensor in ['121f02', '121f03', '121f05', '121f08']:
                abbrev, lab, rack = SENSOR_MAP[sensor]
                print '\n<br><span style="font-weight: bold;">SAMS %s in %s (%s)</span>\n<ul>' % (abbrev, lab, rack)
                for ax in ['s', 'x', 'y', 'z']:
                    print '<li>%s-axis:' % ax.upper(),
                    s = ''
                    for freq in ['0p01to10', '0p01to200']:
                        fpat = FILE_PATTERN % (sensor, ax, freq, date)
                        pdfs_list = get_pdfs_list(sensor, ax, freq, date, dirpath)
                        if len(pdfs_list) == 1:
                            fname = pdfs_list[0]
                            basepath, sensor, ax, freq, date = file_info(fname, fpat)
                            s += '<a href="%s">%s</a> and ' % (fname, FREQ_MAP[freq])
                        else:
                            s += 'BADHANDLER'
                    print '%s</li>' % s[:-5]
                print '</ul>'
                


mares_sarcolab3_list()
raise SystemExit


def pretty_soup(html_file):

    with open(html_file, 'r') as infile:
        html_src = infile.read()
    soup = BeautifulSoup(html_src, "lxml")

    with open('/tmp/trash9.html', 'w') as f:
        f.write(soup.prettify().encode('UTF-8'))


pretty_soup('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_MARES_SARCOLAB-3_2016-11-28/YYYYdayDOY.html');
raise SystemExit


if __name__ == "__main__":
    old_htm_file = sys.argv[1]
    new_htm_file = sys.argv[2]
    print 'Scraping %s,' % old_htm_file,
    scrape_into_dataframe(old_htm_file, new_htm_file=new_htm_file)
    #scrape_into_dataframe(old_htm_file)
    print 'done.',
