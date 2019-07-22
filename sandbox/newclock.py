import time

try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk

def tick(time1):
    # get the current local time from the PC
    time2 = time.strftime('%H:%M:%S')
    # if time string has changed, update it
    if time2 != time1:
        time1 = time2
        clock.config(text=time2)
    # calls itself every 200 milliseconds
    # to update the time display as needed
    clock.after(200, tick, time1)

root = tk.Tk()
clock = tk.Label(root, font=('times', 20, 'bold'), bg='green')
clock.pack(fill='both', expand=1)
tick('foo')
root.mainloop()

