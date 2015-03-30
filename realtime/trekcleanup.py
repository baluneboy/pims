#!/usr/bin/env python

import os
import re
import datetime
from pims.files.utils import listdir_filename_pattern, file_age_days
from shutil import move

def move_old_files(num_days_keep, rec_dir, file_pattern, temp_dir):
	pat_files = listdir_filename_pattern(rec_dir, file_pattern)
	old_files = [ f for f in pat_files if file_age_days(f) > num_days_keep ]
	count = 0
	bytes = 0
	for f in old_files:
		print 'move %s to temporary directory' % f
		try:
			fsize_bytes = os.path.getsize(f)
			move(f, temp_dir)
			count += 1
			bytes += fsize_bytes
		except Exception, e:
			print e.message

	s = '# Cleaned Recordings folder using num_days_keep = %d and found %d files to move' % (num_days_keep, len(old_files))
	if count:
		s += '\n# %d files moved to %s = %.1f GB' % (count, temp_dir, bytes/(1024.0**3))
	return s

def main():
    
    # Recordings folder file recycle parameters
    num_days_keep = 14 # keep 2 weeks on hand
    file_pattern = '(SCT|TRT) (\d{4}-\d{2}-\d{2} \d{2}~\d{2}~\d{2}~\d{3} ){2}(dump2)*apid(412|890|898)(\.LNK)*'
    rec_dir = '/media/trek21/Recordings'
    temp_dir = '/media/trek21/temprecs'
    
    # Relative datetime parameters
    TODAY = datetime.datetime.today().date()
    TWOWEEKSAGO = TODAY - datetime.timedelta(days=14)
    THREEWEEKSAGO = TODAY - datetime.timedelta(days=21)

    summary_str = move_old_files(num_days_keep, rec_dir, file_pattern, temp_dir)

    s  = '\n\n'
    s += '=' * 67
    s += '\n' + TODAY.strftime('%Y GMT %j')
    s += '\n\n' + summary_str
    s += '\n\nCMD LINE CMD monday'
    s += '\n# wait 2 minutes since sending "monday" cmd'
    s += '\nFILE DOWNLINK /usr/tgz/samslogs' + TODAY.strftime('%Y%j.tgz')
    s += '\n\n# REMOVE THESE CHECKLIST LINES AFTER DONE WITH THEM'
    s += '\n# 1. Check OSTPV for SAMS-CU-CMD from GMT 15:00 to 15:20.'
    s += '\n# 2. Set phone alarm for local time 20 minutes before SAMS-CU-CMD.'
    s += '\n# 3. IVoDS audio check.'
    s += '\n# 4. Activate Command Processing (make it mostly green).'
    s += '\n# 5. Clean Recordings folder using datemodified:%s..%s' % (THREEWEEKSAGO.strftime('%m/%d/%Y'), TWOWEEKSAGO.strftime('%m/%d/%Y'))
    s += '\n# 6. Remove this checklist set of lines.'		
    s += '\n# REMOVE THESE CHECKLIST LINES AFTER DONE WITH THEM'

    return s

if __name__ == "__main__":
    s = main()
    with open('/media/trek21/temprecs/log.txt', 'a') as f:
        f.write(s)
