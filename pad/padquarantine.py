#!/usr/bin/env python

import os
import re
import sys
import datetime
import operator
import shutil
import subprocess
import numpy as np
from scipy import stats
from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop
from pims.files.utils import listdir_filename_pattern
from pims.files.filter_pipeline import FileFilterPipeline, DateRangePadFile


# get list of (file, rate) tuples sorted by rate
def file_rate_tuples(r):
    """get list of (file, rate) tuples sorted by rate"""
    regex = re.compile('(.*):.*SampleRate\>(.*)\<.*')
    my_list = [ (m.group(1), float(m.group(2))) for i in r for m in [regex.search(i)] if m ]
    my_list.sort( key=operator.itemgetter(1) )
    return my_list

# grep to get file and sample rate in list
def grep_sample_rate(subdir):
    """grep to get file and sample rate in list"""
    # grep SampleRate /misc/yoda/pub/pad/year2014/month04/day12/sams2_accel_121f02/*.header
    if not os.path.exists(subdir):
        raise OSError('%s does not exist' % subdir)
    cmd = 'grep SampleRate ' + os.path.join(subdir,'*.header')
    process_header_files = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = process_header_files.communicate()
    splitout = out.split('\n')[:-1] # split on newlines & get rid of very last trailing newline
    return splitout

# return True if bad time string; otherwise, False
def bad_timestr(fullfilestr):
    """return True if bad time string; otherwise, False"""
    d1, d2 = pad_fullfilestr_to_start_stop(fullfilestr)
    if not d1:
        print 'bad start part in %s' % fullfilestr
        return True
    if not d2:
        print 'bad stop part in %s' % fullfilestr
        return True
    return False

# return 2d numpy array read from datafile input
def array_fromfile(datafile, columns=4, out_dtype=np.float32):
    """return 2d numpy array read from datafile input"""
    with open(datafile, "rb") as f: 
        a = np.fromfile(f, dtype=np.float32) # accel file: 32-bit float "singles"
    b = np.reshape(a, (-1, columns))
    if b.dtype == out_dtype:
        return b
    return b.astype(out_dtype)

# max abs all data
def max_abs(a):
    """max abs all data"""
    return np.max( np.abs(a[:,1:]) )

# quarantine data and header file
def quarantine(datafiles):
    """quarantine data and header files"""
    for datafile in datafiles:
        dname = os.path.dirname(datafile)
        #bname = os.path.basename(datafile)
        hdrfile = datafile + '.header'
        qdir = os.path.join(dname, 'quarantined')
        if not os.path.isdir(qdir):
            os.mkdir(qdir)
        shutil.move(datafile, qdir)
        shutil.move(hdrfile, qdir)
        print 'quarantined %s' % datafile
        print 'quarantined %s' % hdrfile

# check data file > 0.5 g
def is_over_half_g(datafile):
    """check data file > 0.5 g"""
    a = array_fromfile(datafile, columns=4, out_dtype=np.float32)
    return max_abs(a) > 0.5

def is_too_small(datafile, max_bytes):
    """check data file <= than max_bytes"""
    b = os.path.getsize(datafile)
    return b <= max_bytes    
    
# process single subdir to see if/what needs to be quarantined, return count of quarantined
def process_header_files(subdir):
    """process single subdir to see if/what needs to be quarantined, return count of quarantined"""
    # get list of (file, rate) tuples sorted by rate
    r = grep_sample_rate(subdir)
    my_list = file_rate_tuples(r)
    #print my_list

    # determine mode (i.e. "most common") for sample rate    
    rates = [ t[1] for t in my_list ]
    mode = stats.mode(rates)[0][0]
    #print mode
    
    # get list to be quarantined (sample rate not equal to mode)
    quarantined_list_fs = [ t for t in my_list if t[1] != mode ]
    
    # get another list to be quarantined (like more than 59 seconds in timestr)
    quarantined_list_bad_timestr = [ t for t in my_list if bad_timestr(t[0]) ]
    
    # concat 2 lists
    quarantined_list = quarantined_list_fs + quarantined_list_bad_timestr
    #print 'length of quarantined list is %d for %s' % (len(quarantined_list), subdir)
        
    # if needed, then move to quarantined
    qdir = os.path.join(subdir, 'quarantined')
    if quarantined_list and not os.path.isdir(qdir):
        os.mkdir( qdir )
    for f, fs in quarantined_list:
        #print 'move %s to %s' % (f, qdir)
        #print 'move %s to %s' % (f.rstrip('.header'), qdir)
        shutil.move(f, qdir)                    # move header file
        shutil.move(f.rstrip('.header'), qdir)  # move data file
    
    return len(quarantined_list)

