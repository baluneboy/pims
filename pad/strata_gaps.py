#!/usr/bin/env python

import os
import sys
import csv
from pims.pad.loose_pad_intervalset import get_strata_gaps
from pims.utils.pimsdateutil import datetime_to_longtimestr, days_ago_to_date


# input parameters
defaults = {
'days_ago':      '2',                       # integer number of days ago to process (n days ago)
'sensor':        '121f04',                  # sensor of interest
'maxgapsec':     '59',                      # consider only gaps longer than this integer max gap (sec)
'pad_path':      '/misc/yoda/pub/pad',      # base path of interest for source of PAD files
'csv_path':      '/misc/yoda/www/plots/user/sams/gaps/pad', # base path for output csv file
'write_csv':     'True',                    # True to write CSV; False to just show on stdout
}
parameters = defaults.copy()


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

    # write or just show results
    try:
        parameters['write_csv'] = eval(parameters['write_csv'])
        assert( isinstance(parameters['write_csv'], bool))
    except Exception, err:
        print 'cound not handle write_csv parameter, was expecting it to eval to True or False'
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
    gaps = get_strata_gaps(days_ago=days_ago, sensor=sensor, maxgapsec=maxgapsec, basedir=pad_path)
    doi = days_ago_to_date(days_ago)
    with open('/tmp/trash.csv', 'ab') as outfile:
        writer = csv.writer(outfile, lineterminator='\n')
        if gaps:
            for gap in gaps:
                t1, t2 = gap.lower_bound, gap.upper_bound
                dur_min = ( t2 - t1 ).total_seconds() / 60.0          
                writer.writerow( [doi, sensor, "%.2f" % dur_min,
                    datetime_to_longtimestr(t1).replace(',', ' '),
                    datetime_to_longtimestr(t2).replace(',', ' ')])
        else:
                writer.writerow( [doi, sensor, 'no gaps', '', ''])
    
    
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
            # here is the main routine to check for and show gaps
            if parameters['write_csv']:
                write_strata_gaps()
            else:
                show_strata_gaps()
            return 0

    print_usage()
    
    return 22


# run main with cmd line args and return exit code
if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))
