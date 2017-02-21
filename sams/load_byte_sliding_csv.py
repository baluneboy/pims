#!/usr/bin/env python

import sys
import pandas as pd


def main(spreadsheet_file='/home/pims/temp/ee_data_bigun.csv'):
    """Load info from csv-delimited spreadsheet_file into pandas dataframe."""

    # FIXME error checks on input file (e.g. exists, format, etc.)
    
    # read spreadsheet file into dataframe
    df = pd.read_table(spreadsheet_file)
    
    print df
    
    # see /home/pims/dev/programs/python/pims/gutwrench/load_spreadsheet.py
    
    return 0  # exit code zero for success

if __name__ == "__main__":
    sys.exit( main() )
