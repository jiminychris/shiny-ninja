import Renderable2d
import pygame

_SIZE = _WIDTH, _HEIGHT = 320, 240

class Renderer2d:
    def __init__(self):
        self._window = None

    def OpenWindow(self):
        self._window = pygame.display.set_mode(_SIZE)

    def CloseWindow(self):
        pass

    def Render(self):
        pass
