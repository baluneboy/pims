#!/usr/bin/env python

import time
from pims.database.pimsquery import insert_keep_alive_for_labview, get_packet_count
from pims.realtime.less_flimsy_dbgapdetect import defaults


def get_sensorhosts():
    """return dict of {sensor: host} by parsing defaults"""
    sensorhosts = dict()
    for sensor, host, db, pkts in defaults['sensorhosts']:
        sensorhosts[sensor] = host
    return sensorhosts


def parse_host(sensor):
    """return host from given sensor by parsing defaults"""
    sensorhosts = get_sensorhosts()
    host = sensorhosts[sensor]
    return host


def main():
    for sensor in ['es05', 'es06', 'es20']:
        host = parse_host(sensor)
        count = get_packet_count(host, 'pims', sensor)
        if count == 0:
            print "insert_keep_alive_for_labview", sensor, count
            insert_keep_alive_for_labview(host, 'pims', sensor)


if __name__ == '__main__':
    main()
