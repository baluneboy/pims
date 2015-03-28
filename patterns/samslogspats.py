#!/usr/bin/env python

__all__ = [
    '_SAMSLOGS_PS',
    '_SAMSLOGS_PS_GENCLI',
    '_SAMSLOGS_DF',
    '_SAMSLIST_FILE',
    ]

###############################################################################################################################
#root     17074     1  0 Aug06 ?        01:34:49 /usr/local/bin/generic_client 121-f05 ee122-f03 9803
#root      6010  6009  0 15:00 ?        00:00:00 /bin/sh /usr/local/sams-ii/scripts/monday
#_SAMSLOGS_PS = '(?P<uid>\w+)\s+(?P<pid>\d+)\s+(?P<ppid>\d+)\s+(?P<c>\d+)\s+(?P<stime>.*)\s+(?P<tty>\?|\w+)\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<cmd>.*)'
_SAMSLOGS_PS = '(?P<uid>\w+)\s+(?P<pid>\d+)\s+(?P<ppid>\d+)\s+(?P<c>\d+)\s+(?P<stime>.*)\s+(?P<tty>\?|\w+)\s+(?P<time>(?P<dd>\d+-){0,1}\d{2}:\d{2}:\d{2})\s+(?P<cmd>.*)'

###############################################################################################################################
#/usr/local/bin/generic_client tshes-06-accel tshes-06 9760
#/usr/local/bin/generic_client tshes-06-state tshes-06 9761 70
#/usr/local/bin/generic_client 122-f03 ee122-f03 9805
#generic_client 121-f05 ee122-f03 9803
_SAMSLOGS_PS_GENCLI = '(?P<uid>\w+)\s+(?P<pid>\d+)\s+(?P<ppid>\d+)\s+(?P<c>\d+)\s+(?P<stime>.*)\s+(?P<tty>\?|\w+)\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<cmd>.*generic_client.*)'

###############################################################################################################################
#/dev/sda1      151950716 56330484  88012120  40% /
#udev             1978944        4   1978940   1% /dev
_SAMSLOGS_DF = '(?P<filesys>.+)\s+(?P<kblocks>\d+)\s+(?P<used>\d+)\s+(?P<avail>\d+)\s+(?P<usepct>\d+)\%\s+(?P<mounted>.+)'

###############################################################################################################################
#/misc/yoda/secure/2014_downlink/{2014-08-18}{15-18-06}_1408374968_samslogs2014230/usr/tgz/samslist2014230.txt
_SAMSLIST_FILE = '.*/\{\d{4}-\d{2}-\d{2}\}\{\d{2}-\d{2}-\d{2}\}_\d+_samslogs\d+/.*/samslist.*\.txt'

#~~~~~~~~~~~~~~~~~~~~   #~~~~~~~~~~~~~~~~~~~~   #~~~~~~~~~~~~~~~~~~~~   #~~~~~~~~~~~~~~~~~~~~   #~~~~~~~~~~~~~~~~~~~~

def match_pattern_demo(fname, pat):
    """Check for match."""
    import re
    return re.match(pat, fname)

if __name__ == "__main__":

    m = match_pattern_demo('/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f05006/2013_01_02_00_08_27.913-2013_01_02_01_25_23.117.121f05006.header', _PADHEADERFILES_PATTERN)
    if m:
        print m.group('sensor'), m.group('start')
    else:
        print 'no match'
        
    m = match_pattern_demo('/misc/yoda/www/plots/batch/year2013/month10/day01/2013_10_01_08_00_00.000_121f03_spgs_roadmaps500.pdf', _BATCHROADMAPS_PATTERN)
    if m:
        print m.group('sensor'), m.group('start')
    else:
        print 'no match'