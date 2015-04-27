#!/usr/bin/env python

import os
import time
import datetime
import socket
from collections import OrderedDict
import pygame
from pygame.locals import QUIT

from fontmgr import FontManager
from timemachine import RapidTimeGetter, TimeGetter, TimeMachine

from pims.utils.pimsdateutil import unix2dtm

# some constants
SLEEP = 0.5           # seconds between event loop updates
VERTOFFSET = 240      # vertical offset between gray rect bars
SCREEN_PCT =  90      # % screen width/height that window occupies
FONTSIZE = 145
COLORS = {
    'white':  (255, 255, 255),
    'yellow': (255, 255,  50),
    'red':    (250,   0,   0),
    'gray':   ( 64,  64,  64),
    'black':  (  0,   0,   0),
}

# this centers window both horiz and vert
# ...but this gets changed in run function
os.environ['SDL_VIDEO_CENTERED'] = '1'

# run big timestamp app mainly for ops support
def run(time_machines):
    """run big timestamp app mainly for ops support"""

    # FIXME with better handling of inputs (type check and gracefully allow 3 or less)
    if len(time_machines) != 3:
        raise Exception('expected exactly 3 timemachine objects as input')

    disp_host = socket.gethostname()

    pygame.init()

    # set display mode width and height
    infoObject = pygame.display.Info()
    if disp_host == 'butters':
        wden, hden = 0.9, 2
        xwin, ywin = 0, 100       
    elif disp_host == 'jimmy':
        wden, hden = 1.8, 1
        xwin, ywin = 0, 0
    else:
        wden, hden = 1, 1
        xwin, ywin = 0, 0
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (xwin, ywin)
    WIDTHWIN  = int(SCREEN_PCT * infoObject.current_w / 100 / wden) # divide by 2 for double-wide displays
    HEIGHTWIN = int(SCREEN_PCT * infoObject.current_h / 100 / hden) # divide by 2 for double-high displays
    pygame.display.set_mode((WIDTHWIN, HEIGHTWIN))
    pygame.display.set_caption('bigtime')

    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    # a font of None means to use the default font
    font_mgr = FontManager((
        (None, 24), (None, 48), (None, FONTSIZE),
        ('arial', 24),
        ('arial', 48),
        ('arial', FONTSIZE)
    ))

    # event loop
    running = True
    while running:
        clock.tick(30) # run at 30 fps
        screen.fill((0, 0, 0))

        rect = pygame.Rect(10, 100, WIDTHWIN-20, 65)

        # host system clock gray text in black rect
        txt = 'ignore this line, it is just the system clock of %s %s' % (disp_host, datetime.datetime.now().strftime('%H:%M:%S'))
        pygame.draw.rect(screen, COLORS['black'], rect)
        font_mgr.Draw(screen, 'arial', 24, txt, rect, COLORS['gray'], 'right', 'center', True)
        rect.top += VERTOFFSET / 4

        # spare gray text in gray rect
        txt = 'unused spare gray text inside gray bar'
        pygame.draw.rect(screen, COLORS['gray'], rect)
        font_mgr.Draw(screen, 'arial', 24, txt, rect, COLORS['gray'], 'right', 'center', True)
        rect.top += VERTOFFSET / 1.5

        for tm in time_machines:
            tm.update()
            utime = tm.time
            color = tm.color
            label = tm.prefix + ' ' + tm.time_getter.table.rstrip('rt')
            if utime is None:
                timestr = 'doy/hh:mm:ss'
            else:
                timestr = unix2dtm(utime).strftime('%j/%H:%M:%S')
            txt = '%s %s' % (label, timestr)
            pygame.draw.rect(screen, COLORS['black'], rect)
            font_mgr.Draw(screen, 'arial', FONTSIZE, txt, rect, COLORS[color], 'right', 'center', True)
            rect.top += VERTOFFSET

        pygame.display.update()

        if QUIT in [event.type for event in pygame.event.get()]:
            running = False

        time.sleep(SLEEP)

    pygame.quit()

def demo_on_park():

    bigs = [
        #    table  prefix  EDS      db host
        # -----------------------------------
        ('es05rt',   'CIR', 0.9, 'manbearpig'),
        ('es06rt',   'FIR', 0.9, 'manbearpig'),
        ('121f05rt', 'JEM', 0.9, 'manbearpig'),
    ]

    shift = 0
    time_machines = []
    for table, prefix, expected_delta_sec, dbhost in bigs:
        tg = RapidTimeGetter(table, host=dbhost, shift=shift)
        tm = TimeMachine(tg, expected_delta_sec=SLEEP/3)
        tm.prefix = prefix
        time_machines.append(tm)
        shift += 1

    run(time_machines)

if __name__ == '__main__':

    # TODO find true expected delta instead of empirical value
    bigs = [
        #    table  prefix  ExpDeltaSec   db host
        # -------------------------------------------
        ('es05rt',   'CIR', SLEEP/3,  'manbearpig'),
        ('es06rt',   'FIR', SLEEP/3,  'manbearpig'),
        ('121f05rt', 'JEM', SLEEP/3,  'manbearpig'),
    ]

    time_machines = []
    for table, prefix, expected_delta_sec, dbhost in bigs:
        tg = TimeGetter(table, host=dbhost)
        tm = TimeMachine(tg, expected_delta_sec=expected_delta_sec)
        tm.prefix = prefix # TODO pythonic handling of extraneous attributes
        time_machines.append(tm)

    run(time_machines)
