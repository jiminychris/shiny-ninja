import Tile
import pygame
from Utils import *

class Actor(object):
  def __init__(self, x, y, speed, hp, attack, collaabb, wallcollisions=True, sprites=None, atksprites=None, ai=None):
    self._x = x
    self._y = y
    self._maxhp = hp
    self._attack = attack
    self._collaabb = collaabb
    self._hitaabb = collaabb
    self._speed = speed
    self._wallcollisions = wallcollisions
    self._ai = ai
    self._sprites = sprites
    self._atksprites = atksprites
    self.reset()
    if sprites is not None: 
      if Direction.UP not in sprites.keys():
        raise ValueError('Expected at least UP sprite in dict')
      if Direction.DOWN not in sprites.keys():
        self._sprites[Direction.DOWN] = map(lambda s: pygame.transform.flip(s, False, True), sprites[Direction.UP])
      if Direction.LEFT not in sprites.keys():
        self._sprites[Direction.LEFT] = map(lambda s: pygame.transform.rotate(s, 90), sprites[Direction.UP])
      if Direction.RIGHT not in sprites.keys():
        self._sprites[Direction.RIGHT] = map(lambda s: pygame.transform.flip(s, True, False), self._sprites[Direction.LEFT])
    if atksprites is not None:
      if Direction.UP not in atksprites.keys():
        raise ValueError('Expected at least UP sprite in dict')
      if Direction.DOWN not in atksprites.keys():
        self._atksprites[Direction.DOWN] = pygame.transform.flip(atksprites[Direction.UP], False, True)
      if Direction.LEFT not in atksprites.keys():
        self._atksprites[Direction.LEFT] = pygame.transform.rotate(atksprites[Direction.UP], 90)
      if Direction.RIGHT not in atksprites.keys():
        self._atksprites[Direction.RIGHT] = pygame.transform.flip(self._atksprites[Direction.LEFT], True, False)
    
    self.direction = Direction.DOWN
    
  def reset(self):
    self._dx = 0
    self._dy = 0
    self._hp = self._maxhp
    self._atktimer = 0
    self._canAttack = True
    self._frame = 0
    self._anim = 0
    self._lctimer = 0
    self._invtimer = 0
    self._triumphtimer = 0
    self._triumphtimer = 0
    
  def update(self):
    if self._atktimer > 0:
      self._atktimer -= 1
    if self._invtimer > 0:
      self._invtimer -= 1
    if self._lctimer > 0: 
      self._lctimer -= 1
    if self._triumphtimer > 0: 
      self._triumphtimer -= 1
    
  @property
  def collxoffset(self):
    return self._collaabb.x
  @property
  def collyoffset(self):
    return self._collaabb.y
    
  @property
  def hitxoffset(self):
    return self._hitaabb.x
  @property
  def hityoffset(self):
    return self._hitaabb.y
  
  @property
  def wallcollisions(self):
    return self._wallcollisions
    
  def becomeInvincible(self, t):
    self._invtimer = t  
  @property
  def isInvincible(self):
    return self._invtimer != 0
    
  def loseControl(self, t):
    self._lctimer = t  
  @property
  def isControllable(self):
    return not self._lctimer != 0
  
  def stop(self):
    self._dx = 0
    self._dy = 0    
    
  def doAttack(self, t):
    if self._canAttack:
      self._canAttack = False
      os = self.sprite
      self._atktimer = t
      ns = self.sprite
  def releaseAttack(self):
    self._canAttack = True
  @property
  def isAttacking(self):
    return self._atktimer != 0
  @property
  def canAttack(self):
    return self._canAttack
  
  @property
  def hp(self):
    return self._hp
    
  def heal(self, value):
    if value < 0:
      raise ValueError("Expected positive number")
    self._hp += value
    if self._hp > self._maxhp:
      self._hp = self._maxhp
      
  @property
  def attack(self):
    return self._attack
    
  def hurt(self, value):
    if value < 0:
      raise ValueError("Expected positive number")
    self._hp -= value
    if self._hp < 0:
      self._hp = 0
    
  @property
  def maxhp(self):
    return self._maxhp
    
  def raiseMaxHP(self, dhp):
    self._maxhp += dhp
    
    
  @property
  def x(self):
    return self._x
  @x.setter
  def x(self, value):
    self._x = value
    
  @property
  def y(self):
    return self._y
  @y.setter
  def y(self, value):
    self._y = value
    
  @property
  def speed(self):
    return self._speed
    
  @property
  def dx(self):
    return self._dx
  @dx.setter
  def dx(self, value):
    self._dx = value
    
  @property
  def dy(self):
    return self._dy
  @dy.setter
  def dy(self, value):
    self._dy = value
    
  @property
  def ai(self):
    return self._ai
    
  @property
  def collaabb(self):
    return pygame.Rect(self._collaabb.x+self._x, self._collaabb.y+self._y, self._collaabb.w, self._collaabb.h)
        
  @property
  def hitaabb(self):
    return pygame.Rect(self._hitaabb.x+self._x, self._hitaabb.y+self._y, self._hitaabb.w, self._hitaabb.h)
  
  def setaabb(self, aabb):
    self.setcollaabb(aabb)
    self.sethitaabb(aabb)
  def setcollaabb(self, aabb):
    self._collaabb = aabb  
  def sethitaabb(self, aabb):
    self._hitaabb = aabb
    
  @property
  def sprite(self):
    if self._triumphtimer and self._triumphsprites is not None:
      sprite = self._triumphsprites[0]
    elif self.isAttacking and self._atksprites is not None:
      sprite = self._atksprites[self.direction]
    else:
      sprite = self._sprites[self.direction][self._anim]
    return sprite
    
  def triumph(self, t):
    self.stop()
    self.loseControl(t)
    self._triumphtimer = t
    
  def addtriumphs(self, triumphsprites):
    self._triumphsprites = triumphsprites
    
  def incframe(self, value=1):
    self._frame += value
    while self._frame > 4: 
      self._frame = 0
      self._anim = (self._anim + 1) % 2
      
    
