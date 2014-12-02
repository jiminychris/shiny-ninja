import pygame
from Networking import Client, Messages

_MAX_SPEED = 128

class Sprite(object):
    def __init__(self, uri, x=0, y=0):
        self._uri = uri
        self._x = x
        self._y = y
        self._dx = 0
        self._dy = 0
        self._max_speed = _MAX_SPEED
        self._img = pygame.image.load(uri)

    ###
    # Properties
    ###

    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y

    @property
    def dx(self):
        return self._dx
    @dx.setter
    def dx(self, value):
        if value == self._dx:
            return

        self._dx = value
        Client.send(Messages.NinjaMove(Messages.Orientation.Horizontal, value))

    @property
    def dy(self):
        return self._dy
    @dy.setter
    def dy(self, value):
        if value == self._dy:
            return

        self._dy = value
        Client.send(Messages.NinjaMove(Messages.Orientation.Vertical, value))

    @property
    def max_speed(self):
        return self._max_speed
    @max_speed.setter
    def max_speed(self, value):
        self._max_speed = value
    
    @property
    def img(self):
        return self._img

    ###
    # Methods
    ###

    def update(self, frame_time):
        self._x += self._dx * frame_time
        self._y += self._dy * frame_time

    def recv(self, message):
        if isinstance(message, Messages.NinjaMove):
            if message.orientation == Messages.Orientation.Horizontal:
                self.dx = message.magnitude
            else:
                self.dy = message.magnitude