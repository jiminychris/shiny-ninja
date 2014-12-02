import sys
import os
import pygame
import random
import math

from Networking import Client
from Game import Graphics

size = sizew, sizeh = 704, 528
tile_size = 88
grid_size = gridw, gridh = sizew/tile_size, sizeh/tile_size
fps = 30.0
frame_time = 1.0/fps

class Main:
    def __init__(self):
        self._screen = None
        self._renderables = []
        self._ninjas = []
        self._avatar = None
        self._quit = False

        self._keys = {}

    def main(self):
        random.seed()
        if len(sys.argv) != 3:
            print("Expected name of matchmaking server and number of players")
            sys.exit(1)

        server_name, n = sys.argv[1:]
        n = int(n)

        Client.find_peers(server_name, n)
        spotlight_positions = Client.get_spotlights()
        for i in range(len(spotlight_positions)):
            x, y = spotlight_positions[i]
            spotlight_positions[i] = math.floor(x*gridw), math.floor(y*gridh)

        pygame.init()
        self._screen = pygame.display.set_mode(size)

        self._avatar = Graphics.Sprite(os.path.join("resources", "images", "ninja.png"))

        enemies = [Graphics.Sprite(os.path.join("resources", "images", "enemy.png")) for x in range(n-1)]

        spotlights = [Graphics.Sprite(os.path.join("resources", "images", "spotlight.png"), sp[0], sp[1])
                        for sp in spotlight_positions]

        self._ninjas = enemies + [self._avatar]

        Client.register_avatars(enemies)

        self._avatar.set_position(random.randint(0, gridw), random.randint(0, gridh))

        self._renderables.extend(spotlights)
        self._renderables.extend(self._ninjas)

        self.loop()

    def input(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self._quit = True
                #alert network of quitting
            elif e.type == pygame.KEYDOWN and e.key not in self._keys:
                self._keys[e.key] = 1
                if e.key == pygame.K_LEFT:
                    self._avatar.dx = -self._avatar.max_speed
                elif e.key == pygame.K_RIGHT:
                    self._avatar.dx = self._avatar.max_speed
                elif e.key == pygame.K_UP:
                    self._avatar.dy = -self._avatar.max_speed
                elif e.key == pygame.K_DOWN:
                    self._avatar.dy = self._avatar.max_speed
            elif e.type == pygame.KEYUP and e.key in self._keys:
                del self._keys[e.key]

    def update(self):
        for ninja in self._ninjas:
            ninja.update(frame_time)

    def render(self):
        self._screen.fill((0,0,0))
        for r in self._renderables:
            self._screen.blit(r.img, (tile_size*r.x-r.half_width, tile_size*r.y-r.half_height))
        pygame.display.flip()

    def loop(self):
        next_frame = pygame.time.get_ticks()
        while not self._quit:
            current_time = pygame.time.get_ticks()
            if (current_time >= next_frame):
                next_frame += frame_time * 1000
                Client.recv()
                self.input()
                self.update()
                self.render()

if __name__ == '__main__':
    Main().main()
