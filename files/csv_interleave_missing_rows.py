#!/usr/bin/env python3

"""Fill to even out unevenly-spaced rows in a spreadsheet (ascii/text/csv) file.

The output file has uniformly-spaced rows (no missing time slots). Basically, we want to insert missing
time slots based on times in 't1' column, and when we fill we don't care what goes in the remaining
columns besides newly-inserted time.

NOTE: we assume the input file has time column of interest already sorted! <<< FIXME
"""

import sys
import pandas as pd


def get_freq(f):
    """Return string for frequency of time-fill, e.g. to use with asfreq method.

        Input arguments:
        f -- a string, integer or pandas.core.series.Series to represent frequency value
        """
    if type(f) is int:
        freq_minutes = f
    elif isinstance(f, str):
        return f
    elif isinstance(f, pd.core.series.Series):
        freq_minutes = f.diff().median().total_seconds() / 60.0
    else:
        raise Exception('unhandled type')
    return '%dmin' % freq_minutes


def write_time_filled_csv(csv_infile, tcol='t1', freq=None):
    """Write time-filled CSV file.

        Reads input csv file into dataframe, fills missing times, then writes results.

        Input arguments:
        csv_infile -- a string for path/name of input CSV file to consider
        tcol -- a string for column name (heading/label) to use for time-slot fill criteria
        freq -- a string, integer or None specifies time interval to fill with (default is None)
                when freq is None, use median delta detected from tcol time steps; otherwise,
                freqeuncy/interval is in minutes (like '10min' or 20 for '20min')
        """
    # get output filename
    csv_outfile = csv_infile.replace('.csv', '_filled.csv')

    # read raw into a dataframe
    df = pd.read_csv(csv_infile)

    # convert first column entries to time objects
    df[tcol] = pd.to_datetime(df[tcol], infer_datetime_format=True)

    # fill-in missing time slots (don't care about columns to right of time --> empty)
    if freq is None:
        freq_minutes = get_freq(df[tcol])
    else:
        freq_minutes = get_freq(freq)
    df = df.set_index(tcol).asfreq(freq_minutes).fillna(value=pd.NA).reset_index()

    # finally, write output csv file
    df.to_csv(csv_outfile, index=False)


if __name__ == '__main__':
    csv_file = sys.argv[1]
    write_time_filled_csv(csv_file)  # typical call

    # EXAMPLES OF OTHER INPUT PROFILES/CALLS
    # write_time_filled_csv(csv_file, tcol='t1', freq='10min')
    # write_time_filled_csv(csv_file, tcol='t1', freq=20)
    # write_time_filled_csv(csv_file, tcol='t1', freq=None)
    # write_time_filled_csv(csv_file, tcol='t2')  # NOTE: this moves t2 column to first column
