from Utils import enum

PortalType = enum('Boundary', 'Magic', 'CaveEntrance', 'CaveExit', 'StairsEntrance', 'StairsExit')

class Portal(object):
  def __init__(self, destfile, destx, desty, type):
    self._destfile = destfile
    self._destx = destx
    self._desty = desty
    self._type = type
    
  @property
  def destfile(self):
    return self._destfile
  @property
  def destx(self):
    return self._destx
  @property
  def desty(self):
    return self._desty
  @property
  def type(self):
    return self._type