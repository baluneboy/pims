#!/usr/bin/env python
version = '$Id$'

import os
import re
import sys
import datetime
from pims.files.utils import filter_filenames
from pims.patterns.dailyproducts import _BATCHPCSAMAT_PATTERN

# FIXME we abandoned development of this (to be simpler)
#def free_space_up_to(free_gbytes_required, rootfolder, fullfile_pattern, older_than_days):
#    file_list= get_files_to_be_deleted(rootfolder, fullfile_pattern, older_than_days)
#    while file_list:
#        statv= os.statvfs(rootfolder)
#        if statv.f_bfree*statv.f_bsize >= free_gbytes_required*1024.0*1024.0*1024.0:
#            break
#        print 'remove %s' % file_list.pop() #os.remove(file_list.pop())

def get_files_to_be_deleted(dirpath, fullfile_pattern, older_than_days):
    files = []
    for f in filter_filenames(dirpath, re.compile(fullfile_pattern).match):
        file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(f))
        if datetime.datetime.now() - file_modified > datetime.timedelta(days=older_than_days):
            files.append(f)
    return files

if __name__ == "__main__":
    print 'Running %s...' % sys.argv[0],
    older_than_days = 30
    old_files = get_files_to_be_deleted('/misc/yoda/tmp/ike/offline/batch/results', _BATCHPCSAMAT_PATTERN, older_than_days)
    for f in old_files:
        os.remove(f)
    print 'removed %d files older than %d days.' % (len(old_files), older_than_days)
