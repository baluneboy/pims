#!/usr/bin/env python

import subprocess
from pims.database.pimsquery import get_last_gmt


def get_host_sensor_pairs():
    out = subprocess.check_output("/home/pims/dev/programs/bash/get_host_sensor_pairs.bash", stderr=subprocess.STDOUT, shell=False)
    s = out.rstrip(' ').split(' ')
    hs = [tuple(x.split('_')) for x in s]
    return hs


if __name__ == '__main__':
    host_sensor_pairs = get_host_sensor_pairs()
    print 'max(time) from each db table:\n', '-' * 33
    for t in host_sensor_pairs:
        host, sensor = t[0], t[1]
        max_time = get_last_gmt(host, 'pims', sensor=sensor)
        print max_time, sensor
    raw_input('Now replay data from CU, then after that is complete, press Enter to continue...')
    print 'done'
