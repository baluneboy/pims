# a robust line from dbstatus.py output
#-------------------------------------------------------------
#\s*(?P<computer>\w+(?:-\w+)*)\s+(?P<table>.*)\s+(?P<count>\d+)\s+(?P<mintime>None|0|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(?P<maxtime>None|0|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(?P<age>[+-]?\d+)
_DBSTATUSLINE_PATTERN = (
    "\s*"                                                         # zero or more spaces
    "(?P<Host>\w+(?:-\w+)*)\s+"                                   # computer name (possibly hyphenated like mr-hankey) space
    "(?P<Sensor>\w+(?:-\w+)*)\s+"                                 # table name space
    "(?P<PktCount>\d+)\s+"                                        # count space
    "(?P<FirstPkt>None|0|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+" # mintime space
    "(?P<LastPkt>None|0|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"  # maxtime space
    "(?P<AgeSec>[+-]?\d+)\s+"                                     # age
    "(?P<Rate>[0-9\.]+)\s+"                                       # rate floating point number
    "(?P<Location>.*)"                                            # location
    )

_DBSTATUSLINE_PATTERN = r'\s*(?P<Host>\w+(?:-\w+)*)\s+(?P<Sensor>\w+(?:-\w+)*)\s+(?P<PktCount>\d+)\s+(?P<FirstPkt>None|0|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(?P<LastPkt>None|0|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(?P<AgeSec>[+-]?\d+)\s+(?P<Rate>[0-9\.]+)\s+(?P<Location>.*)'