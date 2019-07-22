#!/usr/bin/env python

"""Use Tkinter to show a large digital clock."""

# 8/20/2015 Hrovat modified to allow for input arguments
# 9/1/2015  Hrovat modified for white bg when yoda db problem
# 4/27/2018 Hrovat modified for new colors when MSFC telemetry went wonky

import os
import sys
import time
import datetime
import ConfigParser
from Tkinter import *
from multiprocessing import Queue

from pims.largeclock.db import query_aos
#from pims.largeclock.timeout import run_with_timeout

_PWORD = raw_input('samsops pword: ') # USE TEMPORARY HARD-CODED FOR PY2EXE

# get path to this script; used to find largeclock.cfg (config) file
def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

# if no input args, then we try to read cfg file (fallback to hard-coded values)
def get_config():
    if len(sys.argv) == 1:
        try:
            # attempt to read local config file
            #script_path = get_script_path()
            #config_file = os.path.join(script_path, "largeclock.cfg")
            if os.name is 'posix':
                script_path = get_script_path()
                config_file = os.path.join(script_path, "largeclock.cfg")
            else:
                config_file = r"C:\\largeclock\\largeclock.cfg"               
            config = ConfigParser.ConfigParser()
            config.read(config_file)
            font_size = int( config.get('font', 'size') )
            w = int( config.get('window', 'width') )
            h = int( config.get('window', 'height') )
            _default = config.get('timeformat', 'default')
            _custom = config.get('timeformat', 'custom')
        except:
            font_size = 180 # font size
            w, h = 1500, 200 # width and height of Tk root window
            _default='%Y-%m-%d, %j/%H:%M:%S'
            _custom='%Y:%j:%H:%M:%S'
    else:
        font_size = int(sys.argv[1])
        w = int(sys.argv[2])
        h = int(sys.argv[3])
        _default = sys.argv[4]
        _custom = sys.argv[5]
   
    return font_size, w, h, _default, _custom

# get query results for Ku AOS/LOS with timeout
def get_aos_query_results_with_timeout(_PWORD):
    timeout_sec = 3
    out_q = Queue()
    args = (_PWORD, out_q)
    kwargs = {}
    finished = run_with_timeout(query_aos, timeout_sec, args, kwargs)
    if finished:
        if out_q.empty():
            return None, None
        else:
            return out_q.get()
    else:
        return None, None # hit the timeout

# update every 200 msec
def tick():
    global time1, dt1
    # get the current local time from local machine
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
            #ku_timestamp, ku_aos_los = get_aos_query_results_with_timeout(_PWORD)
            if ku_timestamp:
                ku_time = ku_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                if ku_aos_los:
                    clock.config(bg='green')
                else:
                    clock.config(bg='yellow')
            else:
                ku_time = "yoda db connection error"
                clock.config(bg='white')
            root.title( 'ku_timestamp = %s' %  ku_time)

    # now call tick every 200 milliseconds to update display
    clock.after(200, tick)

# menu callback for copying time to clipboard
def menu_callback(fmt):
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(datetime.datetime.now().strftime(fmt))
    r.destroy()
    
if __name__ == "__main__":
    
    # get font size, window width, and window height
    font_size, w, h, _default, _custom = get_config()
    
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
    
    # create popup menu
    menu = Menu(root, tearoff=0)
    menu.add_command(label="CopyDefault", command=lambda: menu_callback(_default))
    menu.add_command(label="CopyCustom", command=lambda: menu_callback(_custom))   
    
    def popup(event):
        menu.post(event.x_root, event.y_root)    
    
    # initialize time, color, and clock label before main loop
    time1 = ''
    clock = Label(root, font=('arial', font_size, 'bold'), bg='white')
    clock.pack(fill=BOTH, expand=1)
    clock.bind("<Button-3>", popup)
    
    # get time now, do first tick, and start main loop
    dt1 = datetime.datetime.now()   
    tick()
    root.mainloop()
