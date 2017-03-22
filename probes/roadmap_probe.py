#!/usr/bin/env python

"""check for gaps and intervals among roadmap PDF files"""

import os
import re
import sys
import json
from json2html import json2html
import datetime
import subprocess
import pandas as pd
from dateutil import parser, relativedelta

from pims.utils.gists import tree, add_tree_value
from pims.lib.niceresult import NiceResult
from pims.files.utils import filter_filenames
from pims.utils.pimsdateutil import datetime_to_ymd_path, unix2dtm
from pims.files.filter_pipeline import FileFilterPipeline, MatchSensorAxRoadmap, BigFile
from pims.patterns.probepats import _ROADMAP_PDF_BLANKS_PATTERN, _OSSBTMF_ROADMAP_PDF_FILENAME_PATTERN
from pims.probes.tree_example import ExampleTreeBrowser
from pims.pad.daily_set import _TWODAYSAGO


# input parameters
defaults = {
'dir_name':     '/misc/yoda/www/plots/batch',               # base path
'first_day':    _TWODAYSAGO,                                # first day to process
'last_day':     _TWODAYSAGO,                                # last day to process
'basename_blanks_pattern': _ROADMAP_PDF_BLANKS_PATTERN,     # regular expression pattern to match
'sensors':      '121f02,121f03,121f04,121f05,121f08',       # comma-sep list of sensors
'axes':         's,x,y,z',                                  # comma-sep list of axis chars
'order_by_day': 'True',                                     # order_by_day; True for day/sensor; else, sensor/day
}
parameters = defaults.copy()


# HTML header
_HEADER = """
<HTML>
<BODY BGCOLOR=#FFFFFF TEXT=#000000 LINK=#0000FF VLINK=#800040 ALINK=#800040>
<TITLE>Roadmap Probe</TITLE>
<CENTER>
<B>Last refreshed GMT %s<B><BR>
<link rel="stylesheet" type="text/css" href="roadmap_probe.css" media="screen"/>
""" % datetime.datetime.now().strftime('%d-%b-%Y, %j/%H:%M:%S ')


# HTML footer
_FOOTER = """<BR>
</CENTER>
</BODY>
</HTML>
"""


def get_day_roadmap_pdf_files(base_dir, day, basename_pat):
    """return list of all roadmap PDFs for a given day"""
    day_dir = datetime_to_ymd_path(day, base_dir=base_dir)
    pattern = '.*' + basename_pat
    return list(filter_filenames(day_dir, re.compile(pattern).match))


def get_day_sensor_axis_roadmap_pdf_files(day_roadmap_pdf_files, sensor, axis):
    """return list of roadmap spg files for given day, sensor and axis"""
    # FIXME empirically determine good threshold value for min_bytes arg in BigFile
    if sensor == 'ossbtmf':
        ffp = FileFilterPipeline(BigFile(min_bytes=20))        
    else:
        ffp = FileFilterPipeline(MatchSensorAxRoadmap(sensor, axis), BigFile(min_bytes=20))
    return list(ffp(day_roadmap_pdf_files))


def get_loop_params(parameters):
    dir_name = parameters['dir_name']
    start_date = parameters['first_day']
    end_date = parameters['last_day']
    sensors = parameters['sensors']
    if sensors == ['ossbtmf']:
        axes = ['3']
        basename_pat = _OSSBTMF_ROADMAP_PDF_FILENAME_PATTERN
    else:
        axes = parameters['axes']
        basename_pat = _ROADMAP_PDF_BLANKS_PATTERN.replace('SENSOR', '.*').replace('PLOT', '.*').replace('AXIS', '\w')
    date_range = pd.date_range(start=start_date, end=end_date)
    return dir_name, start_date, end_date, sensors, axes, basename_pat, date_range


def get_roadmap_sensor_tree(parameters):
    dir_name, start_date, end_date, sensors, axes, basename_pat, date_range = get_loop_params(parameters)
    sensor_tree = tree()    
    for day in date_range:
        day_pdf_files = get_day_roadmap_pdf_files(dir_name, day, basename_pat)
        for sensor in sensors:
            for axis in axes:
                pdf_files = get_day_sensor_axis_roadmap_pdf_files(day_pdf_files, sensor, axis)
                sensor_tree[sensor][day.strftime('%Y-%m-%d')][axis] = [ os.path.basename(f) + ' ' + unix2dtm(os.path.getmtime(f)).strftime('%H:%M:%S') for f in pdf_files ]
    return sensor_tree


