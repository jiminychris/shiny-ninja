import xml.etree.ElementTree as et
import Tile
from Portal import Portal, PortalType
from Collectible import Collectible
import Text
from pygame.rect import Rect
from Actor import Actor
from Map import Map
from Spritesheet import Spritesheet
from Decoration import Decoration
import random
from Utils import *

class Parser(object):
  _DEFAULTCOLORS = ((0,0,0),(128,128,128),(192,192,192),(255,255,255))
  _DIRECTIONS = (Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT)
  
  def __init__(self, fname):
    random.seed()
    self._root = root = _safeopen(fname).getroot()
    
    self._tn = tn = root.find('tiles')
    tileroot = _safeopen(defres(tn.get('file', 'tiles.til'))).getroot()
    tss = Spritesheet(bmpres(tileroot.get('file', None)))
    self._tiledefs = {d.get('type', 'blank'): _parsesprite(d.find('sprite'), tss) for d in tileroot.findall('def')}
    
    self._aabbdefs = {d.get('type', 'blank'): _parserects(d) for d in tileroot.findall('def')}    
    
    self._decodefs = {}
    self._dn = dn = root.find('decorations')
    if dn is not None:
      dss = Spritesheet(bmpres(dn.get('file', None)))
      self._decodefs = {d.get('type', 'blank'): 
                  ([colorReplace(s, zip(Parser._DEFAULTCOLORS, _parsecolors(d.find('palette')))) 
                    for s in _parsesprites(d, dss)], d.get('animtype', 'fliph'))
                  for d in dn.findall('def')}
                  
    self._pn = pn = tn.find('palettes')
    if pn is not None:
      self._palettedefs = {p.get('id', 'default'): _parsecolors(p) for p in pn.findall('palette')}
    else:
      pn = tn.find('palette')
      self._palettedefs = {'default': _parsecolors(pn)}

  def parse(self):
    return Map(self.parseTiles(),
               self.parseMonsters(),
               self.parseDecorations(),
               self.parsePortals(),
               self.parseText(),
               self.parseCollectibles())

  def parseTiles(self):
    tilelist = []
    rows = self._tn.findall('row')
    for j in range(len(rows)):
      tiles = rows[j].findall('tile')
      for i in range(len(tiles)):
        tilelist.append(self._parsetile(tiles[i], i, j))
    return tilelist
    
  def _parsetile(self, tile, i, j):
    t = tile.get('type', 'blank')
    p = _tryparseport(tile)
    alt = tile.find('alt')
    action = tile.find('action')
    tile = Tile.Tile(i*Tile.SIZE, j*Tile.SIZE, colorReplace(self._tiledefs[t], zip(Parser._DEFAULTCOLORS, self._palettedefs[tile.get('palette', 'default')])), self._aabbdefs[t], p, eval(tile.get('mask', 'False')))
    
    if alt is not None:    
      tile.addcond(alt.find('condition').text)
      tile.addalt(self._parsetile(alt.find('tile'), i, j))
    if action is not None:
      tile.addaction(action.text)
      
    return tile
    
  def parseMonsters(self):
    monsterlist = []

    monsters = self._root.find('monsters')
    if monsters is not None:
      monsterfile = defres(monsters.get('file', 'monsters.mon'))
      monroot = _safeopen(monsterfile).getroot()
      monsters = monsters.findall('monster')
    else:
      monsters = []
        
    for monster in monsters:
      id = monster.get('id', 'octorok')
      m = None
      m = monroot.find(id)
      if m is None:
        raise ValueError('could not find monster with id \''+id+'\' in '+str(monroot))

      
      hp = m.find('hp')
      if hp is None:
        hp = 8
      else:
        hp = int(hp.text)
        
      atk = m.find('attack')
      if atk is None:
        atk = 8
      else:
        atk = int(atk.text)
        
      pattern = None
      speed = 0
      aimov = m.find('ai')
      if aimov is not None:
        aimov = aimov.find('movement')
      if aimov is not None:
        speed = aimov.find('speed')
        pattern = aimov.find('pattern')
        
      if speed is not 0:
        options = speed.findall('option')
        if options is not None:
          speed = int(options[random.randint(0,len(options)-1)].text)
      if pattern is not None:
        pattern = pattern.text
      a = Actor(int(monster.get('x', '0')), int(monster.get('y', '0')), speed, hp, atk, pygame.Rect(0, 0, Tile.SIZE, Tile.SIZE), True, _sprites(m), None, pattern)
      aabbnode = m.find('aabb')
      caabbnode = m.find('collaabb')
      haabbnode = m.find('hitaabb')
      if aabbnode is not None:
        a.setaabb(_parserect(aabbnode.find('rect')))
      else:
        if caabbnode is not None:
          a.setcollaabb(_parserect(caabbnode.find('rect')))
        if haabbnode is not None:
          a.sethitaabb(_parserect(haabbnode.find('rect')))
      monsterlist.append(a)
        
    return monsterlist
  
  def parseDecorations(self):
    if self._dn is not None:
      return [Decoration(int(d.get('x', '0')), int(d.get('y', '0')), self._decodefs[d.get('type', 'blank')][0], self._decodefs[d.get('type', 'blank')][1]) for d in self._dn.findall('decoration')]
    else:
      return []
    
  def parsePortals(self):
    portals = {}
    
    portn = self._root.find('portals')
    ports = (_tryparseport(portn.find('up')), _tryparseport(portn.find('right')), _tryparseport(portn.find('down')), _tryparseport(portn.find('left')))
    portals = dict(zip(Parser._DIRECTIONS, ports))
    
    return portals
    
  def parseText(self):
    textlist = []
    textnode = self._root.find('text')
    if textnode is not None:
      cond = textnode.find('condition')
      if cond is None:
        cond = 'True'
      else:
        cond = cond.text
      textlist = [tile for line in textnode.findall('line') for tile in _parseline(line)]
      [tile.addcond(cond) for tile in textlist]
      
    return textlist
    
  def parseCollectibles(self):
    collist = []
    collectibles = self._root.find('collectibles')
    if collectibles is not None:
      colfile = defres(collectibles.get('file', 'collectibles.col'))
      colroot = _safeopen(colfile).getroot()
      collectibles = collectibles.findall('collectible')
    else:
      collectibles = []
      
    for collectible in collectibles:
      id = collectible.get('id', 'sword')
      c = None
      c = colroot.find(id)
      if c is None:
        raise ValueError('could not find collectible with id \''+id+'\' in '+str(colroot))
      triumph = eval(c.get('triumph', 'False'))
      action = c.find('action')
      action2 = collectible.find('action')
      cond = collectible.find('condition')
      aabb = _parserect(c.find('rect'))
      spriten = c.find('sprites')
      ck = _parsecolor(spriten.find('colorkey').find('color'))
      palette = _parsecolors(spriten.find('palette'))
      sfile = spriten.get('file','weapons.bmp')
      css = Spritesheet(bmpres(sfile))
      sprites = []
      for sp in spriten.findall('sprite'):
        pal = sp.find('palette')
        if pal is not None:
          pal = _parsecolors(pal)
        else:
          pal = palette
        repl = zip(Parser._DEFAULTCOLORS, pal)
        sprites.append(colorReplace(_parsesprite(sp, css, ck), repl))
      if action is None:
        action = ''
      else:
        action = action.text      
      if action2 is None:
        action2 = ''
      else:
        action2 = action2.text
      action = '\n'.join((action2, action))
      if cond is None:
        cond = 'True'
      else:
        cond = cond.text
      x,y = int(collectible.get('x','0')),int(collectible.get('y','0'))
      collist.append(Collectible(x,y,aabb,sprites,cond,action,triumph))
    return collist
  
