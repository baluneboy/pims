#!/usr/bin/env python

import os
import re
import sys
import datetime
import pandas as pd
from StringIO import StringIO
from pims.patterns.samslogspats import _SAMSLOGS_DF, _SAMSLOGS_PS, _SAMSLIST_FILE
from pims.files.utils import filter_filenames

"""A utility for samslogs/samslist summary."""

__author__ = "Ken Hrovat"
__date__   = "$19-Dec-2011$"

# Ken
#
# ---------------------------------------------------------------------
# You don't need to look at the message files in the EE subdirectories.
#
# -------------------------
# What you want to look at:
# 
# 1. /var/log/messages
# 	a.	Open the latest one and scroll through looking that the rarpd messages occur once a minute and there are no jumps
# 	b.	Nothing out of the ordinary.  Ordinary stuff is /netbsd messages at a time when the ICU booted, or "tftpd[2174]: tftpd: read: Connection refused" at a time when an EE was booting"
# 	c.	Out of ordinary are mb_map full messages
# 	d.	I usually open a few more just to browse to see how things look
# 
# 2. /var/log/sams-ii/messages
# 	a.	Normal entries once a minute "Cumain v1.27[249]: ICU System clock adjusted by..."
# 	b.	Abnormal entries would be warning from a sams process.  Just kind of browse to see different message other than the clock adjusted and then determine what may need to be looked at with the team.
# 
# 3. Watchdoglog file
# 	a.	Scroll to bottom and see when the last time a watchdog timer event occurred.  Looking for anything recent that we need to be concerned about.
#
# ------------------------------------------
# In the dump from the listings, I look for:
# 
# 1. ICU: 5 main processes are running, and only one instance (RIC_manager, telemetry_downlinker, cu_main, icu_state_monitor, rarpd)
#     CU: 4 main processes are running with only one instance:
#           1. /usr/local/bin/RIC_manager -d
#           2. /usr/local/bin/telemetry_downlinker -d
#           3. /usr/local/bin/cu_state_monitor -d
#           4. /usr/sbin/rarpd -e -v
#     CU: 2 instances of "/usr/local/bin/cumain -d" running [Gilead said a new instance is spawned to handle command -- which command the samslist stuff?]:
# 
# 2. ICU: I check the PSID numbers for those 5.  If they are lower than 1000 it is likely they are the originals when first boot of ICU.  If higher, then I wonder if watchdog timer event happened and the process was restarted
#     CU: generic_client full accounting (how long, how many, one for each EE, one for each active sensor, etc.) 
# 
# 3. From the df -k command I look to make sure the hard drive is not getting completely full, nothing nearing 100%, except for /kern
# 
# I hope this helps
# Thanks
# Jen

MINPCT = 50 # FIXME make this more like 75 maybe?
MAXCPU = 10 # FIXME what value should be max CPU pct to trigger flag?

# dict for SAMS CU processes and count of each
sams_procs = {
    '/usr/local/bin/RIC_manager -d':          1,
    '/usr/local/bin/telemetry_downlinker -d': 1,
    '/usr/local/bin/cu_state_monitor -d':     1,
    '/usr/sbin/rarpd -e -v':                  1,
    '/usr/local/bin/cumain -d':               2,
}



def white_strip(text):
    try:
        return text.strip()
    except AttributeError:
        return text

def make_int(text):
    return int(text.strip('" '))

# give each cmd a grade
def grade_process(r):
    if r['C'] >= MAXCPU:
        return '#SAMSCPUHOG'
    if len(r['TIME']) > 8:
        return '#SAMSLONGRUN'
    if r['CMD'] in sams_procs.keys():
        return '#SAMSLISTOKAY'
    else:
        return 0

# give each Use% a grade
def grade_use_percent(p):
    if p < MINPCT:
        return '#SAMSLISTGOOD'
    elif p >= MINPCT and p < 75:
        return '#SAMSLISTOKAY'
    else:
        return '#SAMSLISTBAD'

def OBSOLETErewrite_input_file_with_line_ending_tags(input_file):
    out = StringIO()
    with open(input_file) as f:
        lines = f.read().splitlines()
    for i, line in enumerate(lines):
        
        m = re.match( re.compile(_SAMSLOGS_PS_GENCLI), line)
        if m:
            #print m.group('cmd')
            out.write( line + ' #GENCLI' + '\n')
            continue
        
        m = re.match( re.compile(_SAMSLOGS_DF), line)
        if m:
            #out.write( '\n' + '\t'.join( m.group(1,2,3,4,5,6) ) + '#DF')
            out.write( line + ' #DF' + '\n')        
            continue
        
        out.write( line + '\n')
    print out.getvalue()

