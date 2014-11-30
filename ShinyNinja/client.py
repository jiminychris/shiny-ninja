import sys
import os
import pygame

from Networking import Client
from Game import Graphics

size = 640, 480

class Main:
    def __init__(self):
        self._screen = None
        self._renderables = []
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

        ninjas = [Graphics.Sprite(os.path.join("resources", "images", "idle.png")) for x in range(n)]

        Client.register_avatars(ninjas[1:])

        self._renderables.extend(ninjas)

        self.loop()

    def update(self):
        pass

    def render(self):
        self._screen.fill((0,0,0))
        for r in self._renderables:
            self._screen.blit(r.img, (r.x, r.y))
        pygame.display.flip()

    def loop(self):
        while not self._quit:
            self.update()
            self.render()

if __name__ == '__main__':
    Main().main()
