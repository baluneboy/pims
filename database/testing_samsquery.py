#!/usr/bin/env python

import datetime
from pims.database.samsquery import RtsDrawerQuery, InsertToDeviceTracker
from pims.database.samsquery import _SCHEMA_SAMS, _UNAME_SAMS, _PASSWD_SAMS, _HOST_SAMS


start = datetime.datetime(2017, 12, 31,  0,  0,  0)
stop =  datetime.datetime(2018,  1,  1,  0,  0, 10)
dqc = RtsDrawerQuery(_HOST_SAMS, _SCHEMA_SAMS, _UNAME_SAMS, _PASSWD_SAMS, 'er1_drawer_1_current', begin_date=start, end_date=stop)
dfc = dqc.dataframe_from_query()
print dfc

i2dt = InsertToDeviceTracker(_HOST_SAMS, _SCHEMA_SAMS, 'device_tracker', _UNAME_SAMS, _PASSWD_SAMS)
i2dt.insert('trebuchex', 'sling', 'fathoms', '2009-01-02', '2009-01-03 12:00:04', 'averagedio', 9.45)
