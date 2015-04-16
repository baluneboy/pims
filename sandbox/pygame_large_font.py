import os
import time
import pygame
from pygame.locals import *

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
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                raise SystemExit

        #for f in ['calibri', 'cambria', 'cambriamath', 'kinnari', 'norasi', 'rachana', 'sawasdee', 'ubuntu', 'ubuntumono', 'undinaru', 'ungungseo']: #pygame.font.get_fonts():
        #for f in ['ubuntu', 'ubuntumono', 'undinaru', 'ungungseo']: #pygame.font.get_fonts():
        for f in ['undinaru', 'ubuntumono']:
            print f
            # Fill background
            background = pygame.Surface(screen.get_size())
            background = background.convert()
            background.fill((250, 250, 250))

            # Display some text
            try:
                font = pygame.font.SysFont(f, 196)
                txt = f + ' 12:34:56'
                text = font.render(txt, 1, (255, 0, 10))
                textpos = text.get_rect()
                #textpos.centerx = background.get_rect().centerx
            except:
                font = pygame.font.SysFont("monospace", 196)
                txt = 'not ' + f
                text = font.render(txt, 1, (255, 0, 10))
                textpos = text.get_rect()
                #textpos.centerx = background.get_rect().centerx
            background.blit(text, textpos)

            # Blit everything to the screen
            screen.blit(background, (0, 0))
            pygame.display.flip()
            time.sleep(3)

    pygame.quit()  # Keep this IDLE friendly

if __name__ == '__main__':
    main()
