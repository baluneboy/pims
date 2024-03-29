#!/usr/bin/env python

import random
import datetime
import time
import ouimeaux
from ouimeaux.environment import Environment


if __name__ == "__main__":
    print ""
    print "WeMo Randomizer"
    print "---------------"
    env = Environment()
    # TODO: run from 10am to 10pm
    try:
        env.start()
	print "starting discover (60s)"
        env.discover(60)
        print env.list_switches()
        print env.list_motions()
        print "---------------"
        while True:
            # http://stackoverflow.com/questions/306400/how-do-i-randomly-select-an-item-from-a-list-using-python
            switchRND = env.get_switch( random.choice( env.list_switches() ) )
            print switchRND
            switchRND.toggle()
	    print "wait 90s" 
            env.wait(90)
        
    except (KeyboardInterrupt, SystemExit):
        print "---------------"
        print "Goodbye!"
        print "---------------"
        # Turn off all switches
        for switch in ( env.list_switches() ):
            print "Turning Off: " + switch
            env.get_switch( switch ).off()

