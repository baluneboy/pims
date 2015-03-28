#!/usr/bin/env python
version = '$Id$'

# TODO
# implement "highlights" from config file [for now, show log line matches in parameters['messages'] output]

import datetime
import os
import sys
import glob
import tarfile
import re
from recipes_fileutils import fileAgeDays, filter_filenames
from StringIO import StringIO
import numpy as np
from configobj import ConfigObj

FILESYSLIM = 90

# input parameters
defaults = {
             'top_dir':     '/media/HROVAT_4GB/sams', # where to look for TGZ file
             'extract_dir': '/tmp/tgz',               # extract to this path
             'messages': [],                          # list messages
             'details':  [],                          # list details
             'lines_to_look_at':  [],                 # list dated log lines to look at
             'config_file': '/home/pims/dev/programs/python/samslogs/samslogs.cfg', # config file for what to do with each file
             'files_leftover': [],                 # list of files checked
}
parameters = defaults.copy()

def isnotempty(f):
    return os.path.getsize(f) > 0    
    
def get_nonempty_log_files(dirpath):
    """walk dirpath and append files that do not endwith gz"""
    nonempty_nongz_files = []
    for root, dirnames, filenames in os.walk(dirpath):
        for filename in filenames:
            abspath = os.path.join(root, filename)
            if not abspath.endswith('gz') and isnotempty(abspath):
                nonempty_nongz_files.append(abspath)
    return nonempty_nongz_files

def extract(tar_file, extract_path):

    # open the tar file
    tfile = tarfile.open(tar_file)
    
    # process it
    if tarfile.is_tarfile(tar_file):
        
        # list all contents
        #print "tar file contents:"
        #print tfile.list(verbose=True)
        
        # extract all contents
        #print '>extracting %s' % tar_file
        #print '>to this path %s' % extract_path
        tfile.extractall(extract_path)
        #print '>done'
        
    else:
        print tar_file + " is not a tar file."
    
    tfile.close() 

def check_filesystems(file_str):
    m = re.compile(r'%s.*?%s' % ('df -k', 'ls -al'), re.S)
    a = m.search(file_str).group(0)
    lines = a.split('\n')
    predicate = re.compile('.*\d+\%').match
    matches = [x for x in lines if predicate(x)]
    a = StringIO('\n'.join(matches))
    data = np.genfromtxt(a, names=['filesys','blocks','used','avail','capacity','mount'], dtype=None)
    for filesys, blocks, used, avail, capacity, mount in zip(data['filesys'], data['blocks'], data['used'], data['avail'], data['capacity'], data['mount']):
        line_new = '{0:>4} {1:<11} {2}'.format(capacity, filesys, mount)
        parameters['details'].append('%s' % line_new)
        c = int(capacity[:-1])
        if c > FILESYSLIM:
            parameters['messages'].append( 'FILESYSTEM %s AT %d%% IS ABOVE THRESHOLD OF %d%%.' % (filesys, c, FILESYSLIM) )
            
def check_processes(lines):
    patterns_to_match = ['.*intentional_mismatch.*', '.*xntpd', '.*RIC_manager', '.*telemetry_downlinker', '.*cumain', '.*icu_state_monitor', '.*bootpd\s+', '.*generic_client', '.*rarpd -a', '.*cycle_rarpd']
    for pat in patterns_to_match:
        predicate = re.compile(pat).match
        matches = [x for x in lines if predicate(x)]
        if len(matches) == 0:
            parameters['messages'].append( 'DID NOT FIND ANY LINES TO MATCH A PROCESS LIKE "%s" in %s.' % (pat, parameters['txt_file']) )
        for m in matches:
            parameters['details'].append(m)

def process_list_file(txt_file):
    #print 'Processing %s...' % txt_file
    with open(txt_file, 'r') as f:
        file_str = f.read()
    lines = file_str.splitlines()
    check_filesystems(file_str)
    check_processes(lines)

def extract_log_messages(tgz_file, extract_dir):
    #print 'Processing %s...' % tgz_file
    try:
        extract(tgz_file, extract_dir)
    except:
        print 'Problem extracting %s' % tgz_file

def verify_one_file(prefix, ddd, ext):
    name = '%s%s.%s' % (prefix, ddd, ext)
    fullfile = os.path.join( parameters['top_dir'], name )
    results = glob.glob( fullfile )
    if len(results) != 1:
        print 'expected exactly one file like %s, but got %d' % (fullfile, len(results))
        return False, None
    else:
        f = results[0]
        if fileAgeDays(f) > 1:
            print 'got %s, but age > 1 day' % f
            return False, None
        return True, results[0]    
    