# summarize samslist text file based on revisions to Jen's checklist
def summarize_samslist(input_file):
    """summarize samslist text file based on revisions to Jen's checklist"""
    #print 'Summary processing on %s' % input_file
    
    # FIXME do graceful check of output_file exist/rename/whatever
    output_file = input_file.replace('samslist', 'summary_samslist')
    out = StringIO()
    
    procs = StringIO()
    start_str = 'UID'
    found_start = False
    with open(input_file) as f:
        lines = f.read().splitlines()
    for i, line in enumerate(lines):
        if not line.strip():
            break # stop at first empty line
        if line.startswith(start_str):
            found_start = True
            columns = re.split('\s+', line)
            procs.write('\t'.join(columns))
        elif found_start:
            m = re.match( re.compile(_SAMSLOGS_PS), line)
            procs.write('\n%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (
                        m.group('uid'),
                        m.group('pid'),
                        m.group('ppid'),
                        m.group('c'),
                        m.group('stime'),
                        m.group('tty'),
                        m.group('time'),
                        m.group('cmd')
                        )
                    )
    procs.seek(0) # "rewind" to the beginning of the StringIO object
    df_procs = pd.read_csv(procs, sep='\t')
    
    # check count of processes that we know should be running
    proc_summary_str = ''
    for p, c in sams_procs.iteritems():
        dfss = df_procs[df_procs['CMD'].str.contains(p)]
        dfcount = len(dfss)
        if c != dfcount:
            proc_summary_str += 'NOTE: %s HAS COUNT OF %d, WHICH IS NOT THE DESIRED COUNT OF %d #SAMSLISTBAD\n' % (p, dfcount, c)
    
    formatters = [
        ('PID',    lambda x: '%d' % x),
        ('CMD',    lambda x: '%44s' % str(x))
        ]
    df_procs['Grade'] = df_procs.apply(lambda row: grade_process(row), axis=1)
    
    out.write('# PROCESS GRADES #\n')
    
    if len( df_procs[ df_procs['Grade'] == '#SAMSCPUHOG' ]) > 0:
        proc_summary_str += 'NOTE: CPU HOG(S) #SAMSLISTBAD\n'
    
    if len( df_procs[ df_procs['Grade'] == '#SAMSLONGRUN' ]) > 0:
        proc_summary_str += 'NOTE: LONG RUNNER(S) #SAMSLISTBAD\n'
    
    if proc_summary_str:
        out.write( proc_summary_str ) # keep trailing newline char
    else:
        # empty string (a good thing)
        out.write( 'NOTE: All %d processes matched their expected counts and no hogs or long runners. #SAMSLISTGOOD\n' % len(sams_procs) )

    # FIXME we use weak method to set Grade to zero to signify it's not graded (and won't show up in output)
    df_procs = df_procs[df_procs.Grade != 0]
    out.write( df_procs.to_string(formatters=dict(formatters)) + '\n' )
    
    # pick up line enum where we left off with procs (above) in terms of line numbers...
    mounts = StringIO()
    start_str = 'Filesystem'
    found_start = False
    for i, line in enumerate(lines[i+1:]):
        if not line.strip():
            break # stop at first empty line
        if line.startswith(start_str):
            found_start = True
            line = line.replace('Mounted on', 'MountedOn')
            columns = re.split('\s+', line)
            mounts.write('\t'.join(columns))
        elif found_start:
            m = re.match( re.compile(_SAMSLOGS_DF), line)
            mounts.write('\n%s\t%s\t%s\t%s\t%s\t%s' % (
                        m.group('filesys'),
                        m.group('kblocks'),
                        m.group('used'),
                        m.group('avail'),
                        m.group('usepct'),
                        m.group('mounted')
                        )
                    )
    mounts.seek(0) # "rewind" to the beginning of the StringIO object
    df_mounts = pd.read_csv(mounts, sep='\t',
                          converters = {'Filesystem' : white_strip,
                                        'MountedOn' : white_strip,
                                        'Use%' : make_int,
                                        'Available' : make_int,
                                        '1K-blocks' : make_int})
    df_mounts['Grade'] = df_mounts.apply(lambda row: grade_use_percent(row['Use%']), axis=1)

    out.write( '\n# DISK USAGE GRADES #\n' )
    if max(df_mounts['Use%']) <= MINPCT:
        out.write( 'NOTE: The max disk use percentage is at or below the threshold value of %d. #SAMSLISTGOOD\n' % MINPCT )    
    else:
        out.write( 'NOTE: The max disk use percentage is above the threshold value of %d. #SAMSLISTBAD\n' % MINPCT )    
    out.write( df_mounts.to_string() )

    # now write it all to output file
    with open(output_file, 'w') as fout:
        fout.write( out.getvalue() )
    
    return output_file

# get lastest samslist txt filename  
def get_latest_samslist_file(dirpath):
    # LIKE /misc/yoda/secure/2014_downlink/{2014-08-18}{15-18-06}_1408374968_samslogs2014230/usr/tgz/samslist2014230.txt
    filePattern = _SAMSLIST_FILE
    predicate = re.compile(dirpath + filePattern).match
    files = []
    for filename in filter_filenames(dirpath, predicate):
        files.append(filename)
    files.sort(key=lambda x: os.path.getmtime(x))
    try:
        return files[-1]
    except IndexError, e:
        print 'The full filename (including the path) for samslist under %s does not appear to match our pattern.' % dirpath
        print 'Sure this is the directory to be looking under?'
        raise e

if __name__ == '__main__':
    
    # process the file from cmd line arg
    if len(sys.argv) == 2:
        
        if os.path.isdir( sys.argv[1] ):
            # input arg is dirpath to look for latest samslist file under
            samslist_file = get_latest_samslist_file( sys.argv[1] )
            
        elif os.path.isfile( sys.argv[1] ):
            # just use file from input arg
            # EXAMPLE /home/pims/dev/programs/python/pims/sandbox/data/samslist2014230.txt
            samslist_file = sys.argv[1]

    elif len(sys.argv) == 1:
        
        dirpath = '/misc/yoda/secure/%d_downlink' % datetime.datetime.today().year
        samslist_file = get_latest_samslist_file(dirpath)

    else:
        
        print 'ABORT, no samslist text file could be identified from given input arg'
        raise SystemExit
    
    summary_file = summarize_samslist(samslist_file)
    print 'wrote summary file %s' % summary_file
