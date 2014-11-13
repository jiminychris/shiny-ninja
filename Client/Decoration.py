import pygame

class Decoration(object):
  def __init__(self, x, y, sprites, animtype):
    self._x = x
    self._y = y
    self._frame = 0
    self._anim = 0
    if animtype == "fliph":
      self._sprites = sprites[0], pygame.transform.flip(sprites[0], True, False)
    else:
      self._sprites = sprites
    
  def update(self):
    self._frame += 1
    if self._frame == 4:
      self._frame = 0
      self._anim = (self._anim + 1) % len(self._sprites)
    
  @property
  def x(self): 
    return self._x
  @property
  def y(self): 
    return self._y
    
  @property
  def sprite(self):
    return self._sprites[self._anim]