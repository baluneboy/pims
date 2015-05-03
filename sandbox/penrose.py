import pygame
import sys
import math
import random
from pygame.locals import *

'''
Generate Penrose Tilings, and mazes upon them.

Let's pretend the nontrivial patterns formed by 36 and 72 degree rhombi aren't
patented ('cuz how could you patent something that can be described in nine words?)
The subsitution method I use is detailed at
http://www.math.ubc.ca/~cass/courses/m308-02b/projects/schweber/penrose.html
'''

# Helpful constants. These are found in the ratios of tile lengths.
S = 2*math.cos(36.*math.pi/180.)
T = 2*math.sin(36.*math.pi/180.)
U = 2*math.sin(18.*math.pi/180.)
V = 2*math.cos(18.*math.pi/180.)
R1 = U/(U + 1.0)
R2 = S/(S + 1.0)

RED = pygame.Color(200, 0, 0)
BLUE = pygame.Color(0, 0, 200)
GREEN = pygame.Color(0, 200, 0)
WHITE = pygame.Color(255, 255, 255)
WHITE2 = pygame.Color(200, 200, 250)
WHITE3 = pygame.Color(220, 250, 230)
BLACK = pygame.Color(0, 0, 0)
YELLOW = pygame.Color(255, 255, 0)
GRAY = pygame.Color(150, 150, 150)


# A point is a pair of integers (x, y).

class Kind:
    pass

Kind.NARROW = 0
Kind.WIDE = 1
Kind.NARROW_INVERTED = -1
Kind.WIDE_INVERTED = -2

class Orientation:
    pass

Orientation.LEFT = 0
Orientation.RIGHT = -1

def randomSetChoice(iterable):
    length = len(iterable)
    index = random.randint(0, length - 1)
    for i, elem in enumerate(iterable):
        if i == index:
            return elem

def splitLine(startPoint, endPoint, fraction):
    """Find a point a fraction of the way between startPoint and endPoint."""
    return ((1 - fraction)*startPoint[0] + fraction*endPoint[0],
            (1 - fraction)*startPoint[1] + fraction*endPoint[1])

def center(points):
    x = 0
    y = 0
    for point in points:
        x = x + point[0]
        y = y + point[1]
    return (x/len(points), y/len(points))

class Wall:
    
    def __init__(self, tile1, tile2, startPt, endPt):
        self.tiles = [tile1, tile2]
        self.start = startPt
        self.end = endPt
        
    def getOtherTile(self, tile):
        tile0, tile1 = self.tiles
        if tile == tile0:
            return tile1
        if tile == tile1:
            return tile0
        return None

    def setOtherTile(self, tile, newTile):
        if tile == self.tiles[0]:
            self.tiles[1] = newTile
        if tile == self.tiles[1]:
            self.tiles[0] = newTile
    

class Tile:

    def __init__(self, points, kind, orientation):
        self.points = list(points)
        self.kind = kind
        if kind == Kind.NARROW:
            self.unreachable = [0]
            self.reachable = [1, 2]
        if kind == Kind.WIDE:
            self.unreachable = [0]
            self.reachable = [1, 2]
        self.orientation = orientation
        self.neighbors = [None, None, None]
        self.walls = [None, None, None]
        self.subtiles = []
        self.subpoints = []
        self.center = center(self.points)

    def pressed(self, maze):
        # Mouse button pressed.
        buddy = self.neighbors[0]
        if buddy is not None:
            self.invert(buddy)
            for wall in self.walls:
                maze.destroyedWalls.discard(wall)

    def neighborWall(self, neighbor):
        return self.walls[self.neighborIndex(neighbor)]

    def neighborIndex(self, neighbor):
        for index, tile in enumerate(self.neighbors):
            if tile == neighbor:
                return index
        return None

    def addWall(self, neighbor):
        index = self.neighborIndex(neighbor)
        if self.walls[index] is not None:
            return self.walls[index]
        else:
            return Wall(self, neighbor, self.points[index], self.points[(index + 1) % 3])

    def setWalls(self):
        for index, neighbor in enumerate(self.neighbors):
            if neighbor is not None:
                self.walls[index] = neighbor.addWall(self)

    def reachableNeighbors(self):
        result = set()
        for index in self.reachable:
            if self.neighbors[index] is not None:
                result.add(self.neighbors[index])
        return result

    def unreachableNeighbors(self):
        #??
        if self.kind != Kind.WIDE:
            return set()
        
        result = set()
        for index in self.unreachable:
            result.add(self.neighbors[index])
        return set(filter(lambda x : x is not None, result))

    def splitLine(self, startPt, endPt, fraction, neighbor, subpointIndex):
        """Find the point a fraction of the way along a line.
           But if 'neighbor' has already calculated the point, use its point."""
        if neighbor and neighbor.subpoints:
            return neighbor.subpoints[subpointIndex]
        else:
            return splitLine(startPt, endPt, fraction)

    def invert(self, buddy):
        """This triangle an its neibhor[0] form a rhombus.
           Switch the triangles so that the wall between them is perpendicular to how it was,
           but they still form the same rhombus."""
        points = [self.points[0], self.points[1], self.points[2], buddy.points[2]]
        neighbors = [self.neighbors[1], self.neighbors[2], buddy.neighbors[2], buddy.neighbors[1]]
        walls = [self.walls[1], self.walls[2], buddy.walls[2], buddy.walls[1]]
        sharedWall = self.walls[0]

        sharedWall.start = points[2]
        sharedWall.end = points[3]
        self.points = [points[3], points[2], points[0]]
        buddy.points = [points[3], points[2], points[1]]
        self.walls = [sharedWall, walls[1], walls[2]]
        buddy.walls = [sharedWall, walls[0], walls[3]]
        self.neighbors = [buddy, neighbors[1], neighbors[2]]
        buddy.neighbors = [self, neighbors[0], neighbors[3]]
        if walls[0] is not None: walls[0].tiles = [buddy, neighbors[0]]
        if walls[1] is not None: walls[1].tiles = [self, neighbors[1]]
        if walls[2] is not None: walls[2].tiles = [self, neighbors[2]]
        if walls[3] is not None: walls[3].tiles = [buddy, neighbors[3]]
        if neighbors[0] is not None: neighbors[0].neighbors[neighbors[0].neighborIndex(self)] = buddy
        if neighbors[2] is not None: neighbors[2].neighbors[neighbors[2].neighborIndex(buddy)] = self
        self.kind = ~self.kind
        buddy.kind = ~buddy.kind
        self.center = center(self.points)
        buddy.center = center(buddy.points)
        

    def split(self):
        
        # Subtiles: 0 - tL -> tL, TL -> tR
        #          1 - tL -> TL, TL -> TR
        #          2 - TL -> TL
        # NARROW=t, WIDE=T, LEFT=L, RIGHT=R
        # (see "Triangle substitutions" graphic)
        
        # Subpoints: 0 - new left point in tL
        #               new left point in TL
        #            1 - new bottom point in TL
        # (see "Triangular tiles" graphic)
        if self.kind == Kind.NARROW:
            P = self.points
            Q = self.splitLine(P[0], P[2], R1, self.neighbors[2], 0)
            tile0 = Tile([Q, P[0], P[1]],
                         Kind.NARROW,
                         self.orientation)
            tile1 = Tile([P[1], P[2], Q],
                         Kind.WIDE,
                         self.orientation)
            self.subtiles = [tile0, tile1]
            self.subpoints = [Q]
        
        if self.kind == Kind.WIDE:
            P = self.points
            Q0 = self.splitLine(P[2], P[0], R1, self.neighbors[2], 0)
            Q1 = self.splitLine(P[0], P[1], R2, self.neighbors[0], 1)
            tile0 = Tile([Q0, P[2], Q1],
                         Kind.NARROW,
                         ~self.orientation)
            tile1 = Tile([Q1, P[0], Q0],
                         Kind.WIDE,
                         ~self.orientation)
            tile2 = Tile([P[1], P[2], Q1],
                         Kind.WIDE,
                         self.orientation)
            self.subtiles = [tile0, tile1, tile2]
            self.subpoints = [Q0, Q1]

    def fixNeighbors(self):
        def getSubtile(neighbor, narrowIndex, wideIndex):
            if neighbor and neighbor.subtiles:
                if neighbor.kind == Kind.NARROW:
                    return neighbor.subtiles[narrowIndex]
                if neighbor.kind == Kind.WIDE:
                    return neighbor.subtiles[wideIndex]
            else:
                return None
        
        if self.kind == Kind.NARROW:
            tile0, tile1 = self.subtiles
            N = self.neighbors
            tile0.neighbors = [getSubtile(N[2], 0, 0),
                                getSubtile(N[0], 0, -1),
                                tile1]
            tile1.neighbors = [getSubtile(N[1], 1, 2),
                                getSubtile(N[2], 1, 1),
                                tile0]
        
        if self.kind == Kind.WIDE:
            tile0, tile1, tile2 = self.subtiles
            N = self.neighbors
            tile0.neighbors = [getSubtile(N[2], 0, 0),
                                tile2,
                                tile1]
            tile1.neighbors = [getSubtile(N[0], -1, 1),
                                getSubtile(N[2], 1, 1),
                                tile0]
            tile2.neighbors = [getSubtile(N[1], 1, 2),
                                tile0,
                                getSubtile(N[0], -1, 2)]

    def fixWalls(self):
        for tile in self.subtiles:
            tile.setWalls()


