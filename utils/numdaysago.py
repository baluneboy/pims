#!/usr/bin/env python

import sys
import datetime
from dateutil import parser
from pims.utils.pimsdateutil import datetime_to_days_ago
print datetime_to_days_ago(parser.parse(sys.argv[1]))
