import pygame
from Utils import *
from Parser import Parser

class MapViewer(object):
  def __init__(self):
    self._SCREENW=256
    self._SCREENH=176
    
    self._zoom = 2
    
  def setzoom(self, val):
    self._zoom = val
    size = width, height = self._SCREENW*self._zoom, self._SCREENH*self._zoom
    self._screen = pygame.display.set_mode(size)
    self._render()
    
  def _getzoom(self, surf):
    return pygame.transform.scale(surf, (surf.get_width()*self._zoom, surf.get_height()*self._zoom))
    
  def main(self, fname):
    pygame.init()
    size = width, height = self._SCREENW*self._zoom, self._SCREENH*self._zoom
    self._screen = pygame.display.set_mode(size)
    p = Parser(fname)
    self._tiles = p.parseTiles()
    
    quit = False
    self._render()
    
    while not quit:
      self._input()
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          quit = True
    pygame.quit()
          
  def _input(self):
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_1]:
      self.setzoom(1)
    if keys[pygame.K_2]:
      self.setzoom(2)
    if keys[pygame.K_3]:
      self.setzoom(3)
    if keys[pygame.K_4]:
      self.setzoom(4)
      
  def _render(self):
    self._screen.fill((0,0,0))
    for tile in self._tiles:
      self._screen.blit(self._getzoom(tile.img), (tile.x*self._zoom, tile.y*self._zoom))
    pygame.display.flip()
      
if __name__ == '__main__':
  from os import listdir
  from os.path import isfile, join
  p = mapres('')
  maps = [f for f in listdir(p) if isfile(join(p,f)) and f.endswith('.map')]
  for i in range(len(maps)):
    print ('[%s]' % (i)).ljust(5) + maps[i]
    
  mv = MapViewer()
  QUIT = ('x', 'exit', 'q', 'quit')
  quit = False
  while not quit:
    valid = False
    while not valid:
      rinp = raw_input("selection? ")
      inp = -1
      try:
        inp = int(rinp)
        if inp in range(0,len(maps)):
          valid = True
      except ValueError as e:
        if rinp in QUIT:
          inp = rinp
          valid = True
        else:
          print 'Could not convert to integer'
        
    if inp in QUIT:
      quit = True
    else:
      mv.main(mapres(maps[inp]))