class Tiling:

    def __init__(self, tiles, iterations, outline):
        self.tiles = tiles
        self.outline = outline
        for i in range(iterations):
            self.split()

    def getWalls(self):
        walls = set()
        for tile in self:
            for index, wall in enumerate(tile.walls):
                if index not in tile.reachable and wall is not None:
                    walls.add(wall)
        return walls

    def __iter__(self):
        return self.tiles.__iter__()

    def split(self):
        for tile in self.tiles:
            tile.split()
        for tile in self.tiles:
            tile.fixNeighbors()
        for tile in self.tiles:
            tile.fixWalls()

        newTiles = []
        for tile in self.tiles:
            newTiles.extend(tile.subtiles)
        self.tiles = newTiles


class Maze:

    def __init__(self, tiling, view):
        self.view = view
        self.tiling = tiling
        self.destroyedWalls = set()
        self.continuation = None

    def display(self, tiles, color = WHITE):
        # Display the visited tiles and maze.
        pygame.display.get_surface().fill(color)
        self.view.drawTiles(tiles)
        self.view.drawWalls(self.tiling, self.destroyedWalls, self.tiling.outline)
        pygame.display.flip()
        #pygame.time.wait(250)
        
        # Allow the user to stop the computation.
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

    def invertWalls(self):
        for wall in self.destroyedWalls:
            tile0, tile1 = wall.tiles
            tile0.invert(tile1)
        self.destroyedWalls = set()

    def resetWalls(self):
        for tile in self.tiling:
            if tile.kind < 0:
                tile.invert(tile.neighbors[0])

    def findReachable(self, tiles):
        """Find all tiles reachable from a starting set of tiles."""
        homeland = set()
        frontier = set(tiles)
        while frontier:
            border = set()
            for tile in frontier:
                border.update(tile.reachableNeighbors())
            border.difference_update(frontier, homeland)
            homeland.update(frontier)
            frontier = border
        return homeland

    def findUnreachable(self, reachableTiles):
        """Find all walls of a set of tiles."""
        unreachable = set()
        for tile in reachableTiles:
            for neighbor in tile.unreachableNeighbors():
                if neighbor is not None and neighbor not in reachableTiles:
                    unreachable.add(tile.neighborWall(neighbor))
        return unreachable

    def step(self):
        # Visit all reachable tiles.
        self.visited.update(self.findReachable(self.visited))

        # Display the visited tiles and maze.
        self.display(self.visited, WHITE)

        # Enumerate all unreachable walls.
        self.unreachable = self.findUnreachable(self.visited)

        # Stop if done.
        if not self.unreachable:
            return False

        # Break down a wall.
        wall = randomSetChoice(self.unreachable)
        self.destroyedWalls.add(wall)
        for tile in wall.tiles:
            if tile not in self.visited:
                self.visited.add(tile)

        return bool(self.unreachable)

    def search(self):
        self.destroyedWalls = set()
        self.visited = set([randomSetChoice(self.tiling.tiles)])
        self.unreachable = set()
        while self.step():
            pass

    def generate(self):
        self.resetWalls()
        self.search()
        #self.invertWalls()
        #self.search()

    def update(self):
        if self.continuation is not None:
            self.continuation = self.continuation()