def parseCollectible(fname, id):
  c = _safeopen(fname).getroot().find(id, 'heart')
  triumph = eval(c.get('triumph', 'False'))
  action = c.find('action')
  cond = "True"
  aabb = _parserect(c.find('rect'))
  spriten = c.find('sprites')
  ck = _parsecolor(spriten.find('colorkey').find('color'))
  palette = _parsecolors(spriten.find('palette'))
  sfile = spriten.get('file','weapons.bmp')
  css = Spritesheet(bmpres(sfile))
  sprites = []
  for sp in spriten.findall('sprite'):
    pal = sp.find('palette')
    if pal is not None:
      pal = _parsecolors(pal)
    else:
      pal = palette
    repl = zip(Parser._DEFAULTCOLORS, pal)
    sprites.append(colorReplace(_parsesprite(sp, css, ck), repl))
  if action is None:
    action = ''
  else:
    action = action.text
  x,y = 0,0
  return Collectible(x,y,aabb,sprites,cond,action,triumph)
    
def _sprites(node):
  s = node.find('sprites')
  sheet = s.get('sheet', None)
  
  if sheet is None:
    raise ValueError('Expected a spritesheet')
    
  ss = Spritesheet(bmpres(sheet))
    
  udlr = ((Direction.UP, s.find('up')), 
         (Direction.DOWN, s.find('down')), 
         (Direction.LEFT, s.find('left')), 
         (Direction.RIGHT, s.find('right')))
         
  repl = zip(Parser._DEFAULTCOLORS, _parsecolors(s.find('palette')))
  if udlr[0][1] is None:
    raise ValueError('Cannot do sprite without an UP direction')
    
  sd = {}
  for d in udlr:
    dir = d[0]
    xml = d[1]
    if xml is not None:
      imgs = _parsesprites(xml, ss)
      sd[dir] = imgs if repl is None else [colorReplace(img, repl) for img in imgs]
      
  return sd
    
