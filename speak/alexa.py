#!/usr/bin/env python

import sys
import time
import datetime
import subprocess

DEFAULT_MSG = 'discover devices'


def alexa_speak(message):
    status = subprocess.call(["espeak","-a 122 -s 110 -p 22 ", 'Alexa'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.5)
    status = subprocess.call(["espeak","-a 122 -s 110 -p 22 ", message], stdout=subprocess.PIPE, stderr=subprocess.PIPE)   
    return status


def is_today_in_range(today, dlower, dupper):
    """return True if today between the dlower and dupper days of month"""
    return dlower <= today.day <= dupper

def espeak(message):
    status = subprocess.call(["espeak","-a 122 -s 110 -p 22 ", message], stdout=subprocess.PIPE, stderr=subprocess.PIPE)   
    return status


def announce_capone():
    """if capone date range, then announcement"""
    today = datetime.date.today()
    msg = 'Hey there, it is time to pay the piper.'
    if is_today_in_range(today, 10, 16):
        # today is between 10th and 16th
        if today.weekday() == 5:
            # it's Saturday because weekday() returns 5 for Saturday    
            msg += ' I repeat, it is time to pay the piper.'
        espeak(msg)
    # no announcement if it's not in day range


if __name__ == '__main__':
    if len(sys.argv) == 1:
        msg = DEFAULT_MSG
    else:
        msg = sys.argv[1]
    status = alexa_speak(msg)
    sys.exit(status)
