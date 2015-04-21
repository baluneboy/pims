#!/usr/bin/env python

import os
import time
import datetime
import pygame
from pygame.locals import QUIT

from fontmgr import FontManager
from onerowquery import query_onerow_unixtime

from pims.utils.pimsdateutil import unix2dtm

# some constants
VERTOFFSET = 220 # vertical offset between GRAY rect bars
SCREEN_PCT = 90 # % screen width/height that window occupies
FONTSIZE = 150
WHITE = (255, 255, 255)
RED = (250, 0, 0)
GRAY = (64, 64, 64)
BLACK = (0, 0, 0)

# this centers window both horiz and vert
os.environ['SDL_VIDEO_CENTERED'] = '1'

# run large timestamp app mainly for ops support
def run(host):
    """run large timestamp app mainly for ops support"""
    
    pygame.init()
    
    # set display mode width and height
    infoObject = pygame.display.Info()
    if host == 'butters':
        wden, hden = 1, 2
    elif host == 'jimmy':
        wden, hden = 2, 1
    else:
        wden, hden = 1, 1
    WIDTHWIN = SCREEN_PCT * infoObject.current_w / 100 / wden  # divide by 2 for double-wide displays
    HEIGHTWIN = SCREEN_PCT * infoObject.current_h / 100 / hden # divide by 2 for double-high displays
    pygame.display.set_mode((WIDTHWIN, HEIGHTWIN))
    
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
    
        font_mgr.Draw(screen, None, 48, 'Default font, 48', (0, 50), GRAY)
        font_mgr.Draw(screen, None, 24, 'Default font, 24', (0, 0), GRAY)
    
        rect = pygame.Rect(10, 100, WIDTHWIN-20, 65)
        
        pygame.draw.rect(screen, GRAY, rect)
        font_mgr.Draw(screen, 'arial', 24, 'Arial 24 top left', rect, GRAY, 'left', 'top')
        rect.top += VERTOFFSET / 2
    
        table = 'es05rt'
        utime = query_onerow_unixtime(table)
        if not utime:
            txt = 'CIR %s  %s' % (table.rstrip('rt'), 'HH:MM:SS')
            font_color = RED
        else:
            txt = 'CIR %s  %s' % (table.rstrip('rt'), unix2dtm(utime).strftime('%H:%M:%S'))
            font_color = WHITE
        pygame.draw.rect(screen, BLACK, rect)    
        font_mgr.Draw(screen, 'arial', FONTSIZE, txt, rect, font_color, 'right', 'center', True)
        rect.top += VERTOFFSET
        
        table = 'es06rt'
        utime = query_onerow_unixtime(table)
        if not utime:
            txt = 'FIR %s  %s' % (table.rstrip('rt'), 'HH:MM:SS')
            font_color = RED            
        else:
            txt = 'FIR %s  %s' % (table.rstrip('rt'), unix2dtm(utime).strftime('%H:%M:%S'))
            font_color = WHITE            
        pygame.draw.rect(screen, BLACK, rect)    
        font_mgr.Draw(screen, 'arial', FONTSIZE, txt, rect, font_color, 'right', 'center', True)
        rect.top += VERTOFFSET
    
        utime = query_onerow_unixtime('121f05rt')
        txt = 'JEM 121f05  %s' % unix2dtm(utime).strftime('%H:%M:%S')
        pygame.draw.rect(screen, BLACK, rect)
        font_mgr.Draw(screen, 'arial', FONTSIZE, txt, rect, WHITE, 'right', 'center', True)
        rect.top += VERTOFFSET
    
        pygame.display.update()
        
        if QUIT in [event.type for event in pygame.event.get()]:
            running = False
        
        time.sleep(0.25)
    
    pygame.quit()

if __name__ == '__main__':
    import socket
    host = socket.gethostname()
    run(host)
