#!/usr/bin/env python

"""Use Tkinter to show a sliding digital clock."""

import time
import datetime
from Tkinter import *
from pims.tkclock.geometry import TkGeometrySlider
from pims.tkclock.db import query_aos

_PWORD = raw_input('samsops pword')

w, h = 350, 100
x, y = 0, 450
tgi = TkGeometrySlider(w, h, x, y, sound_on=True)
root = tgi.root
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
time1 = ''
clock = Label(root, font=('arial', 60, 'bold'), bg='white')
clock.pack(fill=BOTH, expand=1)

def tick():
    global time1, dt1
    # get the current local time from the PC
    tnow = time
    time2 = tnow.strftime('%H:%M:%S')
    # if time string has changed, update it
    # with label & xpos update once per second
    if time2 != time1:
        time1 = time2
        clock.config(text=time2)
        xnew = tgi.time2xpos(time2)
        tgi.set_x( xnew )
        root.geometry(tgi)

        if time2[-1:] in ['0', '5']:
            ku_timestamp, ku_aos_los = query_aos(_PWORD)
            ku_time = ku_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            if ku_aos_los:
                clock.config(bg='green')
            else:
                clock.config(bg='red')
            root.title( 'ku_timestamp = %s' %  ku_time)

    # calls itself every 200 milliseconds
    # to update the time display as needed
    # could use >200 ms, but display gets jerky
    clock.after(200, tick)


dt1 = datetime.datetime.now()   
tick()
root.mainloop()