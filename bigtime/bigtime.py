#!/usr/bin/env python

import os
import time
import datetime
import socket
from collections import OrderedDict
import pygame
from pygame.locals import QUIT

from fontmgr import FontManager
from timemachine import RapidTimeGetter, TimeGetter, EeTimeGetter, TimeMachine

from pims.utils.pimsdateutil import unix2dtm

# some constants
SLEEP = 0.7           # seconds between event loop updates
VERTOFFSET = 200      # vertical offset between gray rect bars (default 200)
SCREEN_PCT =  90      # screen width/height that window occupies
FONTSIZE = 145        # bigtime font size (default 145)
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
    if len(time_machines) != 11:
        raise Exception('expected exactly 11 timemachine objects as input')

    disp_host = socket.gethostname()

    pygame.init()

    # set display mode width and height
    infoObject = pygame.display.Info()
    if disp_host == 'butters':
        wden, hden = 0.9, 0.9
        xwin, ywin = 0, 0       
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

    query_list = [ tm.time_getter.table for tm in time_machines ]

    # event loop
    running = True
    while running:
        clock.tick(30) # run at 30 fps
        screen.fill((0, 0, 0))

        rect = pygame.Rect(10, 100, WIDTHWIN-20, 65)

        # host system clock gray text in black rect
        host_now = datetime.datetime.now()
        txt = 'ignore this line, it is just the system clock of %s %s' % (disp_host, host_now.strftime('%H:%M:%S'))
        pygame.draw.rect(screen, COLORS['black'], rect)
        font_mgr.Draw(screen, 'arial', 24, txt, rect, COLORS['gray'], 'right', 'center', True)
        rect.top += VERTOFFSET / 4

        # use logging when host_now.second is zero as trigger to overwrite plots/user/sams/status/sensortimes.txt
        f = None
        if host_now.second == 0:
            f = open('/misc/yoda/www/plots/user/sams/status/sensortimes.txt', 'w')
            f.write('%s %s host' % (host_now.strftime('%Y-%m-%d'), disp_host))
            f.write('\n' + '-' * 44)
            f.write('\nbegin')
            f.write('\n%s %s host' % (host_now.strftime('%Y:%j:%H:%M:%S'), disp_host))
            
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
                logstr = 'yyyy:ddd:hh:mm:ss'
            else:
                dtm = unix2dtm(utime)
                timestr = dtm.strftime('%j/%H:%M:%S')
                logstr = dtm.strftime('%Y:%j:%H:%M:%S')
            txt = '%s %s' % (label, timestr)
            
            if not tm.prefix.startswith('122'):
                pygame.draw.rect(screen, COLORS['black'], rect)
                font_mgr.Draw(screen, 'arial', FONTSIZE, txt, rect, COLORS[color], 'right', 'center', True)
                rect.top += VERTOFFSET

#2015-06-02 host_jimmy
#--------------------------------------------
#begin
#2015:153:12:17:00 host_jimmy
#yyyy:ddd:hh:mm:ss es03rt MSG
#yyyy:ddd:hh:mm:ss es05rt CIR
#2015:149:23:45:02 es06rt FIR
#2015:153:12:17:34 121f02rt 
#2015:153:12:17:34 121f03rt 
#2015:153:12:17:34 121f04rt 
#2015:153:12:17:34 121f05rt 
#2015:153:12:17:34 121f08rt 
#2015:153:12:17:34 ee_packet 122-f02
#2015:153:12:17:33 ee_packet 122-f03
#2015:153:12:17:33 ee_packet 122-f04
#end
            
            if f:
                if not tm.prefix.startswith('122'):
                    msg = '\n%s %s %s' % (logstr, tm.time_getter.table, tm.prefix)
                else:
                    msg = '\n%s %s %s' % (logstr, tm.prefix, tm.time_getter.table)
                f.write(msg)

        if f:
            f.write('\nend')
            f.close()
        
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
        #    table  prefix  ExpDeltaSec   db host        time getter
        # -----------------------------------------------------------
        ('es03rt',    'MSG',     SLEEP/6,  'manbearpig',  TimeGetter),
        ('es05rt',    'CIR',     SLEEP/6,  'manbearpig',  TimeGetter),
        ('es06rt',    'FIR',     SLEEP/6,  'manbearpig',  TimeGetter),
        ('121f02rt',  'SE',      SLEEP/6,  'manbearpig',  TimeGetter),
        ('121f03rt',  'SE',      SLEEP/6,  'manbearpig',  TimeGetter),
        ('121f04rt',  'SE',      SLEEP/6,  'manbearpig',  TimeGetter),
        ('121f05rt',  'SE',      SLEEP/6,  'manbearpig',  TimeGetter),
        ('121f08rt',  'SE',      SLEEP/6,  'manbearpig',  TimeGetter),
        ('ee_packet', '122-f02', SLEEP/6,  'yoda',        EeTimeGetter),
        ('ee_packet', '122-f03', SLEEP/6,  'yoda',        EeTimeGetter),
        ('ee_packet', '122-f04', SLEEP/6,  'yoda',        EeTimeGetter),
    ]

    time_machines = []
    for table, prefix, expected_delta_sec, dbhost, tgetfun in bigs:
        if prefix.startswith('122'):
            tg = tgetfun(table, host=dbhost, ee_id=prefix)
        else:
            tg = tgetfun(table, host=dbhost)
        tm = TimeMachine(tg, expected_delta_sec=expected_delta_sec)
        tm.prefix = prefix # TODO pythonic handling of extraneous attributes
        time_machines.append(tm)

    run(time_machines)
