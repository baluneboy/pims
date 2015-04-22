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
VERTOFFSET = 220 # vertical offset between gray rect bars
SCREEN_PCT =  90 # % screen width/height that window occupies
FONTSIZE = 150
COLORS = {
    'white':  (255, 255, 255),
    'yellow': (255, 255,  50),
    'red':    (250,   0,   0),
    'gray':   ( 64,  64,  64),
    'black':  (  0,   0,   0),
}

# this centers window both horiz and vert
os.environ['SDL_VIDEO_CENTERED'] = '1'

# run big timestamp app mainly for ops support
def run(time_machines):
    """run big timestamp app mainly for ops support"""

    # FIXME with better handling of inputs (type check and gracefully allow 3 or less)
    if len(time_machines) != 3:
        raise Exception('expected 3 timemachine objects as input')

    disp_host = socket.gethostname()

    pygame.init()

    # set display mode width and height
    infoObject = pygame.display.Info()
    if disp_host == 'butters':
        wden, hden = 1, 2
    elif disp_host == 'jimmy':
        wden, hden = 2, 1
    else:
        wden, hden = 1, 1
    WIDTHWIN  = SCREEN_PCT * infoObject.current_w / 100 / wden # divide by 2 for double-wide displays
    HEIGHTWIN = SCREEN_PCT * infoObject.current_h / 100 / hden # divide by 2 for double-high displays
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

        font_mgr.Draw(screen, None, 48, 'Default font, 48', (0, 50), COLORS['gray'])
        font_mgr.Draw(screen, None, 24, 'Default font, 24', (0, 0), COLORS['gray'])

        rect = pygame.Rect(10, 100, WIDTHWIN-20, 65)

        pygame.draw.rect(screen, COLORS['gray'], rect)
        font_mgr.Draw(screen, 'arial', 24, 'Arial 24 top left', rect, COLORS['gray'], 'left', 'top')
        rect.top += VERTOFFSET / 2

        #
        # table (label) >> time_getter
        # utime, textcolor [, rectcolor?] << timemachine(time_getter)
        # timestr << utime
        #

        for tm in time_machines:
            tm.update()
            utime = tm.time
            color = tm.color
            label = tm.prefix + ' ' + tm.time_getter.table.rstrip('rt')
            if utime is None:
                timestr = 'hh:mm:ss'
            else:
                timestr = unix2dtm(utime).strftime('%H:%M:%S')
            txt = '%s  %s' % (label, timestr)
            pygame.draw.rect(screen, COLORS['black'], rect)
            font_mgr.Draw(screen, 'arial', FONTSIZE, txt, rect, COLORS[color], 'right', 'center', True)
            rect.top += VERTOFFSET

        pygame.display.update()

        if QUIT in [event.type for event in pygame.event.get()]:
            running = False

        time.sleep(0.25)

    pygame.quit()

if __name__ == '__main__':

    bigs = [
        #    table  prefix  EDS      db host
        # -----------------------------------
        ('es05rt',   'CIR', 0.9, 'manbearpig'),
        ('es06rt',   'FIR', 0.9, 'manbearpig'),
        ('121f05rt', 'JEM', 0.9, 'manbearpig'),
    ]

    #shift = 0
    time_machines = []
    for table, prefix, expected_delta_sec, dbhost in bigs:
        tg = RapidTimeGetter(table, host=dbhost) #, shift=shift)
        #tg = TimeGetter(table, host=dbhost)
        tm = TimeMachine(tg, expected_delta_sec=expected_delta_sec)
        tm.prefix = prefix
        time_machines.append(tm)
        #shift += 1

    run(time_machines)
