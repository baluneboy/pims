#!/usr/bin/env python

import os
import sys
import csv
import datetime
import numpy as np
import pandas as pd
from pims.pad.loose_pad_intervalset import get_strata_gaps
from pims.utils.pimsdateutil import datetime_to_longtimestr, days_ago_to_date


# input parameters
defaults = {
'days_ago':      '2',                       # integer number of days ago to process (n days ago)
'sensor':        '121f04',                  # sensor of interest
'maxgapsec':     '59',                      # consider only gaps longer than this integer max gap (sec)
'pad_path':      '/misc/yoda/pub/pad',      # base path of interest for source of PAD files
'csv_path':      '/misc/yoda/www/plots/user/sams/gaps/pad', # base path for output csv file
'destination':   'yoda',                    # where to write (or show); yoda for web (CSV and HTML) or any other string for stdout
}
parameters = defaults.copy()


def get_html_header(sensor):
    header = """
    <html>
    <body BGCOLOR=#FFFFFF TEXT=#000000 LINK=#0000FF VLINK=#800040 ALINK=#800040>
    <title>SAMS PAD Gaps</title>
    <link rel="stylesheet" type="text/css" href="recent_gaps.css" media="screen"/>
    <h2>SAMS _SENSOR_, Ten Recent Gaps (> 59sec)</h2>
    """
    return header.replace('_SENSOR_', sensor)


def get_html_footer(sensor):
    timestr = datetime.datetime.now().strftime('%Y-%m-%d/%H:%M:%S')
    footer = """
    <br>
    For list dating back to 2016-11-16, see <a href="http://pims.grc.nasa.gov/plots/user/sams/gaps/pad/_SENSOR_.csv">this CSV file.</a><br>
    <br>
    <b>This page was updated at GMT _TIMESTR_<b>
    <br>
    </body>
    </html>
    """
    footer = footer.replace("_SENSOR_", sensor)
    return footer.replace("_TIMESTR_", timestr)


# convert input parameter to integer
def str2int(s):
    is_ok = False
    try:
        parameters[s] = int(parameters[s])
    except Exception, e:
        print 'could not convert input for %s: %s' % (s, e.message)
    else:
        is_ok = True # try worked okay, so return True
    finally:
        # no matter what happened, do [clean-up?] with finally clause
        return is_ok
    
    
# check for reasonableness of parameters
def parameters_ok():
    """check for reasonableness of parameters"""
    
    # verify paths exist
    if not os.path.exists(parameters['pad_path']):
        print 'the path (%s) does not exist' % parameters['pad_path']
        return False
    parameters['csv_file'] = os.path.join(parameters['csv_path'], parameters['sensor'] + '.csv')
    if not os.path.exists(parameters['csv_file']):
        print 'the csv file (%s) does not exist' % parameters['csv_file']
        return False
    
    # convert these inputs to integer values
    for param in [ 'days_ago', 'maxgapsec' ]:
        is_ok = str2int(param)
        if not is_ok:
            return False

    return True # all OK; otherwise, we would've returned False above


# print helpful text how to run the program
def print_usage():
    """print helpful text how to run the program"""
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])


# show strata gaps
def show_strata_gaps():
    """show strata gaps"""
    days_ago =  parameters['days_ago']
    sensor =    parameters['sensor']
    maxgapsec = parameters['maxgapsec']
    pad_path =   parameters['pad_path']
    gaps = get_strata_gaps(days_ago=days_ago, sensor=sensor, maxgapsec=maxgapsec, basedir=pad_path)
    doi = days_ago_to_date(days_ago)
    if gaps:
        for gap in gaps:
            t1, t2 = gap.lower_bound, gap.upper_bound
            dur_min = ( t2 - t1 ).total_seconds() / 60.0
            print '%s %s %7.2f %s to %s' % (doi, sensor, dur_min,
                datetime_to_longtimestr(t1).replace(',', ' '),
                datetime_to_longtimestr(t2).replace(',', ' '))
    else:
            print '%s %s no gaps' % (doi, sensor)


# write strata gaps to csv
def write_strata_gaps():
    """write strata gaps to csv"""
    days_ago =  parameters['days_ago']
    sensor =    parameters['sensor']
    maxgapsec = parameters['maxgapsec']
    pad_path =   parameters['pad_path']
    csv_file = parameters['csv_file']
    gaps = get_strata_gaps(days_ago=days_ago, sensor=sensor, maxgapsec=maxgapsec, basedir=pad_path)
    doi = days_ago_to_date(days_ago)
    with open(csv_file, 'ab') as outfile:
        writer = csv.writer(outfile, lineterminator='\n')
        if gaps:
            for gap in gaps:
                t1, t2 = gap.lower_bound, gap.upper_bound
                dur_min = ( t2 - t1 ).total_seconds() / 60.0          
                writer.writerow( [doi, sensor, "%.2f" % dur_min,
                    datetime_to_longtimestr(t1).replace(',', ' '),
                    datetime_to_longtimestr(t2).replace(',', ' ')])
        else:
                writer.writerow( [doi, sensor, '0.00', '', ''])
    return csv_file, sensor


def write_strata_gaps_html(csv_file, sensor):
    html_file = csv_file.replace('.csv', '.html')
    df = pd.read_csv(csv_file)
    
    # only consider gaps greater than zero minutes long (duh)
    df = df[ df['Gap(m)'] > 0.0 ]
   
    ## replace NaN's with a space
    #df = df.replace(np.nan, ' ', regex=True)
    
    # reverse chrono sort
    df = df.sort_values(by=['StartGap'], ascending=False)
    
    # for web page, just keep most recent 10 entries
    df = df.head(n=10)
    
    # convert df to html and save
    html_table = df.to_html(index=False)
    html_header = get_html_header(sensor)
    html_footer = get_html_footer(sensor)
    with open(html_file, 'wb') as f:
        f.write(html_header)
        f.write(html_table)
        f.write(html_footer)


#for sensor in ['121f03', '121f04']:
#    csv_file = '/tmp/' + sensor + '.csv'
#    write_strata_gaps_html(csv_file, sensor)
#raise SystemExit


# get inputs, verify ok, then run main routine
def main(argv):
    """get inputs, verify ok, then run main routine"""
    
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

            if parameters['destination'] == 'yoda':
                # here is the main routine to check for and show gaps
                csv_file, sensor = write_strata_gaps()
                write_strata_gaps_html(csv_file, sensor)
            else:
                show_strata_gaps()

            return 0

    print_usage()
    
    return 22


# run main with cmd line args and return exit code
if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))