def get_roadmap_day_tree(parameters):
    dir_name, start_date, end_date, sensors, axes, basename_pat, date_range = get_loop_params(parameters)    
    day_tree = tree()    
    for sensor in sensors:
        for day in date_range:
            day_pdf_files = get_day_roadmap_pdf_files(dir_name, day, basename_pat)
            for axis in axes:
                pdf_files = get_day_sensor_axis_roadmap_pdf_files(day_pdf_files, sensor, axis)
                day_tree[day.strftime('%Y-%m-%d')][sensor][axis] = [ os.path.basename(f) + ' ' + unix2dtm(os.path.getmtime(f)).strftime('%H:%M:%S') for f in pdf_files ]
    return day_tree


def get_roadmap_tree(parameters):
    if parameters['order_by_day']:
        roadmap_tree = get_roadmap_day_tree(parameters)
    else:
        roadmap_tree = get_roadmap_sensor_tree(parameters)
    return roadmap_tree


def parameters_ok():
    """check for reasonableness of parameters"""

    # verify base path
    if not os.path.exists(parameters['dir_name']):
        print 'base path (%s) does not exist' % parameters['dir_name']
        return False
    
    # convert start day to date object
    try:
        parameters['first_day'] = parser.parse( parameters['first_day'] ).date()
    except Exception, e:
        print 'could not get first_day input as date object: %s' % e.message
        return False
    
    # convert stop day to date object
    try:
        parameters['last_day'] = parser.parse( parameters['last_day'] ).date()
    except Exception, e:
        print 'could not get last_day input as date object: %s' % e.message
        return False

    # verify pattern is good regular expression
    try:
        re.compile(parameters['basename_blanks_pattern'])
    except Exception, e:
        print 'basename_blanks_pattern "%s" would not compile as valid regular expression' % parameters['basename_blanks_pattern']
    
    # get list of sensors
    try:
        parameters['sensors'] = list(parameters['sensors'].split(','))
    except Exception, e:
        print 'could not get comma-sep list of sensors: %s' % e.message
        return False    
    
    # get list of axis chars
    try:
        parameters['axes'] = list(parameters['axes'].split(','))
        is_one_char = [ len(i)==1 for i in parameters['axes'] ]
        assert(all(is_one_char))
    except Exception, e:
        print 'could not get comma-sep list of axis chars: %s' % e.message,
        print parameters['axes']
        return False

    # get hierarchy order
    try:
        parameters['order_by_day'] = eval(parameters['order_by_day'])
    except Exception, e:
        print 'could not cast "order_by_day" parameter as boolean: %s' % e.message,
        return False
    
    # be sure user did not mistype or include a parameter we are not expecting
    s1, s2 = set(parameters.keys()), set(defaults.keys())
    if s1 != s2:
        extra = list(s1-s2)
        missing = list(s2-s1)
        if extra:   print 'extra   parameters -->', extra
        if missing: print 'missing parameters -->', missing
        return False    

    return True # all OK; otherwise, return False somewhere above


def print_usage():
    """print helpful text how to run the program"""
    #FIXME with git keyword sub via following:
    # http://stackoverflow.com/questions/11534655/git-keyword-substitution-like-those-in-subversion
    #print version << BETTER GO AT THIS???
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])


def write_html(json_str):
    html_str = json2html.convert(json_str)
    with open("/misc/yoda/www/plots/user/pims/roadmap_probe.html", "w") as html_file:
        html_file.write( _HEADER + html_str + _FOOTER )         

    
def main(argv):
    """describe main routine here"""

    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parameters_ok():
            nr = NiceResult(get_roadmap_tree, parameters)
            nr.do_work()
            my_tree = nr.get_result()
            if my_tree:
                json_str = json.dumps(my_tree, sort_keys=True, indent=3, separators=(',', ':'))
                print json_str
                write_html(json_str)
                #exampleTreeBrowser(dict(sensor_tree)).main()
                return 0 # zero for unix success
            else:
                return -1

    print_usage()


if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))
