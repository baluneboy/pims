#!/usr/bin/env python

import os
import re
from datetime import datetime
from dateutil import parser

DOWNLINKFILEPAT = '(?P<pth>.*)\{(?P<ymd>\d{4}-\d{2}-\d{2})\}\{(?P<hms>\d{2}-\d{2}-\d{2})\}_\d+_cmd_.*\.txt$'
SAMSLISTSTRINGS = ['ps ax', 'df -k', 'ls -l']

class CommandDownlinkFile(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.dtm_named = self.get_named_timestamp()
        self.dtm_mtime = self.get_os_mtime()

    def __str__(self):
        cname = self.__class__.__name__
        if not self.dtm_named:
            return 'NOT %s: %s' % (cname ,self.filename)
        s = '%s: %s' % (cname ,self.filename)
        s += ', TIMESTAMP = %s' % str(self.dtm_named)
        s += ', MTIME = %s' % str(self.dtm_mtime)
        return s
    
    def get_named_timestamp(self):
        m = re.match(DOWNLINKFILEPAT, self.filename)
        dtm_named = None
        if m:
            ymdstr = m.group('ymd').replace('_', '-')
            hmsstr = m.group('hms').replace('_', ':')
            dstr = ymdstr + ' ' + hmsstr
            dtm_named = parser.parse(dstr)
        return dtm_named
    
    def get_os_mtime(self):
        dtm_mtime = None
        if self.dtm_named:
            utime = os.path.getmtime(self.filename)
            dtm_mtime = datetime.fromtimestamp(utime)
        return dtm_mtime

    def is_disguised_samslist(self):
        return self.contains(SAMSLISTSTRINGS)
    
    def contains(self, strings):
        if isinstance(strings, str):
            strings = [strings]
        with open(self.filename, 'r') as f:
            content = f.read()
            for s in strings:
                if s not in content:
                    return False
        return True

if __name__ == '__main__':
    file_name = '/tmp/{2015-01-26}{15-07-33}_1422284716_cmd_12345_wx3yz.txt'
    cdf = CommandDownlinkFile(file_name)
    if cdf.is_disguised_samslist():
        print 'YES disguised samslist file %s' % file_name
    else:
        print 'NOT disguised samslist file %s' % file_name