def parametersOK():
    """check for reasonableness of parameters"""
    if not os.path.exists(parameters['top_dir']):
        print 'top_dir (%s) does not exist' % parameters['top_dir']
        return False
    
    if not os.path.exists(parameters['extract_dir']):
        print 'extract_dir (%s) does not exist' % parameters['extract_dir']
        return False    
    
    ddd = datetime.datetime.today().strftime('%03d')

    blnGotTgz, tgz_file = verify_one_file('samslogs', ddd, 'tgz')
    if not blnGotTgz:
        return False
    else:
        parameters['tgz_file'] = tgz_file

    blnGotTxt, txt_file = verify_one_file('list', ddd, 'txt')
    if not blnGotTxt:
        return False
    else:
        parameters['txt_file'] = txt_file
    
    return True # all OK, return 0 otherwise

def range_GMT(matched_lines):
    pass
    
def median_frequency(matched_lines):
    pass

class LogLineMatcher(object):
    
    def __init__(self, label='unknown', lines=None, dlabel={'pattern': '.*', 'attributes': ['range_GMT', 'median_frequency']}):
        self.label = label
        self.lines = lines
        self.dlabel = dlabel
        self.pattern = self.get_pattern()
        self.attributes = self.get_attributes()
        self.total_lines = len(lines)
        self.matching_lines = self.get_matches()
        self.num_lines_match = len(self.matching_lines)

    def remove_matching_lines(self):
        return [line for line in self.lines if line not in self.matching_lines]

    def get_pattern(self):
        return self.dlabel['pattern']
    
    def get_attributes(self):
        return self.dlabel['attributes']
    
    def __str__(self):
        numstr = "  matched {0:>5d} of {1:>5d} lines".format(self.num_lines_match, self.total_lines)
        s = '%s for %s' % ( numstr, self.label )
        return s

    def get_matches(self):
        return [line for line in self.lines if re.match(self.pattern,line)]

def process_log_message_files(filename=parameters['config_file']):
    config = ConfigObj(filename)
    dirpath = parameters['extract_dir']
    # These "leftover" files get removed from list after processed, which leaves leftovers when done!
    parameters['files_leftover'] = get_nonempty_log_files(dirpath)
    parameters['details'].append('Found %d nonempty, nongz files.' % len(parameters['files_leftover']))
    files = config['files']
    for file_pattern, dfile in files.items():
        if eval(dfile['active']):
            del dfile['active']
            fullfile_pattern = os.path.join(dirpath, file_pattern)
            files_to_process = [f for f in filter_filenames(dirpath, re.compile(fullfile_pattern).match)]
            [process_logfile(f, dfile) for f in files_to_process]
    for fullname in parameters['files_leftover']:
            parameters['details'].append('CONFIG "active" SET TO IGNORE %s.' % fullname)
            parameters['messages'].append('CONFIG "active" SET TO IGNORE %s.' % fullname)

def process_logfile(fname, dfile):
    parameters['details'].append('-'*33)
    parameters['details'].append('Processing %s ...' % fname)
    with open(fname, 'r') as f:
        file_str = f.read()
    lines = file_str.splitlines()  
    for label, dlabel in dfile.items():
        p = LogLineMatcher(label=label, lines=lines, dlabel=dlabel)
        lines = p.remove_matching_lines()
        strlines = str(p) + " (%d lines remain)" % len(lines)
        parameters['details'].append(strlines)
    # do something about remaining lines, if any
    if len(lines) > 0:
        parameters['details'].append('  NOT ALL LINES MATCHED.')
        unmatchstr = '{0:.>6} LINES REMAIN UNMATCHED FROM {1} (SEE DETAILS ABOVE).'.format(len(lines), fname) 
        parameters['messages'].append(unmatchstr)
        parameters['lines_to_look_at'].append('* Lines from %s' % fname)
        for line in lines:
            parameters['lines_to_look_at'].append(line)
    else:
        parameters['details'].append('  ALL LINES WERE MATCHED.')
    try:
        parameters['files_leftover'].remove(fname)
    except Exception as e:
        print 'could not remove %s' % fname

def summary():
    # the "process" lines below append to 'details' or 'messages' for output below
    
    print 'vvv BEGIN KEY DETAILS vvv'
    for d in parameters['details']:
        print d
    print '^^^ END KEY DETAILS ^^^'
    
    print '\nvvv BEGIN UNMATCHED LOG LINES vvv'
    for line in parameters['lines_to_look_at']:
        print line
    print '^^^ END UNMATCHED LOG LINES ^^^'
    
    # this list gets decimated along the way, leaving behind unprocessed filenames
    for f in parameters['files_leftover']:
        parameters['messages'].append('-DID NOT PROCESS LEFTOVER FILE %s', f)
    
    print '\nvvv BEGIN IMPORTANT MESSAGES vvv'
    for msg in parameters['messages']:
        print msg
    print '^^^ END IMPORTANT MESSAGES ^^^'
    
def main():
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parametersOK():
            extract_log_messages(parameters['tgz_file'], parameters['extract_dir'])
            get_nonempty_log_files(parameters['extract_dir'])
            process_list_file(parameters['txt_file'])
            process_log_message_files()
            summary()
    return 0

if __name__ == '__main__':
    sys.exit(main())