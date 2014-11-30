import pygame

class Sprite:
    def __init__(self, uri, x=0, y=0):
        self.uri = uri
        self.x = x
        self.y = y
        self.img = pygame.image.load(uri)

