class Inventory(object):
  def __init__(self):
    self._rupees = 0
    self._bombs = 0
    self._keys = 0
    self._sword = 0
    
  @property
  def rupees(self):
    return self._rupees
  @property
  def bombs(self):
    return self._bombs
  @property
  def keys(self):
    if self._keys != 'A':
      return self._keys
    else:
      return 8
  @property
  def keystr(self):
    return str(self._keys)
  @property
  def sword(self):
    return self._sword
    
  def addrupees(self, value):
    if value < 0:
      raise ValueError("Expected positive number")
    self._rupees = min(255, self._rupees + value)
  def removerupees(self, value):
    if value < 0:
      raise ValueError("Expected positive number")
    self._rupees = max(0, self._rupees - value)
  def addbombs(self, value):
    if value < 0:
      raise ValueError("Expected positive number")
    self._bombs = min(8, self._bombs + value)
  def removebombs(self, value):
    if value < 0:
      raise ValueError("Expected positive number")
    self._bombs = max(0, self._bombs - value)
  def addkey(self):
    if self._keys != 'A':
      self._keys = min(8, self._keys + 1)
  def removekey(self):
    if self._keys != 'A':
      self._keys = max(0, self._keys - 1)
  def acquiremkey(self):
    self._keys = 'A'
  def changesword(self, value):
    if value not in (0,1,2,4):
      raise ValueError("Expected 0, 1, 2, or 4")
    self._sword = value