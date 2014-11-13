import pygame

GRAYSCALE=False

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)
  
def colorReplace(surf, swaps):
  s = surf.copy()
  if not GRAYSCALE:
    pa = pygame.PixelArray(s)
    for swap in swaps:
      src = swap[0]
      dest = swap[1]
      [row.replace(src, dest) for row in pa]
      
  return s
    
def bmpres(fname):
  return 'resources/bitmaps/'+fname
    
def mapres(fname):
  return 'resources/maps/'+fname
    
def defres(fname):
  return 'resources/definitions/'+fname

Direction = enum("UP", "DOWN", "LEFT", "RIGHT")
DIRECTIONS = Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT
