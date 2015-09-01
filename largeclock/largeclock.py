#!/usr/bin/env python

"""Use Tkinter to show a large digital clock."""

# 8/20/2015 Hrovat modified to allow for input arguments

import os
import sys
import time
import datetime
import ConfigParser
from Tkinter import *
#from pims.tkclock.db import query_aos
from pims.largeclock.db import query_aos

_PWORD = raw_input('samsops pword')

def getScriptPath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

# if no input args, then we try to read cfg file (fallback to hard-coded values)
if len(sys.argv) == 1:
    try:
        # attempt to read local config file
        script_path = getScriptPath()
        config_file = os.path.join(script_path, "largeclock.cfg")
        #config_file = r"C:\\largeclock\\largeclock.cfg"
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        font_size = int( config.get('font', 'size') )
        w = int( config.get('window', 'width') )
        h = int( config.get('window', 'height') )
    except:
        font_size = 180 # font size
        w, h = 1500, 200 # width and height of Tk root window
else:
    font_size = int(sys.argv[1])
    w = int(sys.argv[2])
    h = int(sys.argv[3])
    
# get root window and screen dimensions
root = Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# compute x and y coords for root window
x = (screen_width/2) - (w/2)
y = (screen_height/2) - (h/2)

# set root window size and position
geom = '%dx%d+%d+%d' % (w, h, x, y)
root.geometry( geom )

# initialize time, color, and clock label before main loop
time1 = ''
clock = Label(root, font=('arial', font_size, 'bold'), bg='white')
clock.pack(fill=BOTH, expand=1)

# update every 200 msec
def tick():
    global time1, dt1
    # get the current local time from the PC
    tnow = time
    time2 = tnow.strftime('%j  %H:%M:%S')
    # if time string has changed, update it
    # with label update once per second
    if time2 != time1:
        time1 = time2
        clock.config(text=time2)

        # every 5 seconds check if we are AOS/LOS and
        # update color & title text
        if time2[-1:] in ['0', '5']:
            ku_timestamp, ku_aos_los = query_aos(_PWORD)
            ku_time = ku_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            if ku_aos_los:
                clock.config(bg='green')
            else:
                clock.config(bg='yellow')
            root.title( 'ku_timestamp = %s' %  ku_time)

    # now call itself every 200 milliseconds
    # to update the time display as needed
    # could use >200 ms, but display gets jerky
    clock.after(200, tick)

dt1 = datetime.datetime.now()   
tick()
root.mainloop()