#!/usr/bin/env python

from pims.strings.utils import underscore_as_datetime

if __name__ == '__main__':

    from datetime import datetime
    ind_list = list(range(7,19,3))
    ind_list.append(3)
    ind_list.sort(reverse=True)
    for i in ind_list:
        timestr = datetime(2013,10,3,8,55,59,999000).strftime('%Y_%m_%d_%H_%M_%S.%f')[0:-i]
        print '-'*44
        print timestr
        print underscore_as_datetime(timestr)