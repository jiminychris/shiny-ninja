import pygame
from Spritesheet import Spritesheet
from Utils import *

WHITE = (255,255,255)
BLACK = (0,0,0)
TEXT = None

def get(txt, color=None):
  if TEXT is None:
    initialize()
  return [s if color is None else colorReplace(s, ((WHITE, color),)) for s in [TEXT[t] for t in txt]]
  
def initialize():
  rows = ('ABCDEFGHIJKLM',
          'NOPQRSTUVWXYZ',
          '0123456789',
          '-.,!\'& ')
  ss = Spritesheet(bmpres('text.bmp'))
  global TEXT
  TEXT = {}
  for j in range(len(rows)):
    row = rows[j]
    for i in range(len(row)):
      l = row[i]
      TEXT[l] = ss.image_at((i*8,j*8,8,8), colorkey=BLACK)