class View:

    lineColor = GRAY
    lineWidth = 1
    wallColor = BLACK
    wallWidth = 3
    background = WHITE
    tileColors = {Kind.NARROW : RED,
                  Kind.WIDE : BLUE,
                  Kind.NARROW_INVERTED : YELLOW,
                  Kind.WIDE_INVERTED : GREEN}

    def __init__(self):
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen = pygame.display.get_surface()

    def draw(self, tiling, showTiles, showWalls, destroyedWalls):
        self.screen.fill(self.background)
        if showTiles:
            self.drawTiles(tiling)
        if showWalls:
            self.drawWalls(tiling, destroyedWalls, tiling.outline)
        pygame.display.flip()

    def drawTiles(self, tiles):
        for tile in tiles:
            self.drawTile(tile)
        for tile in tiles:
            self.outlineTile(tile)

    def drawWalls(self, tiling, destroyedWalls, outline):
        for wall in tiling.getWalls().difference(destroyedWalls):
            self.drawWall(wall, self.wallColor, self.wallWidth)
        #for tile in tiling:
        #    for neighbor in tile.reachableNeighbors():
        #        pygame.draw.line(self.screen, WHITE, tile.center, neighbor.center)
        #for wall in destroyedWalls:
        #    pygame.draw.line(self.screen, WHITE, wall.tiles[0].center, wall.tiles[1].center)
        pygame.draw.lines(self.screen, self.wallColor,
                          True, outline, self.wallWidth)

    def drawTile(self, tile):
        pygame.draw.polygon(self.screen, self.tileColors[tile.kind], tile.points)

    def outlineTile(self, tile):
        pygame.draw.line(self.screen, self.lineColor,
                         tile.points[0], tile.points[2], self.lineWidth)
        pygame.draw.line(self.screen, self.lineColor,
                         tile.points[1], tile.points[2], self.lineWidth)

    def drawWall(self, wall, color, width):
        pygame.draw.line(self.screen, color, wall.start, wall.end, width)


class Controller:

    def __init__(self, view, tiling):
        self.view = view
        self.tiling = tiling
        self.maze = Maze(tiling, view)
        self.showTiling = True
        self.showWalls = True

    def getTile(self, position):
        minDist = None
        closestTile = None
        for tile in self.tiling.tiles:
            dist = (tile.center[0] - position[0])**2 + (tile.center[1] - position[1])**2
            if minDist is None or dist < minDist:
                minDist = dist
                closestTile = tile
        return closestTile

    def process(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_t:
                    self.showTiling = not self.showTiling
                if event.key == pygame.K_m:
                    self.showWalls = not self.showWalls
                if event.key == pygame.K_g:
                    self.maze.generate()
                self.draw()
            if event.type == pygame.MOUSEBUTTONDOWN:
                tile = self.getTile(event.pos)
                tile.pressed(self.maze)
                self.draw()
        return True

    def run(self):
        pygame.init()
        self.draw()
        while self.process(pygame.event.get()):
            pass
        pygame.quit()

    def draw(self):
        self.view.draw(self.tiling, self.showTiling, self.showWalls, self.maze.destroyedWalls)


def main():
    SCALE = 1200
    ITERATIONS = 9

    X = U/2
    Y = V/2
    x = SCALE/50
    y = SCALE/50
    K = SCALE
    points = [(x, y + K*Y), (x + K, y + K*Y), (x + K*(1 + X), y), (x + K*X, y)]
    top = Tile([points[0], points[2], points[3]],
               Kind.WIDE,
               Orientation.LEFT)
    bot = Tile([points[0], points[2], points[1]],
               Kind.WIDE,
               Orientation.RIGHT)
    top.neighbors = [bot, None, None]
    bot.neighbors = [top, None, None]
    top.setWalls()
    bot.setWalls()

    try:
        tiling = Tiling([top, bot], ITERATIONS, points)
        view = View()
        controller = Controller(view, tiling)
        controller.run()
    except:
        pygame.quit()
        raise


if __name__ == '__main__':
    main()