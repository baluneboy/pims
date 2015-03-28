#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python curses gadget (python 2.x/3.x).

Simple matrix-like console "screensaver". Works on systems which have
python installation with curses module. Original code written in 2007.

https://github.com/drmats/matrix-curses
"""

import sys
import os
import random
import math
import curses
import threading

__all__ = [
    "begin_gui_mode",
    "Codechunk",
    "compute_color",
    "end_gui_mode",
    "init_pairs",
    "Main",
    "MC",
    "Thr"
]

__author__ = "drmats"
__copyright__ = "copyright (c) 2014, drmats"
__version__ = "0.1.1"
__license__ = "BSD 2-Clause license"

class MC:

    """Misc. program constants."""

    MATRIX_START_LINE       = 0.0
    NR_OF_MATRIX_COLORS     = 6
    GREEN_HEAD_PROBABILITY  = 90
    WHITE_HEAD_PROBABILITY  = 1
    CYAN_HEAD_PROBABILITY   = 1
    BLUE_HEAD_PROBABILITY   = 1
    YELLOW_HEAD_PROBABILITY = 5
    RED_HEAD_PROBABILITY    = 2
    HEAD_MAXLEN             = 30
    FALLING_MINSPEED        = 20
    FALLING_MAXSPEED        = 110

def begin_gui_mode ():
    """Initialize curses mode."""
    win = curses.initscr()
    curses.start_color()
    curses.cbreak()
    win.keypad(1)
    curses.noecho()
    curses.curs_set(0)
    return win

def init_pairs ():
    """Initialize default color-pairs."""
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(10, curses.COLOR_GREEN, curses.COLOR_BLACK)

def end_gui_mode (win):
    """End curses mode."""
    win.clear()
    win.refresh()
    curses.curs_set(1)
    curses.endwin()

def compute_color (prob_table):
    """Choose color number from a probability range."""
    p = n = 0
    rnd = random.randrange(0, 100)
    i = 0
    for pti in prob_table:
        n += pti
        if p <= rnd and rnd < n:
            return i
        p = n
        i += 1
    return 0

class Codechunk:

    """Structure representing one "falling" code chunk."""

    def __init__ (
        self, x, y, erasing_y, color,
        falling_speed, erasing_speed, head_length
    ):
        """Default constructor."""
        # horizontal position on the screen
        self.x = x
        # vertical positions on the screen
        self.y = y
        self.erasing_y = erasing_y
        # ncurses COLOR_PAIR(n) code-chunk colors
        self.color = color
        # speed of chunk head and tail
        self.falling_speed = falling_speed
        self.erasing_speed = erasing_speed
        # length of chunk head
        self.head_length = head_length

class Thr(threading.Thread):

    """Thread responsible for displaying all stuff."""

    def __init__ (self, scr, sleep_time):
        """Default constructor."""
        threading.Thread.__init__(self)
        self.stop_this_thread = False
        self.scr = scr
        self.sleep_time = sleep_time
        self.start()


    def run (self):
        """Application "work-horse"."""
        # fill-up some missing MC defines
        MC.LINES, MC.COLS = self.scr.getmaxyx()
        MC.MATRIX_END_LINE = MC.LINES

        # init tables (lists)
        self.color_table = [
            curses.color_pair(10) | curses.A_BOLD,
            curses.color_pair(0)  | curses.A_BOLD,
            curses.color_pair(2)  | curses.A_BOLD,
            curses.color_pair(6)  | curses.A_BOLD,
            curses.color_pair(8)  | curses.A_BOLD,
            curses.color_pair(9)  | curses.A_BOLD
        ]
        self.head_prob_table = [
            MC.GREEN_HEAD_PROBABILITY,
            MC.WHITE_HEAD_PROBABILITY,
            MC.CYAN_HEAD_PROBABILITY,
            MC.BLUE_HEAD_PROBABILITY,
            MC.YELLOW_HEAD_PROBABILITY,
            MC.RED_HEAD_PROBABILITY
        ]

        # init chunks
        self.cc = []
        for i in range(MC.COLS):
            falling_speed = random.randrange(
                MC.FALLING_MINSPEED, MC.FALLING_MAXSPEED
            ) * 0.01
            self.cc = [Codechunk(
                i,
                MC.MATRIX_START_LINE,
                MC.MATRIX_START_LINE - (random.randrange(0, MC.LINES)),
                self.color_table[compute_color(self.head_prob_table)],
                falling_speed,
                falling_speed - 0.20,
                random.randrange(2, MC.HEAD_MAXLEN)
            )] + self.cc

        # main loop
        while not self.stop_this_thread:
            # do some work for every chunk
            for cci in self.cc:
                # "erasing tail"
                if (
                    cci.erasing_y >= MC.MATRIX_START_LINE and
                    cci.erasing_y < MC.MATRIX_END_LINE
                ):
                    try:
                        self.scr.addch(
                            int(math.floor(cci.erasing_y)), cci.x,
                            ' ', cci.color
                        )
                    except:
                        pass
                # draw "tail"
                if (
                    cci.y - cci.head_length >= MC.MATRIX_START_LINE and
                    cci.y - cci.head_length < MC.MATRIX_END_LINE
                ):
                    try:
                        self.scr.addch(
                            int(math.floor(cci.y - cci.head_length)), cci.x,
                            chr(random.randrange(30, 120)),
                            cci.color & ~curses.A_BOLD
                        )
                    except:
                        pass
                # draw "head"
                if (
                    cci.y >= MC.MATRIX_START_LINE and
                    cci.y < MC.MATRIX_END_LINE
                ):
                    try:
                        self.scr.addch(
                            int(math.floor(cci.y)), cci.x,
                            chr(random.randrange(30, 120)),
                            cci.color
                        )
                    except:
                        pass
                # compute vertical positions
                cci.y += cci.falling_speed
                cci.erasing_y += cci.erasing_speed
                # if codechunk falls, reset (randomize) it's attributes
                if cci.erasing_y >= MC.MATRIX_END_LINE:
                    # reset y positions
                    cci.y = MC.MATRIX_START_LINE
                    cci.erasing_y = \
                        MC.MATRIX_START_LINE - random.randrange(0, MC.LINES)
                    # randomize colors
                    cci.color = self.color_table[
                        compute_color(self.head_prob_table)
                    ]
                    cci.trail_color = cci.color
                    # randomize falling and erasing speeds
                    cci.falling_speed = random.randrange(
                        MC.FALLING_MINSPEED, MC.FALLING_MAXSPEED
                    ) * 0.01
                    cci.erasing_speed = cci.falling_speed - 0.20
                    cci.head_length = random.randrange(2, MC.HEAD_MAXLEN)

            # sync. actual screen with previous drawing methods
            self.scr.refresh()
            threading._sleep(self.sleep_time)

class Main:

    """Main program class."""

    def __init__ (self):
        """Default constructor."""
        random.seed()
        self.mw = begin_gui_mode()
        init_pairs()
        self.run()


    def run (self):
        """Create working thread and wait for keypress."""
        thr = Thr(self.mw, 0.03)
        self.mw.getch()
        thr.stop_this_thread = True
        thr.join()
        self.quit()


    def quit (self):
        """Safely finish app."""
        end_gui_mode(self.mw)

# run the program!
if __name__ == "__main__":
    Main()
