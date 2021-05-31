import sys
import pygame
import pygame.font
from operator import itemgetter
import datetime
import socket


# define font constants
FONT_STR, FONT_SIZE, FONT_SIZE_SMALL = "ubuntumono, bold", 132, 72


def init_display(title_str):
    """return tuple of (screen_width, screen_height, window_object) from initialization and set title bar string"""
    pygame.init()
    pygame.display.set_caption(title_str)
    info_object = pygame.display.Info()
    screen_w, screen_h = info_object.current_w, info_object.current_h
    win = pygame.display.set_mode((info_object.current_w, info_object.current_h), pygame.RESIZABLE)
    return screen_w, screen_h, win


def get_max_text_width_height(txt_lines, font_obj):
    """return tuple of (max_text_width, common_text_height) from lines of text to be rendered"""
    wh = [font_obj.size(s) for s in txt_lines]
    width = max(wh, key=itemgetter(0))[0]  # width is max from first element of list of text (width, height) tuples
    height = wh[0][1]  # assume height is same for all lines
    return width, height


def blit_sensor_text(surface, long_text, pos, font_obj, color=pygame.Color('white')):
    """FIXME - Can we get rid of this unused routine?"""
    words = [word.split(' ') for word in long_text.splitlines()]  # 2D array where each row is a list of words.
    space = font_obj.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    word_width, word_height = 0, 0
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font_obj.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.


def main(title_str):
    """do some setup and run main loop for pygame display"""
    # init display and get screen width and height, plus hostname and pygame clock
    screen_width, screen_height, window = init_display(title_str)
    bar_width = screen_width - 80  # width of subtle rectangle between timestamp lines
    host_name = socket.gethostname()
    clock = pygame.time.Clock()

    # get font properties
    font = pygame.font.SysFont(FONT_STR, FONT_SIZE)
    font_small = pygame.font.SysFont(FONT_STR, FONT_SIZE_SMALL)

    # inner loop builds (nominally) 5 lines of text to be displayed
    prefixes = [
        'MSRR es18',
        'MSG es09',
        'ER3 121f02',
        'ER2 121f03',
        'ER7 121f04',
    ]
    lines = [s + ' GMT 000/00:00:00' for s in prefixes]

    # get max text width and common text height from lines of text
    text_width, text_height = get_max_text_width_height(lines, font)

    # get right-alignment based on text_width, which is derived from widest text among lines of text
    text_right = window.get_rect().centerx + text_width//2

    # compute height of blank lines based on: screen_height, text_height and len(lines)
    unused_height = screen_height - (text_height * len(lines))
    num_blank_lines = len(lines) + 1  # plus one reserves room at bottom for subtle font local/host time
    height_blank_line = unused_height // num_blank_lines

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        window.fill(0)

        y_pos = 0
        for prefix in prefixes:
            # FIXME this next line needs MySQL query of various hosts (i.e. "time getter")
            text_str = prefix + ' GMT 888/' + datetime.datetime.now().strftime('%H:%M:%S')
            text = font.render(text_str, True, (255, 0, 0))
            window.blit(text, text.get_rect(top=y_pos, right=text_right))
            pygame.draw.rect(window, (0, 0, 11), (20, y_pos + text_height, bar_width, height_blank_line))
            y_pos += text_height + height_blank_line

        # put local hostname and time at bottom in hard-to-see font/color
        text_str = 'ignore this line: ' + host_name + ' GMT 888/' + datetime.datetime.now().strftime('%H:%M:%S')
        text = font_small.render(text_str, True, (9, 9, 5))
        window.blit(text, text.get_rect(top=y_pos-height_blank_line, right=text_right))
        pygame.display.flip()

    pygame.quit()
    sys.exit("bigtime exiting")


if __name__ == '__main__':
    title = sys.argv[1]
    main(title)