def _parsecolor(node):
  return (int(node.get('r', '0')), int(node.get('g', '0')), int(node.get('b', '0')))
def _parsecolors(node):
  return [_parsecolor(c) for c in node.findall('color')]
def _parsesprite(node, ss, ck=None):
  sp = ss.image_at([int(a) for a in (node.get('x','0'), node.get('y', '0'), node.get('w', '16'), node.get('h', '16'))], ck)
  trans = node.get('transform', 'default')
  if trans == 'fliph':
    sp = pygame.transform.flip(sp, True, False)
  elif trans == 'flipv':
    sp = pygame.transform.flip(sp, False, True)
  elif trans == 'flip':
    sp = pygame.transform.flip(sp, True, True)
  return sp
def _parsesprites(node, ss):
  return [_parsesprite(s, ss, _tryparsecolorkey(node)) for s in node.findall('sprite')]
def _parserect(node):
  return pygame.Rect([int(a) for a in (node.get('x','0'), node.get('y', '0'), node.get('w', '16'), node.get('h', '16'))])
def _parserects(node):
  return [_parserect(r) for r in node.findall('rect')]
def _tryparseport(node):
  if node is None:
    return node
  port = node.find('portal')
  if port is not None:
    port = Portal(port.get('file', 'swordcave.map'), int(port.get('x', '0')), int(port.get('y', '0')), PortalType.__dict__[port.get('type', 'Boundary')])
  return port
def _tryparsecolorkey(node):
  if node is None:
    return None
  ck = node.find('colorkey')
  if ck is None:
    return None
  return _parsecolor(ck.find('color'))
def _parseline(node):
  x = int(node.get('x', '0'))
  y = int(node.get('y', '0'))
  txt = Text.get(node.get('value', ''))
  tiles = []
  for i in range(len(txt)):
    tiles.append(Tile.Tile((x+i*8), y, txt[i]))
  return tiles
  
def _safeopen(fname):
  if not isinstance(fname, str):
    raise TypeError("Expected filename of type str")
  tree = None
  try:
    tree = et.parse(fname)
  except IOError as e:
    raise e
    
  return tree
        
    
