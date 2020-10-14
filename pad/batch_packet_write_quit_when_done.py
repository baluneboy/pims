#!/usr/bin/env python

import subprocess

#          t1                     t2
#          GMT_START_TIME         GMT_STOP_TIME
times = [('2020-08-04@03:36:00', '2020-08-04@03:40:00'),
         ('2020-08-04@05:14:00', '2020-08-04@05:16:00'),
         ('2020-08-04@16:17:00', '2020-08-04@16:20:00')]

#            host      sensor
sensors = [('chef',   '121f05'),
           ('chef',   'es06'),
           ('chef',   'es20'),
           ('kenny',  'es05'),
           ('kenny',  'es09'),
           ('timmeh', '121f02'),
           ('timmeh', '121f08'),
           ('tweek',  '121f03'),
           ('tweek',  '121f04')]


DRYBASHCMD = '/home/pims/dev/programs/bash/packetwritequitwhendone.bash -n "T1" "T2" HOST SENSOR cartman:/home/pims/temp/padger'

for t1, t2 in times:
    for host, sensor in sensors:
        cmd = DRYBASHCMD.replace('T1', t1).replace('T2', t2).replace('HOST', host).replace('SENSOR', sensor)
        cmd_list = [arg.replace('@', ' ') for arg in cmd.split()]
        print cmd_list
        # print cmd.replace('@', ' ').replace(' -n', '')

        process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)
        out, err = process.communicate()
        print out
        print err
