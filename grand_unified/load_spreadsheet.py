#!/usr/bin/env python

"""Load ISS Motion Control System (MCS) Flight Info.

    Given properly-formatted, tab-delimited text filename as input,
    load the info there into pandas dataframe object.

"""

import sys
import pandas as pd
from pims.grand_unified.actions import ACTIONS

def general_fun(cat, label, start_gmt, stop_gmt, extras):
    print '-' * 24, ' for MATLAB fun'
    print 'cat:', cat
    print 'label:', label
    print 'start:', start_gmt
    print 'stop:', stop_gmt
    print '%02d EXTRAS BELOW:' % len(extras)
    for key, val in extras.iteritems():
        print '--> %s = %s' % (key, val)
        
# Load info from tab-delimited spreadsheet_file into pandas dataframe.
def main(spreadsheet_file='/home/pims/Documents/grand_unified.tab'):
    """Load info from tab-delimited spreadsheet_file into pandas dataframe."""

    # FIXME error checks on input file (e.g. exists, format, etc.)
    
    # read spreadsheet file into dataframe
    df = pd.read_table(spreadsheet_file)
    
    # format StartGMT and StopGMT as datetime objects
    df['StartGMT'] = pd.to_datetime(df['StartGMT'])
    df['StopGMT'] = pd.to_datetime(df['StopGMT'])
    
    # FIXME: gracefully handle [ignore?] any GMTs that might now be "NaT"
    
    # iterate over spreadsheet rows
    for row_tuple in df.itertuples():
        row = row_tuple._asdict()
        
        print '=' * 33, ' SHOWING FOR SCRIPT OUTPUT'
        for key, val in row.iteritems():
            print key + ":", val
        
        kwargs = dict()
        extras = row['Extra'].split(',')
        for item in extras:
            pair = item.split('=')
            if (2 != len(pair)):
                print 'bad parameter dealing with:', pair
                break
            else:
                kwargs[pair[0]] = pair[1]
        general_fun(row['Category'], row['Label'], row['StartGMT'], row['StopGMT'], kwargs)
        
    return 0  # exit code zero for success

if __name__ == "__main__":
    sys.exit( main() )
