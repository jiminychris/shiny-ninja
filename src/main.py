import sys
import pygame

from Parser import *
import Tile
import time
from Actor import Actor
from Inventory import Inventory
from Utils import *
from Spritesheet import Spritesheet
from Portal import Portal, PortalType
import random
import Text
  
class Play(object):
  def __init__(self):
    self._cache = []
    self._deathanims = []
    self._debugging = False
    if '-aabbdebug' in sys.argv:
      self._debugging = True
    self._startmap = 'ow8-8.map'
    if '-startm' in sys.argv:
      self._startmap = sys.argv[sys.argv.index('-startm')+1]
    self._starthearts = 3
    if '-hearts' in sys.argv:
      self._starthearts = int(sys.argv[sys.argv.index('-hearts')+1])
    random.seed()
    self._SCREENW=256
    self._SCREENH=240
    self._MAPW=256
    self._MAPH=176
    self._OFFSET=self._SCREENH-self._MAPH
    
    self._UBOUND = pygame.Rect(0, 0, self._MAPW, 8)
    self._RBOUND = pygame.Rect(self._MAPW, 0, 8, self._MAPH)
    self._BBOUND = pygame.Rect(0, self._MAPH, self._MAPW, 8)
    self._LBOUND = pygame.Rect(-8, 0, 8, self._MAPH)
    
    self._TEXTSPEED=4
    
    self._sword = None
    self._haabb = pygame.Rect(0, Tile.HALF, Tile.SIZE, Tile.HALF)
    self._vaabb = pygame.Rect(2, Tile.HALF, Tile.SIZE-4, Tile.HALF)
    self._spelunking = 0
    self._zoning = None
    
    self._zoom = 2
    pygame.init()
    size = width, height = self._SCREENW*self._zoom, self._SCREENH*self._zoom
    self._screen = pygame.display.set_mode(size)
    
    linkpalette = (((0,0,0),(0,0,0)),((128,128,128),(200,76,12)),((192,192,192),(128,208,16)),((255,255,255),(252,152,56)))
    wss = Spritesheet(bmpres('weapons.bmp'))
    self._swordsprite = colorReplace(wss.image_at((0,0,8,16), colorkey=(0,0,0)), linkpalette)
    ssprite = self._swordsprite
    lssprite = pygame.transform.rotate(ssprite,90)
    self._swordsprites = {x:y for x,y in zip(DIRECTIONS, (ssprite, pygame.transform.flip(ssprite,False,True), lssprite, pygame.transform.flip(lssprite,True,False)))}
    self._lifetxt = Text.get('-LIFE-', (216,40,0))
    self._btxt = Text.get('Z')[0]
    self._atxt = Text.get('X')[0]
    
    iss = Spritesheet(bmpres('icons.bmp'))
    heart = iss.image_at((0,0,8,8), colorkey=(0,0,0))
    self._fullheart = colorReplace(heart, (((128,128,128), (216,40,0)),))
    self._halfheart = colorReplace(iss.image_at((8,0,8,8), colorkey=(0,0,0)), (((128,128,128),(216,40,0)),((255,255,255),(255,227,171))))
    self._emptyheart = colorReplace(heart, (((128,128,128),(255,227,171)),))
    
    self._uibox = {}
    self._uibox['ul'] = colorReplace(iss.image_at((0,8,8,8), colorkey=(0,0,0)), (((128,128,128),(0,89,250)),))
    self._uibox['v'] = colorReplace(iss.image_at((8,8,8,8), colorkey=(0,0,0)), (((128,128,128),(0,89,250)),))
    self._uibox['h'] = pygame.transform.rotate(self._uibox['v'], 90)
    self._uibox['ur'] = pygame.transform.flip(self._uibox['ul'], True, False)
    self._uibox['br'] = pygame.transform.flip(self._uibox['ur'], False, True)
    self._uibox['bl'] = pygame.transform.flip(self._uibox['ul'], False, True)
    
    self._uirupee, self._uikey, self._uibomb = iss.images_at(((0,16,8,8), (8,16,8,8), (16,16,8,8)), colorkey=(0,0,0))
    self._uirupee = colorReplace(self._uirupee, (((128,128,128),(255,161,68)),((255,255,255),(255,227,171))))
    self._uikey = colorReplace(self._uikey, (((128,128,128),(255,161,68)),))
    self._uibomb = colorReplace(self._uibomb, (((192,192,192),(0,89,250)),))
    
    
    ss = Spritesheet(bmpres('link.bmp'))
    s = {}
    s[Direction.UP] = [colorReplace(sp, (((0,0,0),(0,0,0)),((128,128,128),(200,76,12)),((192,192,192),(128,208,16)),((255,255,255),(252,152,56)))) for sp in ss.images_at(((16,0,16,16),(16,16,16,16)), colorkey=(0,0,0))]
    s[Direction.DOWN] = [colorReplace(sp, (((0,0,0),(0,0,0)),((128,128,128),(200,76,12)),((192,192,192),(128,208,16)),((255,255,255),(252,152,56)))) for sp in ss.images_at(((0,0,16,16),(0,16,16,16)), colorkey=(0,0,0))]
    s[Direction.LEFT] = [colorReplace(sp, (((0,0,0),(0,0,0)),((128,128,128),(200,76,12)),((192,192,192),(128,208,16)),((255,255,255),(252,152,56)))) for sp in ss.images_at(((32,0,16,16),(32,16,16,16)), colorkey=(0,0,0))]
    atks = {}
    atks[Direction.UP] = colorReplace(ss.image_at((16,32,16,16), colorkey=(0,0,0)), linkpalette)
    atks[Direction.DOWN] = colorReplace(ss.image_at((0,32,16,16), colorkey=(0,0,0)), linkpalette)
    atks[Direction.LEFT] = colorReplace(ss.image_at((32,32,16,16), colorkey=(0,0,0)), linkpalette)
    self._pc = Actor(15*8,11*8,2,self._starthearts*16,8,self._vaabb,True,s,atksprites=atks)
    self._pc.sethitaabb(pygame.Rect(0,0,16,16))
    self._pc.addtriumphs((colorReplace(ss.image_at((48,0,16,16), colorkey=(0,0,0)), linkpalette),colorReplace(ss.image_at((48,16,16,16), colorkey=(0,0,0)), linkpalette)))
    
    self._pcweapons = []
    self._temps = []
    self._startport = Portal(self._startmap, 15*8, 10*8, PortalType.Magic)
    self._start()
    
  def _getHeartCollectible(self):
    return parseCollectible(defres('collectibles.col'), 'heart')
  def _getRupeeCollectible(self):
    return parseCollectible(defres('collectibles.col'), 'rupee')
  def _getBlueRupeeCollectible(self):
    return parseCollectible(defres('collectibles.col'), 'brupee')
    
  def _start(self):
    self._pc.reset()
    self._currentmapname = self._startmap
    self._maps = {}
    self._maphistory = [self._startmap]
    self._inventory = Inventory()
    if '-mkey' in sys.argv:
      self._inventory.acquiremkey()
    if '-sword' in sys.argv:
      self._inventory.changesword(int(sys.argv[sys.argv.index('-sword')+1]))
    self._port(self._startport)
    
    
  @property
  def inventory(self):
    return self._inventory
    
  @property
  def _actors(self):
    return self._monsters + self._pcweapons + [self._pc]
  @property
  def _bounders(self):
    return [actor for actor in self._actors if actor.wallcollisions]
  @property
  def _updaters(self):
    return self._actors+self._decos+self._collectibles
  @property
  def _currentmap(self):
    return self._maps[self._currentmapname]
  @property
  def _tiles(self):
    return self._currentmap.tiles
  @_tiles.setter
  def _tiles(self, value):
    self._currentmap.tiles = value
  @property
  def _monsters(self):
    return self._currentmap.monsters
  @_monsters.setter
  def _monsters(self, value):
    self._currentmap.monsters = value
  @property
  def _decos(self):
    return self._currentmap.decorations
  @property
  def _portals(self):
    return self._currentmap.portals
  @property
  def _textlist(self):
    return self._currentmap.text
  @_textlist.setter
  def _textlist(self, value):
    self._currentmap.textlist = value
  @property
  def _collectibles(self):
    return self._currentmap.collectibles
  @_collectibles.setter
  def _collectibles(self, value):
    self._currentmap.collectibles = value
    
  def _loadmap(self, m):
    p = Parser(m)
    self._currentmapname = m
    if m in self._maps:
      self._maphistory.remove(m)
    else:
      self._maps[m] = p.parse()
      if len(self._maphistory) == 4:
        self._maphistory = self._maphistory[1:]
    self._maphistory.append(m)
    self._maps = {k: v for k, v in self._maps.items() if k in self._maphistory}
    g = globals()
    l = locals()
    self._tiles = [tile if eval(tile.condition) else tile.alt for tile in self._tiles]
    self._maskedTiles = [tile for tile in self._tiles if tile.mask]
    self._unmaskedTiles = [tile for tile in self._tiles if not tile.mask]
    self._collectibles = [coll for coll in self._collectibles if eval(coll.condition,g,l)]
    self._textlist = [text for text in self._textlist if eval(text.condition,g,l)]
    self._texttimer = 0
    self._zonetimer = 0
    self._texttimermax = len(self._textlist)*self._TEXTSPEED
    self._pc.stop()
    self._pc.loseControl(self._texttimermax)
    
  def setzoom(self, val):
    self._zoom = val
    size = width, height = self._SCREENW*self._zoom, self._SCREENH*self._zoom
    self._screen = pygame.display.set_mode(size)
  
  def _attacks(self):
    if self._pc.isAttacking and self._sword is None:
      atk = self._inventory.sword*16
      sprite = {Direction.UP: [self._swordsprite]}
      w=3
      l=11
      if self._pc.direction == Direction.UP:
        x,y,r = self._pc.x+3, self._pc.y-1-l, pygame.Rect(2, 0, w, l)
      elif self._pc.direction == Direction.RIGHT:
        x,y,r = self._pc.x+12, self._pc.y+5, pygame.Rect(5, 3, l, w)
      elif self._pc.direction == Direction.DOWN:
        x,y,r = self._pc.x+5, self._pc.y+12, pygame.Rect(2, 5, w, l)
      else:# self._pc.direction == Direction.LEFT:
        x,y,r = self._pc.x-12, self._pc.y+5, pygame.Rect(0, 3, l, w)
      self._sword = Actor(x,y,0,0,atk,r,False,sprite)
      self._sword.direction = self._pc.direction
      self._pcweapons.append(self._sword)
    elif not self._pc.isAttacking and self._sword is not None:
      self._pcweapons.remove(self._sword)
      self._sword = None  
  
  def _deaths(self):
    if self._pc.hp == 0:
      self._pc.heal(self._pc.maxhp)
      self._start()
    deads = [monster for monster in self._monsters if monster.hp == 0]
    self._monsters = [monster for monster in self._monsters if monster.hp > 0]
    for monster in deads:
      self._deathanims.append(type('DeathAnim', (), {'x': monster.x, 'y': monster.y, 't': 8}))
    
  @property
  def _porting(self):
    return self._spelunking != 0 or self._zoning != None
    
  def _timers(self):
    drops = [d for d in self._deathanims if d.t == 0]
    for d in drops:
      roll = random.randint(1,20)
      if roll > 10 and roll < 15:
        c = self._getHeartCollectible()
      elif roll > 14 and roll < 19:
        c = self._getRupeeCollectible()
      elif roll == 19:
        c = self._getBlueRupeeCollectible()
      elif roll == 20:
        c = None
        #print 'fairy'
      else:
        c = None
      if c is not None:
        c.x = d.x
        c.y = d.y
        self._collectibles.append(c)
    self._deathanims = [d for d in self._deathanims if d > 0]
    for d in self._deathanims:
      d.t -= 1
        
    for temp in self._temps:
      temp[1] -= 1
    self._temps = [[s,t] for [s,t] in self._temps if t > 0]

    if self._zonetimer > 0:
      self._zonetimer -= 1
    else:
      self._zoning = None
    
    if self._texttimer < self._texttimermax:
      self._texttimer += 1
    s = self._spelunking
    if s != 0:
      if self._cavetimer % 3 == 0:
        self._pc.y -= s
      if self._cavetimer > 0:
        self._cavetimer -= 1
        self._pc.incframe()
      else:
        self._spelunking = 0
        if s == -1:
          self._port(self._currentport)
    
  def _update(self):
    self._attacks()
    self._deaths()
    self._timers()
    [updater.update() for updater in self._updaters]
    self._input()
    self._physics()
    
  def _render(self):
    self._screen.fill((0,0,0))
    
    if self._spelunking != 0:
      for tile in [tile for tile in self._tiles if tile.portal is not None]:
        self._screen.blit(self._getzoom(tile.img), ((tile.x)*self._zoom, (tile.y+self._OFFSET)*self._zoom))
      self._screen.blit(self._getzoom(self._pc.sprite), ((self._pc.x)*self._zoom, (self._pc.y+self._OFFSET)*self._zoom))
      for tile in [tile for tile in self._tiles if tile.portal is None]:
        self._screen.blit(self._getzoom(tile.img), ((tile.x)*self._zoom, (tile.y+self._OFFSET)*self._zoom))
      for deco in self._decos:
        self._screen.blit(self._getzoom(deco.sprite), (deco.x*self._zoom, (deco.y+self._OFFSET)*self._zoom))
    elif self._zoning is not None:
      if self._zoning == Direction.UP:
        dxo = 0
        dxn = 0
        dyo = 4*(44-self._zonetimer)
        dyn = -4*(self._zonetimer)
      if self._zoning == Direction.RIGHT:
        dxo = -4*(64-self._zonetimer)
        dxn = 4*self._zonetimer
        dyo = 0
        dyn = 0
      if self._zoning == Direction.DOWN:
        dxo = 0
        dxn = 0
        dyo = -4*(44-self._zonetimer)
        dyn = 4*(self._zonetimer)
      if self._zoning == Direction.LEFT:
        dxo = 4*(64-self._zonetimer)
        dxn = -4*self._zonetimer
        dyo = 0
        dyn = 0
      for tile in self._unmaskedTiles:
        self._screen.blit(self._getzoom(tile.img), ((tile.x+dxn)*self._zoom, (tile.y+dyn+self._OFFSET)*self._zoom))
      for tile in [tile for tile in self._oldmap.tiles if not tile.mask]:
        self._screen.blit(self._getzoom(tile.img), ((tile.x+dxo)*self._zoom, (tile.y+dyo+self._OFFSET)*self._zoom))
      self._screen.blit(self._getzoom(self._pc.sprite), ((self._pc.x)*self._zoom, (self._pc.y+self._OFFSET)*self._zoom))
      for tile in self._maskedTiles:
        self._screen.blit(self._getzoom(tile.img), ((tile.x+dxn)*self._zoom, (tile.y+dyn+self._OFFSET)*self._zoom))
      for tile in [tile for tile in self._oldmap.tiles if tile.mask]:
        self._screen.blit(self._getzoom(tile.img), ((tile.x+dxo)*self._zoom, (tile.y+dyo+self._OFFSET)*self._zoom))
    else:
      for tile in self._unmaskedTiles:
        self._screen.blit(self._getzoom(tile.img), ((tile.x)*self._zoom, (tile.y+self._OFFSET)*self._zoom))
      for deco in self._decos:
        self._screen.blit(self._getzoom(deco.sprite), (deco.x*self._zoom, (deco.y+self._OFFSET)*self._zoom))   
      for coll in self._collectibles:
        self._screen.blit(self._getzoom(coll.sprite), (coll.x*self._zoom, (coll.y+self._OFFSET)*self._zoom))   
      for tile in self._textlist[:self._texttimer/self._TEXTSPEED]: 
        self._screen.blit(self._getzoom(tile.img), (tile.x*self._zoom, (tile.y+self._OFFSET)*self._zoom))    
      if self._debugging:
        self._renderaabbdebug()
      for actor in self._actors:
        self._screen.blit(self._getzoom(actor.sprite), ((actor.x)*self._zoom, (actor.y+self._OFFSET)*self._zoom))
      for [s,t] in self._temps:
        self._screen.blit(self._getzoom(s.img), ((s.x)*self._zoom, (s.y+self._OFFSET)*self._zoom))
      for tile in self._maskedTiles:
        self._screen.blit(self._getzoom(tile.img), ((tile.x)*self._zoom, (tile.y+self._OFFSET)*self._zoom))
      
    self._renderui()
    
    pygame.display.flip()

  def _renderaabbdebug(self):
    for aabb in [actor.hitaabb for actor in self._actors]:
      r = self._getzoom(pygame.Surface((aabb.w, aabb.h)))
      r.fill((255,255,0))
      self._screen.blit(r, (aabb.x*self._zoom, (aabb.y+self._OFFSET)*self._zoom))
    for aabb in [actor.collaabb for actor in self._actors]:
      r = self._getzoom(pygame.Surface((aabb.w, aabb.h)))
      r.fill((255,0,255))
      self._screen.blit(r, (aabb.x*self._zoom, (aabb.y+self._OFFSET)*self._zoom))
    for aabb in [coll.aabb for coll in self._collectibles]:
      r = self._getzoom(pygame.Surface((aabb.w, aabb.h)))
      r.fill((255,0,255))
      self._screen.blit(r, (aabb.x*self._zoom, (aabb.y+self._OFFSET)*self._zoom))
  
  
  def _renderui(self):
    black = pygame.Surface((256,64))
    self._screen.blit(self._getzoom(black), (0,0))
    for i in range(len(self._lifetxt)):
      self._screen.blit(self._getzoom(self._lifetxt[i]), ((23+i)*8*self._zoom, 16*self._zoom))
    self._screen.blit(self._getzoom(self._atxt), ((19)*8*self._zoom, 16*self._zoom))
    self._screen.blit(self._getzoom(self._btxt), ((16)*8*self._zoom, 16*self._zoom))
    
    ul = self._getzoom(self._uibox['ul'])
    ur = self._getzoom(self._uibox['ur'])
    br = self._getzoom(self._uibox['br'])
    bl = self._getzoom(self._uibox['bl'])
    v = self._getzoom(self._uibox['v'])
    h = self._getzoom(self._uibox['h'])
    for i in range(2):
      self._screen.blit(ul, ((3*i+15)*8*self._zoom, 2*8*self._zoom))
      self._screen.blit(ur, ((3*i+17)*8*self._zoom, 2*8*self._zoom))
      self._screen.blit(br, ((3*i+17)*8*self._zoom, 5*8*self._zoom))
      self._screen.blit(bl, ((3*i+15)*8*self._zoom, 5*8*self._zoom))
      self._screen.blit(h, ((3*i+16)*8*self._zoom, 5*8*self._zoom))
      for j in range(4):
        self._screen.blit(v, ((3*i+2*(j%2)+15)*8*self._zoom, (j/2+3)*8*self._zoom))
    if self._inventory.sword > 0:
      self._screen.blit(self._getzoom(self._swordsprite), (19*8*self._zoom, 3*8*self._zoom))
    self._screen.blit(self._getzoom(self._uirupee), (11*8*self._zoom, 2*8*self._zoom))
    self._screen.blit(self._getzoom(self._uikey), (11*8*self._zoom, 4*8*self._zoom))
    self._screen.blit(self._getzoom(self._uibomb), (11*8*self._zoom, 5*8*self._zoom))
    rupees = Text.get(('X' if self._inventory.rupees < 100 else '')+str(self._inventory.rupees))
    for i in range(len(rupees)):
      self._screen.blit(self._getzoom(rupees[i]), ((i+12)*8*self._zoom,(2)*8*self._zoom))
    keys = Text.get('X'+self._inventory.keystr)
    for i in range(len(keys)):
      self._screen.blit(self._getzoom(keys[i]), ((i+12)*8*self._zoom,(4)*8*self._zoom))
    bombs = Text.get('X'+str(self._inventory.bombs))
    for i in range(len(bombs)):
      self._screen.blit(self._getzoom(bombs[i]), ((i+12)*8*self._zoom,(5)*8*self._zoom))
    maprect = pygame.Surface((8*8, 8*4))
    maprect.fill((100,100,100))
    self._screen.blit(self._getzoom(maprect), (2*8*self._zoom, 2*8*self._zoom))    
        
    for i in range(self._pc.maxhp/16):
      heart = self._fullheart
      if self._pc.hp > i*16 and self._pc.hp <= i*16+8:
        heart = self._halfheart
      elif self._pc.hp <= i*16:
        heart = self._emptyheart
      self._screen.blit(self._getzoom(heart), ((22+i%8)*8*self._zoom, (6-i/8)*8*self._zoom))
      
  def _getzoom(self, surf):
    return pygame.transform.scale(surf, (surf.get_width()*self._zoom, surf.get_height()*self._zoom))
  
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
    
    if self._pc.isControllable:
      dx = 0
      dy = 0
      
      if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
        self._pc.incframe()

      if keys[pygame.K_DOWN] or keys[pygame.K_UP]:
        if keys[pygame.K_DOWN]:
          if self._pc.x % 8 == 0:
            dy += self._pc.speed
            self._pc.direction = Direction.DOWN
            self._pc.setcollaabb(self._vaabb)
          elif self._pc.direction == Direction.LEFT:
            dx -= self._pc.speed
          elif self._pc.direction == Direction.RIGHT:
            dx += self._pc.speed
        if keys[pygame.K_UP]:
          if self._pc.x % 8 == 0:
            dy -= self._pc.speed
            self._pc.direction = Direction.UP
            self._pc.setcollaabb(self._vaabb)
          elif self._pc.direction == Direction.LEFT:
            dx -= self._pc.speed
          elif self._pc.direction == Direction.RIGHT:
            dx += self._pc.speed
      else:
        if keys[pygame.K_LEFT]:
          if self._pc.y % 8 == 0:
            dx -= self._pc.speed
            self._pc.direction = Direction.LEFT
            self._pc.setcollaabb(self._haabb)
          elif self._pc.direction == Direction.UP:
            dy -= self._pc.speed
          elif self._pc.direction == Direction.DOWN:
            dy += self._pc.speed
        if keys[pygame.K_RIGHT]:
          if self._pc.y % 8 == 0:
            dx += self._pc.speed
            self._pc.direction = Direction.RIGHT
            self._pc.setcollaabb(self._haabb)
          elif self._pc.direction == Direction.UP:
            dy -= self._pc.speed
          elif self._pc.direction == Direction.DOWN:
            dy += self._pc.speed
      self._pc.dx = dx
      self._pc.dy = dy
      
      if keys[pygame.K_x]:
        if self._pc.canAttack and self._inventory.sword > 0:
          self._pc.doAttack(8)
          self._pc.loseControl(8)
          self._pc.stop()
      else:
        self._pc.releaseAttack()
      
    for monster in self._monsters:
      monster.incframe()
      if monster.isControllable:
        if monster.ai == 'random':
          if random.randint(1,20) == 20:
            dx = 0
            dy = 0
            if (monster.dx != 0 and monster.x % 8 == 0) or (monster.dy != 0 and monster.y % 8 == 0) or (monster.dx == 0 and monster.dy == 0):
              d = (None, Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT)[random.randint(0,4)]
              if d is not None:
                monster.direction = d
                if d == Direction.UP:
                  dy -= monster.speed
                if d == Direction.DOWN:
                  dy += monster.speed
                if d == Direction.LEFT:
                  dx -= monster.speed
                if d == Direction.RIGHT:
                  dx += monster.speed
            monster.dx = dx
            monster.dy = dy
          
  def _physics(self):
    if not self._porting:
      for actor in self._bounders:
        d = None
        if actor.collaabb.colliderect(self._UBOUND):
          d = Direction.UP
          actor.y = self._UBOUND.y+self._UBOUND.h-actor.collyoffset
        if actor.collaabb.colliderect(self._RBOUND):
          d = Direction.RIGHT
          actor.x = self._RBOUND.x-actor.collaabb.w-actor.collxoffset
        if actor.collaabb.colliderect(self._BBOUND):
          d = Direction.DOWN
          actor.y = self._BBOUND.y-actor.collaabb.h-actor.collyoffset
        if actor.collaabb.colliderect(self._LBOUND):
          d = Direction.LEFT
          actor.x = self._LBOUND.x+self._LBOUND.w-actor.collxoffset
        if d is not None and self._portals[d] is not None and actor is self._pc:
          if self._portals[d].type == PortalType.CaveExit:
            self._spelunking = 1
            self._cavetimer = 47
            self._pc.loseControl(47)
            self._port(self._portals[d])
          elif self._portals[d] is not None:
            self._zone(d)
        else:
          colls = []
          actor.x += actor.dx
          for tile in self._tiles:
            for wall in tile.aabbs:
              if actor.collaabb.colliderect(wall):
                colls.append(tile)
                if actor.dx < 0:
                  actor.x = wall.x+wall.w-actor.collxoffset
                else:
                  actor.x = wall.x-actor.collaabb.w-actor.collxoffset
          actor.y += actor.dy
          for tile in self._tiles:
            for wall in tile.aabbs:
              if actor.collaabb.colliderect(wall):
                colls.append(tile)
                if actor.dy < 0:
                  actor.y = wall.y+wall.h-actor.collyoffset
                else:
                  actor.y = wall.y-actor.collaabb.h-actor.collyoffset
                if actor is self._pc and tile.isPortal:
                  if tile.portal.type == PortalType.CaveEntrance:
                    self._spelunking = -1
                    self._currentport = tile.portal
                    self._cavetimer = 47
                    self._pc.loseControl(47)
          for tile in colls:
            for wall in tile.aabbs:
              if actor is self._pc and tile.action is not None:
                exec tile.action
      if not self._porting:          
        for monster in self._monsters:
          for weapon in self._pcweapons:
            if monster.hitaabb.colliderect(weapon.hitaabb) and not monster.isInvincible:
              monster.hurt(weapon.attack)
              monster.becomeInvincible(30)
              monster.loseControl(8)
              monster.stop()
              speed = self._pc.speed*2
              if self._pc.direction == Direction.UP:
                monster.dy = -speed
              if self._pc.direction == Direction.DOWN:
                monster.dy = speed
              if self._pc.direction == Direction.LEFT:
                monster.dx = -speed
              if self._pc.direction == Direction.RIGHT:
                monster.dx = speed
              
          if self._pc.hitaabb.colliderect(monster.hitaabb) and not self._pc.isInvincible:
            self._pc.hurt(monster.attack)
            self._pc.becomeInvincible(30)
            self._pc.loseControl(8)
            self._pc.stop()
            if not self._pc.isAttacking:
              speed = self._pc.speed*2
              if monster.direction == Direction.UP:
                self._pc.dy = -speed
              if monster.direction == Direction.DOWN:
                self._pc.dy = speed
              if monster.direction == Direction.LEFT:
                self._pc.dx = -speed
              if monster.direction == Direction.RIGHT:
                self._pc.dx = speed
        removes = []
        for collectible in self._collectibles:
          for actor in [actor for actor in [self._pc]+self._pcweapons]:
            if collectible.aabb.colliderect(actor.collaabb):
              exec collectible.action
              removes.append(collectible)
              if collectible.triumph:
                self._pc.x = collectible.x-(collectible.x%8)
                self._pc.y = collectible.y+(-collectible.y%8)
                self._pc.triumph(48)
                self._temps.append([Tile.Tile(self._pc.x,self._pc.y-16,collectible.sprite),48])
          self._collectibles = [c for c in self._collectibles if c not in removes]
    elif self._zoning is not None:
      self._pc.incframe()
      if self._zoning == Direction.UP:
        self._pc.y += 4
        if self._pc.collaabb.colliderect(self._BBOUND):
          self._pc.y = self._BBOUND.y-self._pc.collaabb.h-self._pc.collyoffset
      if self._zoning == Direction.RIGHT:
        self._pc.x -= 4
        if self._pc.collaabb.colliderect(self._LBOUND):
          self._pc.x = self._LBOUND.x+self._LBOUND.w-self._pc.collxoffset
      if self._zoning == Direction.DOWN:
        self._pc.y -= 4
        if self._pc.collaabb.colliderect(self._UBOUND):
          self._pc.y = self._UBOUND.y+self._UBOUND.h-self._pc.collyoffset
      if self._zoning == Direction.LEFT:
        self._pc.x += 4
        if self._pc.collaabb.colliderect(self._RBOUND):
          self._pc.x = self._RBOUND.x-self._pc.collaabb.w-self._pc.collxoffset

  def _zone(self, direction):
    if self._portals[direction] is None:
      return
    self._zoning = direction
    self._oldmap = self._currentmap
    self._loadmap(mapres(self._portals[direction].destfile))
    if direction == Direction.UP or direction == Direction.DOWN:
      n = 44
    else:
      n = 64
    self._pc.loseControl(n)
    self._zonetimer = n
      
  def _port(self, portal):
    self._currentport = None
    self._loadmap(mapres(portal.destfile))
    if portal.destx != -1:
      self._pc.x = portal.destx
    if portal.desty != -1:
      self._pc.y = portal.desty  
    
class Game(object):
  def __init__(self):
    self._FPS=40
    self._TICK=1000/self._FPS
    self._play = Play()
    self._quit = False
    
    
  def main(self):
    nexttick = millis()+self._TICK
    while not self._quit:
      t = millis()
      if t >= nexttick:
        for event in pygame.event.get():
          if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self._quit = True
            return
        self._play._update()
        self._play._render()
        nexttick = t+self._TICK
  
def millis():  
  return int(round(time.time()*1000))
  
if __name__ == '__main__':
  Game().main()
