#!/usr/bin/env python

# print grid of all colors and brightnesses
# uses stdout.write to write chars with no newline nor spaces between them
# This should run more-or-less identically on Windows and Unix.
import sys
import datetime
import pandas as pd
import numpy as np

# Add parent dir to sys path, so the following 'import colorama' always finds
# the local source in preference to any installed version of colorama.
from colorama import init, Fore, Back, Style
init()

# Fore, Back and Style are convenience classes for the constant ANSI strings that set
#     the foreground, background and style. The don't have any magic of their own.
FORES = [ Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE ]
BACKS = [ Back.BLACK, Back.RED, Back.GREEN, Back.YELLOW, Back.BLUE, Back.MAGENTA, Back.CYAN, Back.WHITE ]
STYLES = [ Style.DIM, Style.NORMAL, Style.BRIGHT ]

NAMES = {
    Fore.BLACK: 'black', Fore.RED: 'red', Fore.GREEN: 'green', Fore.YELLOW: 'yellow', Fore.BLUE: 'blue', Fore.MAGENTA: 'magenta', Fore.CYAN: 'cyan', Fore.WHITE: 'white'
    , Fore.RESET: 'reset',
    Back.BLACK: 'black', Back.RED: 'red', Back.GREEN: 'green', Back.YELLOW: 'yellow', Back.BLUE: 'blue', Back.MAGENTA: 'magenta', Back.CYAN: 'cyan', Back.WHITE: 'white',
    Back.RESET: 'reset'
}

# dataframe formatters (for db query to dataframe)
_formatters = [
('A',   lambda x: Fore.RED + ' %s' % x + Fore.RESET),
('B',   lambda x: Fore.GREEN + ' %s' % x + Fore.RESET),
('C',   lambda x: Fore.YELLOW + ' %s' % x + Fore.RESET)
]
DF_FORMATTERS = dict(_formatters)
todays_date = datetime.datetime.now().date()
index = pd.date_range(todays_date-datetime.timedelta(10), periods=11, freq='D')
columns = ['A','B', 'C']
#df_ = pd.DataFrame(index=index, columns=columns)
#df_ = df_.fillna(0) # with 0s rather than NaNs
data = np.array([np.arange(11)]*3).T
df = pd.DataFrame(data, index=index, columns=columns)
lines = [df.to_string(index=False).split('\n')[0]]
[ lines.append(line) for line in df.to_string(formatters=DF_FORMATTERS, index=False).split('\n')[1:] ]
print '\n'.join(lines)

# show the color names
print ''
sys.stdout.write('        ')
for foreground in FORES:
    sys.stdout.write('%s%-7s' % (foreground, NAMES[foreground]))
print ''

# make a row for each background color
for background in BACKS:
    sys.stdout.write('%s%-7s%s %s' % (background, NAMES[background], Back.RESET, background))
    # make a column for each foreground color
    for foreground in FORES:
        sys.stdout.write(foreground)
        # show dim, normal bright
        for brightness in STYLES:
            sys.stdout.write('%sX ' % brightness)
        sys.stdout.write(Style.RESET_ALL + ' ' + background)
    print Style.RESET_ALL

print ''