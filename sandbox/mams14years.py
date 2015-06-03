#!/usr/bin/env python

import datetime

# a generator to get datetimes (every day)
def next_day(dtm_start, dtm_stop):
    dtm = dtm_start
    yield(dtm)
    while dtm < dtm_stop:
        dtm += datetime.timedelta(days=1)
        yield(dtm)

if __name__ == "__main__":
    dtm_start = datetime.datetime(2001, 5, 3)
    dtm_stop  = datetime.datetime(2015, 5, 2)
    count = 0
    for day in next_day(dtm_start, dtm_stop):
        count += 1
        print count, day
    
