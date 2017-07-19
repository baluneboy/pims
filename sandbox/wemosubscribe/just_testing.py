#!/usr/bin/env python

import time
from ouimeaux.environment import Environment
from ouimeaux.signals import statechange, receiver


def got_torch(switch):
    if switch.name == 'Torch':
        print "Switch found!", switch.name


def toggle_times(device, n=2, sec_sleep=1):
    def toggle_print(d):
        print d.name, "toggle"
        d.toggle()
    for i in xrange(n-1):
        toggle_print(device)
        time.sleep(sec_sleep)
    toggle_print(device)


env = Environment(got_torch)
env.start()
env.discover(seconds=5)
torch = env.get_switch('Torch')

toggle_times(torch, n=2, sec_sleep=1)

@receiver(statechange, sender=torch)
def switch_toggle(device, **kwargs):
    print device, kwargs['state']

sec_loop = 10
print 'Pass control to event loop for %d seconds.' % sec_loop
env.wait(timeout=sec_loop)  # Pass control to the event loop for 5 seconds (maybe this can be one hour for garage?)
