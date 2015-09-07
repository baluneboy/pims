#!/usr/bin/env python

import os
import time
import datetime
import socket
from collections import OrderedDict
import pygame
from pygame.locals import QUIT
import pandas as pd

from fontmgr import FontManager
from timemachine import RapidTimeGetter, TimeGetter, EeTimeGetter, KuTimeGetter, HirapTimeGetter, TimeMachine

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

FORMATTERS = {
    'GMT':    lambda x: '%17s' % x,
    'Device': lambda x: '%8s' % x,
    'Type':   lambda x: '%4s'  % x,    
}

#FF0000 is RED
#000000 is BLACK
#FFFFFF is WHITE
HEADER = '''
<html>
    <head>
        <title>
            SAMS Device Times
        </title>
        <style>
            .okay tbody tr { background-color: #FFFFFF; color: #000000; white-space: pre; font-family: monospace; font-size: 14px; }
            .olds tbody tr { background-color: #FFFFFF; color: #FF0000; white-space: pre; font-family: monospace; font-size: 14px; }
        </style>
    </head>
    <body>
'''

FOOTER = '''
    </body>
</html>
'''

# this centers window both horiz and vert
# ...but this gets changed in run function
os.environ['SDL_VIDEO_CENTERED'] = '1'

# run big timestamp app mainly for ops support
def run(time_machines):
    """run big timestamp app mainly for ops support"""

    # FIXME with better handling of inputs (type check and gracefully allow 3 or less)
    if len(time_machines) != 14:
        raise Exception('expected exactly 14 timemachine objects as input')

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

        # when host_now.second is zero this triggers overwrite plots/user/sams/status/sensortimes.txt and .html file too
        f = None
        html_rows = []
        dict_row = {}
        if host_now.second == 0:
            txt_file = '/misc/yoda/www/plots/user/sams/status/sensortimes.txt'
            htm_file = txt_file.replace('.txt', '.html')
            
            f = open(txt_file, 'w')
            f.write('%s %s host' % (host_now.strftime('%Y-%m-%d'), disp_host))
            f.write('\n' + '-' * 38)
            f.write('\nbegin')
            f.write('\n%s %s HOST' % (host_now.strftime('%Y:%j:%H:%M:%S'), disp_host))
            
            dict_row['GMT'] = host_now.strftime('%Y:%j:%H:%M:%S')
            dict_row['Device'] = disp_host
            dict_row['Type'] = 'HOST'
            html_rows.append(dict_row)
            
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
            
            if tm.prefix.startswith('122') or tm.prefix.startswith('Ku'):
                pass
            else:
                pygame.draw.rect(screen, COLORS['black'], rect)
                font_mgr.Draw(screen, 'arial', FONTSIZE, txt, rect, COLORS[color], 'right', 'center', True)
                rect.top += VERTOFFSET
            
            if f:
                dict_row = {}
                dict_row['GMT'] = logstr
                if tm.prefix.startswith('122') or tm.prefix.startswith('Ku'):
                    devi, dtab = tm.time_getter.table.split('_')[0:2]
                    msg = '\n%s %s %s' % (logstr, tm.prefix, devi.upper())
                    dict_row['Device'] = tm.prefix
                    dict_row['Type'] = devi.upper()                
                else:
                    msg = '\n%s %s %s' % (logstr, tm.time_getter.table, tm.prefix)
                    dict_row['Device'] = tm.time_getter.table
                    dict_row['Type'] = tm.prefix                       
                f.write(msg)
                html_rows.append(dict_row)

        if f:
            f.write('\nend')
            f.close()

            # now we write html file
            h = open(htm_file, 'w')

            # write HTML header
            h.write(HEADER)
            
            # get html_rows into dataframe
            df = pd.DataFrame(html_rows)
            
            # order columns left-to-right
            df = df[ ['GMT', 'Device', 'Type'] ]
            
            # sort rows by GMT descending
            df = df.sort( ['GMT'], ascending = [False] )
            
            # write 2 tables and footer
            to_html(df, h) # this writes 2 tables
            h.write(FOOTER)
            h.close()
        
        pygame.display.update()

        if QUIT in [event.type for event in pygame.event.get()]:
            running = False

        time.sleep(SLEEP)

    pygame.quit()

def to_html(df, h):
    df_host = df[ df['Type'] == 'HOST' ]
    host_gmt = df_host['GMT'].values[0]
    df_okay = df[ df['GMT'] >= host_gmt ]
    df_olds = df[ df['GMT'] < host_gmt ]
    h.write( df_okay.to_html(classes='okay', index=False, formatters=FORMATTERS) )
    # FIXME need to account for empty dataframe possibility for df_olds
    h.write( df_olds.to_html(classes='olds', index=False, formatters=FORMATTERS, header=False) )

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
        ('gse_packet',   'Ku_AOS',  SLEEP/6,  'yoda',        KuTimeGetter),        
        ('ee_packet_rt', '122-f02', SLEEP/6,  'yoda',        EeTimeGetter),
        ('ee_packet_rt', '122-f03', SLEEP/6,  'yoda',        EeTimeGetter),
        ('ee_packet_rt', '122-f04', SLEEP/6,  'yoda',        EeTimeGetter),
        ('es03rt',       'MSG',     SLEEP/6,  'chef',        TimeGetter),
        ('es05rt',       'CIR',     SLEEP/6,  'manbearpig',  TimeGetter),
        ('es06rt',       'FIR',     SLEEP/6,  'manbearpig',  TimeGetter),
        ('121f02rt',     'SE',      SLEEP/6,  'manbearpig',  TimeGetter),
        ('121f03rt',     'SE',      SLEEP/6,  'manbearpig',  TimeGetter),
        ('121f04rt',     'SE',      SLEEP/6,  'manbearpig',  TimeGetter),
        ('121f05rt',     'SE',      SLEEP/6,  'manbearpig',  TimeGetter),
        ('121f08rt',     'SE',      SLEEP/6,  'manbearpig',  TimeGetter),
        ('hirap',        'MAM',     SLEEP/6,  'towelie',     HirapTimeGetter),
        ('oss',          'MAM',     SLEEP/6,  'stan',        HirapTimeGetter),
        #('xx00rt',       'XXX',     SLEEP/6,  'chef',        TimeGetter),        
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
