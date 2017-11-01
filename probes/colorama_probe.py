#!/usr/bin/env python

import re
import sys
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

if __name__ == "__main__":

    # Note that sys.stdin is a file object. All the same functions that
    # can be applied to a file object can be applied to sys.stdin.
    for line in sys.stdin.readlines():
#            if line.endswith('n.py\n'):
            if re.match('.*\d{4}-\d{2}-\d{2}.*', line):
                #sys.stdout.write('%s%-7s' % (Fore.CYAN, line))
                #sys.stdout.write('%s%-7s %s' % (Back.RED, line, Back.RESET))
                print Style.BRIGHT + Fore.YELLOW + Back.RED + line + Back.RESET + Fore.RESET + Style.RESET_ALL
            else:
                sys.stdout.write(line)
                
