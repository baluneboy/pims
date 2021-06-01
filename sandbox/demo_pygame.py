# Simple pygame program

# Import and initialize the pygame library
import os
import datetime
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE

pygame.init()

# some constants
SLOPTIME = datetime.timedelta(seconds=20) # GMT slop for timestamp still close enough to HOST's now
SLEEP = 0.7           # seconds between event loop updates
VERTOFFSET = 200      # vertical offset between gray rect bars (default 200)
SCREEN_PCT =  60      # screen width/height that window occupies
FONTSIZE = 145        # bigtime font size (default 145)
COLORS = {
    'white':  (255, 255, 255),
    'yellow': (255, 255,  50),
    'red':    (250,   0,   0),
    'gray':   ( 64,  64,  64),
    'black':  (  0,   0,   0),
}

FORMATTERS = {
    'GMT':    lambda x: '%s' % x,
    'Device': lambda x: '%s' % x,
    'Type':   lambda x: '%s' % x,
}

# set display mode width and height
infoObject = pygame.display.Info()
wden, hden = 0.9, 0.9
xwin, ywin = 5, 25
os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (xwin, ywin)
WIDTHWIN = int(SCREEN_PCT * infoObject.current_w / 100 / wden)  # divide by 2 for double-wide displays
HEIGHTWIN = int(SCREEN_PCT * infoObject.current_h / 100 / hden)  # divide by 2 for double-high displays
screen = pygame.display.set_mode((WIDTHWIN, HEIGHTWIN))
pygame.display.set_caption('bigtime')
clock = pygame.time.Clock()

# a font of None means to use the default font
font = pygame.font.Font('freesansbold.ttf', 32)


# Run until the user asks to quit
running = True
while running:

    # Did the user click the window close button or hit ESC key?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

    clock.tick(30)  # run at 30 fps

    # Fill the background with black
    screen.fill((0, 0, 0))

    rect = pygame.Rect(10, 100, WIDTHWIN-20, 65)

    # create a text surface object,
    # on which text is drawn on it.
    text = font.render('bigtime', True, green, blue)

    # host system clock gray text in black rect
    host_now = datetime.datetime.now()
    txt = 'ignore this line, it is just the system clock of %s %s' % (disp_host, host_now.strftime('%H:%M:%S'))
    pygame.draw.rect(screen, COLORS['black'], rect)
    font_mgr.Draw(screen, 'arial', 24, txt, rect, COLORS['gray'], 'right', 'center', True)
    rect.top += VERTOFFSET / 4

    # # Draw a solid blue circle in the center
    # pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)
    #
    # # Flip the display
    # pygame.display.flip()

# Done! Time to quit.
pygame.quit()
