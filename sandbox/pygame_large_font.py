#!/usr/bin/env python

import os
import time
import datetime
import pygame
from pygame.locals import *

_FONT = 'cambria' # undinaru
_FONTSIZE = 186
os.environ['SDL_VIDEO_CENTERED'] = '1'

def main():
    # Initialize screen
    pygame.init()
    screen = pygame.display.set_mode((1500, 1000))
    pygame.display.set_caption('Basic Pygame program')

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    # Display some text
    font = pygame.font.SysFont("monospace", 296)
    text = font.render("Hello There", 1, (255, 0, 10))
    textpos = text.get_rect()
    #textpos.centerx = background.get_rect().centerx
    background.blit(text, textpos)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Event loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

        # Fill background
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((250, 250, 250))

        # Display some text
        font = pygame.font.SysFont(_FONT, _FONTSIZE)
        txt = 'butters    %s' % datetime.datetime.now().strftime('%H:%M:%S')
        text = font.render(txt, 1, (255, 0, 10))
        textpos = text.get_rect()
        background.blit(text, textpos)

        txt = 'CIR es05  %s' % datetime.datetime.now().strftime('%H:%M:%S')
        text = font.render(txt, 1, (255, 0, 10))
        textpos = text.get_rect()
        textpos.centery += _FONTSIZE
        background.blit(text, textpos)

        txt = 'FIR es06  %s' % datetime.datetime.now().strftime('%H:%M:%S')
        text = font.render(txt, 1, (255, 0, 10))
        textpos = text.get_rect()
        textpos.centery += 2 * _FONTSIZE
        background.blit(text, textpos)
        
        # Blit everything to the screen
        screen.blit(background, (0, 0))
        pygame.display.flip()
        time.sleep(1)

    pygame.quit()  # keep this interpreter friendly

if __name__ == '__main__':
    main()
