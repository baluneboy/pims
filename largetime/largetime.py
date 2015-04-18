#!/usr/bin/env python

import os
import time
import datetime
import pygame
from pygame.locals import QUIT
from fontmgr import FontManager

# some constants
VERTOFFSET = 250 # vertical offset between GRAY rect bars
SCREEN_PCT = 90 # % screen width/height that window occupies
WHITE = (255, 255, 255)
RED = (250, 0, 0)
GRAY = (64, 64, 64)

# this centers window both horiz and vert
os.environ['SDL_VIDEO_CENTERED'] = '1'

# run large timestamp app mainly for FCF Ops support
def run():
    """run large timestamp app mainly for FCF Ops support"""
    
    pygame.init()
    
    # set display mode width and height
    infoObject = pygame.display.Info()
    WIDTHWIN = SCREEN_PCT * infoObject.current_w / 100
    HEIGHTWIN = SCREEN_PCT * infoObject.current_h / 100
    pygame.display.set_mode((WIDTHWIN, HEIGHTWIN))
    
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    # a font of None means to use the default font
    font_mgr = FontManager((
        (None, 24), (None, 48), (None, 172), 
        ('arial', 24),
        ('arial', 48),
        ('arial', 172)
    ))

    # event loop
    RUNNING = True
    while RUNNING:
        clock.tick(30) # run at 30 fps
        screen.fill((0, 0, 0))
    
        font_mgr.Draw(screen, None, 48, 'Default font, 48', (0, 50), WHITE)
        font_mgr.Draw(screen, None, 24, 'Default font, 24', (0, 0), WHITE)
    
        rect = pygame.Rect(10, 100, WIDTHWIN-20, 65)
        
        pygame.draw.rect(screen, GRAY, rect)
        font_mgr.Draw(screen, 'arial', 24, 'Arial 24 top left', rect, WHITE, 'left', 'top')
        rect.top += 75
    
        pygame.draw.rect(screen, GRAY, rect)
        font_mgr.Draw(screen, 'arial', 24, 'Arial 24 centered', rect, WHITE, 'center', 'center')
        rect.top += 75
    
        pygame.draw.rect(screen, GRAY, rect)
        font_mgr.Draw(screen, 'arial', 24, 'Arial 24 bottom right', rect, WHITE, 'right', 'bottom')
        rect.top += 75
    
        pygame.draw.rect(screen, GRAY, rect)
        font_mgr.Draw(screen, 'arial', 24, 'Arial 24 bottom right, anti-aliased', rect, WHITE, 'right', 'bottom', True)
        rect.top += VERTOFFSET
    
        txt = 'CIR es05  %s' % datetime.datetime.now().strftime('%H:%M:%S')
        if txt.endswith('5'):
            font_color = RED
        else:
            font_color = WHITE
        pygame.draw.rect(screen, GRAY, rect)    
        font_mgr.Draw(screen, 'arial', 172, txt, rect, font_color, 'right', 'center', True)
        rect.top += VERTOFFSET
    
        txt = 'FIR es06  %s' % datetime.datetime.now().strftime('%H:%M:%S')
        pygame.draw.rect(screen, GRAY, rect)
        font_mgr.Draw(screen, 'arial', 172, txt, rect, WHITE, 'right', 'center', True)
        rect.top += 75
    
        pygame.display.update()
        
        if QUIT in [event.type for event in pygame.event.get()]:
            RUNNING = False
        
        time.sleep(0.25)
    
    pygame.quit()

if __name__ == '__main__':
    run()