# process single subdir to see if/what needs to be amplitude quarantined, return count of quarantined
def process_amplitudes(subdir):
    """process single subdir to see if/what needs to be amplitude quarantined, return count of quarantined"""
    # get list of header files (this works for all sensors, that's why)
    hdrfiles = listdir_filename_pattern(subdir, '.*\.header$')
    quarantined_amplitude_list = [ i for i in hdrfiles if is_over_half_g(i.rstrip('.header')) ]
    
    # if needed, then move to quarantined
    qdir = os.path.join(subdir, 'quarantined')
    if quarantined_amplitude_list and not os.path.isdir(qdir):
        os.mkdir( qdir )
    for f in quarantined_amplitude_list:
        shutil.move(f, qdir)                    # move header file
        shutil.move(f.rstrip('.header'), qdir)  # move data file

    return len(quarantined_amplitude_list)


def process_too_small_files(subdir, max_bytes):
    """process single subdir to see if/what needs to be 'too-small' quarantined, return count of quarantined"""
    # get list of header files (this works for all sensors, that's why)
    hdrfiles = listdir_filename_pattern(subdir, '.*\.header$')
    quarantined_list = [ i for i in hdrfiles if is_too_small(i.rstrip('.header'), max_bytes) ]
    
    # if needed, then move to quarantined
    qdir = os.path.join(subdir, 'quarantined')
    if quarantined_list and not os.path.isdir(qdir):
        os.mkdir( qdir )
    for f in quarantined_list:
        shutil.move(f, qdir)                    # move header file
        shutil.move(f.rstrip('.header'), qdir)  # move data file

    return len(quarantined_list)


# FIXME this is not very surgical about start/stop range [but can it be better?]
def process_daterange_files(subdir, start, stop):
    """process single subdir to see if/what's in daterange and quarantines those, return count of quarantined"""
    # get list of header files (this works for all sensors, that's why)
    hdrfiles = listdir_filename_pattern(subdir, '.*\.header$')
    ffp = FileFilterPipeline(DateRangePadFile(start, stop))
        
    # if needed, then move to quarantined
    num_quar = len(list(ffp(hdrfiles)))
    qdir = os.path.join(subdir, 'quarantined')
    if  num_quar > 0 and not os.path.isdir(qdir):
        os.mkdir( qdir )
    for f in ffp(hdrfiles):
        shutil.move(f, qdir)                    # move header file
        shutil.move(f.rstrip('.header'), qdir)  # move data file
    
    return num_quar


def main(daydir):
    """iterate over day directory (only sams2 and samses subdirs for now)"""
    # get sams2 and samses directories
    subdirs = [ i for i in os.listdir(daydir) if os.path.isdir(os.path.join(daydir, i)) ]
    sams_subdirs = [ i for i in subdirs if (i.startswith('sams2_accel_') or i.startswith('samses_accel_')) ]
    check_dirs = [ os.path.join(daydir, sd) for sd in sams_subdirs ]
    for samsdir in check_dirs:
        #print samsdir; continue
        count1 = process_header_files(samsdir)
        count2 = process_amplitudes(samsdir)
        print 'length of quarantined list is %d + %d = %d for %s' % (count1, count2, count1 + count2, samsdir)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        d2 = datetime.datetime.now().date() - datetime.timedelta(days=2)
        daydir = datetime_to_ymd_path(d2)
    else:
        daydir = sys.argv[1]
    main(daydir)
