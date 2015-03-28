#!/usr/bin/env python

#Charlie Harrison
#Jan 22, 2011
#Game Of Life
#the life automaton with some optimizations (nothing huge)

import sys
import pygame
from pygame.locals import *

def update(screen, m ,ons, size, dimx, dimy):
    new_m = [[0 for i in xrange(dimy)] for j in xrange(dimx)]
    more_ons = []
    for x,y in ons:
        on_neighbors = 0#number of neighbors to the current cell that are on
        for i in xrange(x-1,x+2):#(i,j) = the adjacent cells to the one we're checking
            for j in xrange(y-1,y+2):
                if (x,y) != (i,j):
                    #makes the cell cycle through to opposite edge
                    i%=dimx
                    j%=dimy

                    #if the cell is ON, we increase the number of on neighbors
                    if m[i][j] == 1: on_neighbors +=1
                    elif new_m[i][j] != 1:#off cell that hasn't been checked
                        n = 0#number of cells adjacent to the adjacent OFF cell
                        for p in xrange(i-1,i+2):
                            for q in xrange(j-1,j+2):
                                if (i,j) != (p,q):

                                    p%=dimx
                                    q%=dimy
                                    try:
                                        if m[p][q] == 1: n+=1
                                    except: print p,q, (dimx,dimy)
                        if n == 3:#if the off cell has 3 neighbors, TURN ON!
                            more_ons.append((i,j))
                            new_m[i][j] = 1
                            pygame.draw.rect(screen,(250,0,0),(i*size,j*size,size,size))

        if not(on_neighbors == 2 or on_neighbors == 3):
            new_m[x][y] = 0
            pygame.draw.rect(screen,(0,0,0),(x*size,y*size,size,size))
        else:
            more_ons.append((x,y))
            new_m[x][y] = 1
            pygame.draw.rect(screen,(250,0,0),(x*size,y*size,size,size))

    return new_m,more_ons


def main(rdimx,rdimy,size):
    pygame.init()
    try: import psyco; psyco.full()
    except: "Psyco module not found: will run a tad slower"
    rdim = (rdimx,rdimy)
    dimx,dimy = (rdimx/size,rdimy/size)
    mappy = [[0 for y in xrange(dimy)] for x in xrange(dimx)]
    ons = []
    screen = pygame.display.set_mode(rdim)

    paused = True
    moused = False
    deleting = False

    while True:
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE: pygame.quit();  sys.exit()
                elif e.key == K_p: paused = not paused
                elif e.key == K_d: deleting = True
                elif e.key == K_g:
                    screen.fill((0,0,0))
                    size +=1
                    ons = []
                    ndimx,ndimy = (rdimx/size,rdimy/size)
                    m = [[0 for y in xrange(ndimy)] for x in xrange(ndimx)]
                    for x in xrange(ndimx):
                        for y in xrange(ndimy):
                            if mappy[x][y] == 1:
                                m[x][y] = 1
                                ons.append((x,y))
                                pygame.draw.rect(screen,(250,0,0),(x*size,y*size,size,size))
                    mappy = [m[i][:] for i in xrange(ndimx)]
                    dimx,dimy = ndimx,ndimy

                elif e.key == K_t:
                    screen.fill((0,0,0))
                    size -=1
                    ons = []
                    ndimx,ndimy = (rdimx/size,rdimy/size)
                    m = [[0 for y in xrange(ndimy)] for x in xrange(ndimx)]
                    for x in xrange(dimx):
                        for y in xrange(dimy):
                            if mappy[x][y] == 1:
                                m[x][y] = 1
                                ons.append((x,y))
                                pygame.draw.rect(screen,(250,0,0),(x*size,y*size,size,size))
                    mappy = [m[i][:] for i in xrange(ndimx)]
                    dimx,dimy = ndimx,ndimy
            elif e.type == KEYUP:
                if e.key == K_d: deleting = False
            elif e.type == MOUSEBUTTONDOWN: moused = True
            elif e.type == MOUSEBUTTONUP: moused = False

        if deleting == True:
            mx,my = [pygame.mouse.get_pos()[i]/size for i in range(2)]
            mappy[mx][my] = 0
            if ons.count((mx,my))>0:ons.remove((mx,my))
            pygame.draw.rect(screen,(0,0,0),(mx*size,my*size,size,size))

        if moused == True:#the mouse is pressed down
            mx,my = [pygame.mouse.get_pos()[i]/size for i in range(2)]

            mappy[mx][my] = 1
            if ons.count((mx,my))==0:ons.append((mx,my))
            pygame.draw.rect(screen,(250,0,0),(mx*size,my*size,size,size))

        if paused == False:#PAUSED!!!
            mappy,ons = update(screen,mappy,ons,size, dimx,dimy)
        pygame.display.flip()

if __name__ == "__main__":
    #input = raw_input('input x dimension, y dimension, block size separated by spaces or commas ')
    #l = input.replace(',','').split()
    #try:
    #       dimx = int(l[0])
    #       dimy = int(l[1])
    #       size = int(l[2])
    #except:
    #       print 'INVALID INPUT'
    #       sys.exit()
    #main(dimx,dimy,size)
    main(1500, 1000, 3)
