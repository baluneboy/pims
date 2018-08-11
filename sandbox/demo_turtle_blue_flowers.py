#!/usr/bin/env python

from turtle import *
import random
import Tkinter

def demo(n):
    for n in range(n):
        penup()
        goto(random.randint(-400, 400), random.randint(-400, 400))
        pendown()
    
        red_amount   = random.randint( 0,  30) / 100.0
        blue_amount  = random.randint(50, 100) / 100.0
        green_amount = random.randint( 0,  30) / 100.0
        pencolor((red_amount, green_amount, blue_amount))
    
        circle_size = random.randint(10, 40)
        pensize(random.randint(1, 5))
    
        for i in range(6):
            circle(circle_size)
            left(60)


def demo2(fwd_steps, a):
    fred = Pen()
    fred.left(a)
    fred.color("blue")
    fred.forward(fwd_steps)
    fred.circle(fwd_steps)
    fred.circle(-fwd_steps)
    fred.forward(fwd_steps)
    #fred.home()

def demo3(wn):
    wn.bgcolor("lightgreen")
    tess = Turtle()
    tess.color("blue")
    #tess.shape("turtle")
    
    tess.up()                       # this is another way to pick up the pen
    for dist in range(5,60,2):      # start with dist = 5 and grow by 2
        tess.stamp()                # leave an impression on the canvas
        tess.forward(dist)          # move tess along
        tess.right(24)              # and turn her
    tess.color("red")

# get window on top
wn = Screen()
rootwindow = wn.getcanvas().winfo_toplevel()
rootwindow.call('wm', 'attributes', '.', '-topmost', '1')
rootwindow.call('wm', 'attributes', '.', '-topmost', '0')
wn.title("Hello, Turtle!")  # Set the window title

# draw a few blue flowers
#demo(3)

#for dist in range(45, 45*4, 45):
#    for angle in range(0, 360, 90):
#        demo2(dist, angle)

demo3(wn)

# keep graphics window alive
Tkinter.mainloop()
