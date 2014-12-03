import pygame
from Networking import Client, Messages
import Util

class Sprite(object):
    def __init__(self, uri, x=0, y=0):
        self._uri = uri
        self._x = x
        self._y = y
        self._img = pygame.image.load(uri)
        self._width = self._img.get_width()
        self._height = self._img.get_height()

        self._half_width = self._width/2
        self._half_height = self._height/2

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
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def half_width(self):
        return self._half_width

    @property
    def half_height(self):
        return self._half_height

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
    def img(self):
        return self._img

    ###
    # Properties
    ###

    def update(self, frame_time):
        pass

class Ninja(Sprite):
    _MAX_SPEED = 1

    def __init__(self, uri):
        self._uri = uri
        self._x = 0
        self._y = 0
        self._dx = 0
        self._dy = 0
        self._max_speed = Ninja._MAX_SPEED
        self._img = pygame.image.load(uri)
        self._width = self._img.get_width()
        self._height = self._img.get_height()
        self._dies = Util.Event()

        self._half_width = self._width/2
        self._half_height = self._height/2

    ###
    # Properties
    ###

    @property
    def dies(self):
        return self._dies
    
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

    ###
    # Methods
    ###

    def swing_sword(self):
        Client.send(Messages.SwordSwing(self._x, self._y))

    def set_position(self, x, y):
        self._x = x
        self._y = y
        Client.send(Messages.NinjaPosition(x, y))

    def update(self, frame_time):
        self._x += self._dx
        self._y += self._dy
        self._dx = 0
        self._dy = 0

    def recv(self, message):
        if isinstance(message, Messages.NinjaMove):
            if message.orientation == Messages.Orientation.Horizontal:
                self._dx = message.magnitude
            else:
                self._dy = message.magnitude
        elif isinstance(message, Messages.NinjaPosition):
            self._x = message.x
            self._y = message.y
        elif isinstance(message, Messages.SwordSwing):
            if self._x == message.x and self._y == message.y:
                self._dies.fire({"sender": self})
                Client.send(Messages.NinjaDeath())
        elif isinstance(message, Messages.NinjaDeath):
            self._dies.fire({"sender": self})
