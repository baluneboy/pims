#!/usr/bin/python

import pyperclip
from dateutil import parser

#06/17/2014 	0000240104 	$3,546.18 	$1,310.37 	$1,000.00 	 
#06/03/2014 	0000220101 	$3,502.40 	$1,285.02 	$1,000.00 	 
#05/20/2014 	0000018186 	$3,502.40 	$1,285.02 	  	 
#05/06/2014 	0000180098 	$3,502.40 	$785.02 	$500.00 	$1,000.00
#

def strip_chars(s, bad_chars='$, '):
    for bc in bad_chars:
        s = s.replace(bc, '')
    if not s:
        s = '0'
    return s

# get clipboard contents (in chrono order)
lines = pyperclip.getcb().split('\n')
lines.reverse()

out = ''
for line in lines:
    columns = line.split(' \t')
    if len(columns) == 6:
        datestr, chknum, grosspay, netpay1, netpay2, netpay3 = columns
        out += '%s\t%s\t%.2f\t%.2f\t%.2f\t%.2f\n' % (parser.parse(datestr).date(), chknum,
                                                     float(strip_chars(grosspay)),
                                                     float(strip_chars(netpay1)),
                                                     float(strip_chars(netpay2)),
                                                     float(strip_chars(netpay3)),                                                     
                                                     )

out.rstrip('\n')
pyperclip.setcb(out)