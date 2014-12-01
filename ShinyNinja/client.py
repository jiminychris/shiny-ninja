import sys
import os
import pygame

from Networking import Client
from Game import Graphics

size = 640, 480
fps = 30.0
frame_time = 1.0/fps

class Main:
    def __init__(self):
        self._screen = None
        self._renderables = []
        self._ninjas = []
        self._avatar = None
        self._quit = False

    def main(self):
        if len(sys.argv) != 3:
            print("Expected name of matchmaking server and number of players")
            sys.exit(1)

        server_name, n = sys.argv[1:]
        n = int(n)

        Client.find_peers(server_name, n)

        pygame.init()
        self._screen = pygame.display.set_mode(size)

        self._ninjas = [Graphics.Sprite(os.path.join("resources", "images", "idle.png")) for x in range(n)]

        self._avatar = self._ninjas[0]
        Client.register_avatars(self._ninjas[1:])

        self._renderables.extend(self._ninjas)

        self.loop()

    def input(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self._quit = True
                #alert network of quitting
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    self._avatar.dx = -self._avatar.max_speed
                elif e.key == pygame.K_RIGHT:
                    self._avatar.dx = self._avatar.max_speed
                elif e.key == pygame.K_UP:
                    self._avatar.dy = -self._avatar.max_speed
                elif e.key == pygame.K_DOWN:
                    self._avatar.dy = self._avatar.max_speed
            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_LEFT:
                    self._avatar.dx = 0
                elif e.key == pygame.K_RIGHT:
                    self._avatar.dx = 0
                elif e.key == pygame.K_UP:
                    self._avatar.dy = 0
                elif e.key == pygame.K_DOWN:
                    self._avatar.dy = 0

    def update(self):
        for ninja in self._ninjas:
            ninja.update(frame_time)

    def render(self):
        self._screen.fill((0,0,0))
        for r in self._renderables:
            #print(r.x, r.y, r.dx, r.dy)
            self._screen.blit(r.img, (r.x, r.y))
        pygame.display.flip()

    def loop(self):
        next_frame = pygame.time.get_ticks()
        while not self._quit:
            current_time = pygame.time.get_ticks()
            if (current_time >= next_frame):
                next_frame += frame_time * 1000
                self.input()
                self.update()
                self.render()

if __name__ == '__main__':
    Main().main()
