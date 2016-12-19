#!/usr/bin/env python

from pims.utils.pimsdateutil import unix2dtm, dtm2unix
from timemachine import EeTimeGetter
from pims.database.ee_packets import dbstat
from pims.database.pimsquery import db_connect


# return tuple of count, min(time), and max(time) from ee table
def query_timestamps(table, host='towelie'):
    # select count(*), from_unixtime(min(time)), from_unixtime(max(time)) from 122f04;
    query_str = 'select count(*), from_unixtime(min(time)), from_unixtime(max(time)) from %s;' % table
    res = db_connect(query_str, host, retry=False)
    count, tmin, tmax = res[0]
    return count, tmin, tmax


# get pims db ee_packet table timestamp(s) [maybe from towelie]
class MultiTimeGetter(EeTimeGetter):
    """get pims db ee_packet table timestamp(s)"""

    #def __init__(self, *args, **kwargs):
    #    self.ee_id = kwargs.pop('ee_id')       
    #    super(MultiTimeGetter, self).__init__(*args, **kwargs)

    def _get_time(self):
        return query_timestamps(self.table, host=self.host)

    
etg2 = MultiTimeGetter('122f03', ee_id='122-f03', host='towelie')
print etg2._get_time()[-1]
raise SystemExit