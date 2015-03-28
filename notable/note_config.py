#!/usr/bin/env python

from ConfigParser import SafeConfigParser
from os.path import dirname, join, expanduser

# NOTE: the files in config.read are optional, but with each that exists
#       subsequent one will override earlier one(s) on field-by-field basis

"""
GET THESE FILES IN PLACE TO SEE EXAMPLE OF LAYERED APPROACH
AND TRY VARIOUS COMBINATIONS OF THESE FILES EXISTING OR NOT

FIRST, defaults.ini in RELATIVE_SUBDIR of PROGRAM_DIR (where this file is):
--------------------------------------------------------
# tool/defaults.ini
[server]
# default host and port
host=localhost
port=8080
url=http://%(host)s:%(port)s/

NEXT, ~/.exampletool.ini for user's own prefs:
--------------------------------------------------------
# ~/.exampletool.ini
[server]
# user overrides default port
port=5000

FINALLY localconfig.ini for special config in $PWD
--------------------------------------------------------
# localconfig.ini
[server]
# override with special hostname
host=www.ninjarockstar.ken

"""

PROGRAM_DIR = dirname(__file__)
RELATIVE_SUBDIR = 'data'
config = SafeConfigParser()
print 'config files being used:', config.read([
    join(PROGRAM_DIR, RELATIVE_SUBDIR, 'defaults.ini'),
    expanduser('~/.exampletool.ini'),
    'localconfig.ini'
])
print config.sections()
print 'host:', config.get('server', 'host')
print 'port:', config.get('server', 'port')