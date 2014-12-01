import pygame

__MAX_SPEED = 5

class Sprite:
    def __init__(self, uri, x=0, y=0):
        self._uri = uri
        self._x = x
        self._y = y
        self._dx = 0
        self._dy = 0
        self._max_speed = __MAX_SPEED
        self._img = pygame.image.load(uri)

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

    def update():
        self._x += self._dx
        self._y += self._dy
