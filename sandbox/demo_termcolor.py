#!/usr/bin/env python

import sys
from termcolor import colored, cprint

text = colored('red reverse blink', 'red', attrs=['reverse', 'blink'])
print(text)
cprint('green on_red', 'green', 'on_red')

print_red_on_cyan = lambda x: cprint(x, 'red', 'on_cyan')
print_red_on_cyan('red on_cyan')
print_red_on_cyan('red on_cyan again')

for i in range(10):
    cprint(str(i) + ' magenta', 'magenta', end=' ')

cprint("red bold", 'red', attrs=['bold'], file=sys.stderr)
print ''
colors = [
'grey',
'red',
'green',
'yellow',
'blue',
'magenta',
'cyan',
'white'
]
for c in colors:
    print colored(c, c)