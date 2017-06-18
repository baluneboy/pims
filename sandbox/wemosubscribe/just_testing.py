#!/usr/bin/env python

from ouimeaux.environment import Environment
from ouimeaux.signals import statechange, receiver


def got_torch(switch):
    if switch.name == 'Torch':
        print "Switch found!", switch.name


env = Environment(got_torch)
env.start()
env.discover(seconds=5)
torch = env.get_switch('Torch')


@receiver(statechange, sender=torch)
def switch_toggle(device, **kwargs):
    print device, kwargs['state']

env.wait(timeout=10)  # Pass control to the event loop for 10 seconds
