#!/usr/bin/env python

import datetime
from pims.database.pimsquery import prune_by_time

two_days_ago = datetime.datetime.now().date() - datetime.timedelta(days=2)


def take_care_of_mimsy(table='121f03', dtm_min=two_days_ago):
    res = prune_by_time('mimsy', table, dtm_min)
    return res


if __name__ == '__main__':
    res = take_care_of_mimsy()
    print res
