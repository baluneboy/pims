#!/usr/bin/env python

#import os
#import datetime
#import socket
#from collections import OrderedDict
#import pygame
#from pygame.locals import QUIT
#
import time
from pims.bigtime.timemachine import RapidTimeGetter, TimeGetter, TimeMachine
from pims.utils.pimsdateutil import unix2dtm

SLEEP = 1.0

def demo():

    smalls = [
        #    table  prefix  EDS      db host
        # -----------------------------------
        ('es03rt',   'MSG', 0.9, 'manbearpig'),
        ('es05rt',   'CIR', 0.9, 'manbearpig'),
        ('es06rt',   'FIR', 0.9, 'manbearpig'),
        ('121f08rt', 'F08', 0.9, 'manbearpig'),
        ('121f05rt', 'F05', 0.9, 'manbearpig'),
        ('121f04rt', 'F04', 0.9, 'manbearpig'),
        ('121f03rt', 'F03', 0.9, 'manbearpig'),
        ('121f02rt', 'F02', 0.9, 'manbearpig'),
    ]

    time_machines = []
    for table, prefix, expected_delta_sec, dbhost in smalls:
        tg = TimeGetter(table, host=dbhost)
        tm = TimeMachine(tg, expected_delta_sec=SLEEP/8)
        tm.prefix = prefix
        time_machines.append(tm)

    for x in range(11):
        for t in time_machines:
            t.update()
            if t.time:
                print t.prefix, unix2dtm(t.time).strftime('%j/%H:%M:%S')
            else:
                print t.prefix, None
        time.sleep(SLEEP)

if __name__ == '__main__':
    demo()
